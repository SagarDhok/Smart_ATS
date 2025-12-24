from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
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
import os
import tempfile

logger = logging.getLogger(__name__)

def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # ✅ DUPLICATE CHECK (BEFORE SAVE)
            if Application.objects.filter(job=job, email=email).exists():
                form.add_error("email", "You have already applied for this job.")
                return render(request, "applications/apply.html", {
                    "form": form,
                    "job": job
                })

            try:
                with transaction.atomic():

                    # ❌ DO NOT SAVE YET
                    app = form.save(commit=False)
                    app.job = job

                    # -------- SAFE RESUME PARSING --------
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        for chunk in request.FILES["resume"].chunks():
                            tmp.write(chunk)
                        tmp_path = tmp.name

                    parsed = parse_resume(tmp_path, job)

                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

                    # -------- SCORING --------
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

                    # Parsed fields
                    app.parsed_name = parsed.get("name")
                    app.parsed_email = parsed.get("email")
                    app.parsed_phone = parsed.get("phone")
                    app.parsed_experience = parsed.get("experience_years")
                    app.parsed_skills = parsed.get("skills")
                    app.parsed_projects = parsed.get("projects")
                    app.parsed_education = parsed.get("education")
                    app.parsed_certifications = parsed.get("certifications")

                    # ✅ SAVE ONLY WHEN EVERYTHING SUCCEEDS
                    app.save()

                return redirect("application_success")

            except Exception as e:
                logger.exception("Application submission failed")
                form.add_error(None, "Something went wrong. Please try again.")
                return render(request, "applications/apply.html", {
                    "form": form,
                    "job": job
                })

    else:
        form = ApplicationForm()

    return render(request, "applications/apply.html", {
        "form": form,
        "job": job
    })
