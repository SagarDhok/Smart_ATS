from django.shortcuts import render, redirect, get_object_or_404
from applications.forms import ApplicationForm
from jobs.models import Job
from applications.models import Application
from applications.parsing import parse_resume
from applications.utils import (
    compute_match_score,
    generate_summary,
    evaluate_candidate,
    fit_category,
)
from applications.supabase_client import upload_resume
import logging
import os
import tempfile

logger = logging.getLogger(__name__)


def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # DUPLICATE CHECK
            if Application.objects.filter(job=job, email=email).exists():
                form.add_error("email", "You have already applied for this job.")
                return render(request, "applications/apply.html", {"form": form, "job": job})

            app = form.save(commit=False)
            app.job = job

            resume_file = request.FILES.get("resume")
            if not resume_file:
                form.add_error("resume", "Resume is required.")
                return render(request, "applications/apply.html", {"form": form, "job": job})

            # TEMP FILE FOR PARSING
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in resume_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            try:
                parsed = parse_resume(tmp_path, job)
            except Exception as e:
                logger.warning(f"Resume parsing failed: {e}")
                parsed = {}
            finally:
                os.remove(tmp_path)

            # SCORING
            scoring = compute_match_score(parsed, job)

            app.match_score = scoring["final_score"]
            app.skill_score = scoring["skill_score"]
            app.experience_score = scoring["experience_score"]
            app.keyword_score = scoring["keyword_score"]
            app.matched_skills = scoring["matched_skills"]
            app.missing_skills = scoring["missing_skills"]

            app.summary = generate_summary(parsed, scoring["final_score"])
            app.evaluation = evaluate_candidate(scoring["final_score"])
            app.fit_category = fit_category(scoring["final_score"])

            app.parsed_name = parsed.get("name")
            app.parsed_email = parsed.get("email")
            app.parsed_phone = parsed.get("phone")
            app.parsed_experience = parsed.get("experience_years")
            app.parsed_skills = parsed.get("skills")
            app.parsed_projects = parsed.get("projects")
            app.parsed_education = parsed.get("education")
            app.parsed_certifications = parsed.get("certifications")



            # SUPABASE UPLOAD
            try:
                resume_file.seek(0)
                app.resume_url = upload_resume(resume_file, job.slug)
            except Exception as e:
                logger.exception(e)
                form.add_error("resume", str(e))

                return render(request, "applications/apply.html", {"form": form, "job": job})

            # FINAL SAVE
            print("FILES:", request.FILES)
            print("FILE OBJ:", resume_file, type(resume_file))

            try:
                app.save()
            except Exception as e:
                logger.exception(e)
                form.add_error(None, str(e))

                return render(request, "applications/apply.html", {"form": form, "job": job})

            return redirect("application_success")

    else:
        form = ApplicationForm()

    return render(request, "applications/apply.html", {"form": form, "job": job})
