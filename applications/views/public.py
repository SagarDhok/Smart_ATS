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

logger = logging.getLogger(__name__)


def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug,is_deleted=False)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # DUPLICATE CHECK
            if Application.objects.filter(job=job, email=email).exists():
                form.add_error("email", "You have already applied for this job.")
                return render(request, "applications/apply.html", {"form": form, "job": job})

            application = form.save(commit=False)
            application.job = job

            resume_file = request.FILES.get("resume")
            if not resume_file:
                form.add_error("resume", "Resume is required.")
                return render(request, "applications/apply.html", {"form": form, "job": job})

            # PARSING RESUME 
            try:
                resume_file.seek(0)
                parsed = parse_resume(resume_file, job)

            except ValueError as e:
                form.add_error("resume", str(e))
                return render(request, "applications/apply.html", {"form": form, "job": job})

            except Exception as e:
                logger.exception("Unexpected parsing error")
                form.add_error("resume", "Resume processing failed. Please try again.")
                return render(request, "applications/apply.html", {"form": form, "job": job})

            # SCORING
            scoring = compute_match_score(parsed, job)

            application.match_score = scoring["final_score"]
            application.skill_score = scoring["skill_score"]
            application.experience_score = scoring["experience_score"]
            application.keyword_score = scoring["keyword_score"]
            application.matched_skills = scoring["matched_skills"]
            application.missing_skills = scoring["missing_skills"]

            application.summary = generate_summary(parsed, scoring["final_score"])
            application.evaluation = evaluate_candidate(scoring["final_score"])
            application.fit_category = fit_category(scoring["final_score"])

            application.parsed_name = parsed.get("name")
            application.parsed_email = parsed.get("email")
            application.parsed_phone = parsed.get("phone")
            application.parsed_experience = parsed.get("experience_years")
            application.parsed_skills = parsed.get("skills")
            application.parsed_projects = parsed.get("projects")
            application.parsed_education = parsed.get("education")
            application.parsed_certifications = parsed.get("certifications")

            # SUPABASE UPLOAD (seek(0) is handled inside upload_resume too)
            try:
                application.resume_url = upload_resume(resume_file, job.slug)
            except Exception as e:
                logger.exception(e)
                form.add_error("resume", f"Upload failed: {str(e)}")
                return render(request, "applications/apply.html", {"form": form, "job": job})

            # FINAL SAVE
            try:
                application.save()
            except Exception as e:
                logger.exception(e)
                form.add_error(None, f"Persistence error: {str(e)}")
                return render(request, "applications/apply.html", {"form": form, "job": job})

            return redirect("application_success")

    else:
        form = ApplicationForm()

    return render(request, "applications/apply.html", {"form": form, "job": job})
