from django.shortcuts import render, redirect, get_object_or_404
from applications.forms import ApplicationForm
from jobs.models import Job
from applications.parsing import parse_resume
from applications.models import Application
from applications.utils import (
    compute_match_score,
    generate_summary,
    evaluate_candidate,
    fit_category
)
import logging

logger = logging.getLogger(__name__)


def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():

            # -----------------------------
            # DUPLICATE APPLICATION CHECK
            # -----------------------------
            email = form.cleaned_data.get("email")

            if Application.objects.filter(job=job, email=email).exists():
                logger.info(f"Duplicate application attempt for job={job.id} | email={email}")
                form.add_error('email', 'You have already applied for this job.')
                return render(request, "applications/apply.html", {
                    "form": form,
                    "job": job
                })

            # -----------------------------
            # CREATE APPLICATION
            # -----------------------------
            app = form.save(commit=False)
            app.job = job
            app.save()

            # -----------------------------
            # PARSE RESUME  (CRITICAL)
            # -----------------------------
            try:
                parsed = parse_resume(app.resume.path, job)
            except Exception as e:
                logger.error(
                    f"Resume parsing failed for job={job.id} | email={app.email} | error={e}"
                )
                form.add_error(None, "Could not process your resume. Try another file.")
                app.delete()
                return render(request, "applications/apply.html", {
                    "form": form,
                    "job": job
                })

            # -----------------------------
            # SCORING
            # -----------------------------
            scoring = compute_match_score(parsed, job)

            app.match_score = scoring["final_score"]
            app.skill_score = scoring["skill_score"]
            app.experience_score = scoring["experience_score"]
            app.keyword_score = scoring["keyword_score"]

            app.matched_skills = ", ".join(scoring["matched_skills"])
            app.missing_skills = ", ".join(scoring["missing_skills"])

            app.summary = generate_summary(parsed, scoring["final_score"])
            app.evaluation = evaluate_candidate(scoring["final_score"])
            app.fit_category = fit_category(scoring["final_score"])

            # RAW PARSED FIELDS
            app.parsed_name = parsed.get("name")
            app.parsed_email = parsed.get("email")
            app.parsed_phone = parsed.get("phone")
            app.parsed_experience = parsed.get("experience_years")
            app.parsed_skills = parsed.get("skills")
            app.parsed_projects = parsed.get("projects")
            app.parsed_education = parsed.get("education")
            app.parsed_certifications = parsed.get("certifications")

            app.save()

            return redirect("application_success")

    else:
        form = ApplicationForm()

    return render(request, "applications/apply.html", {"form": form, "job": job})
