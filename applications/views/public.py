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

def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():

            # ==================================================================
            # 🔥 FIX #1 — Duplicate Application Prevention
            # ==================================================================
            email = form.cleaned_data.get("email")

            if Application.objects.filter(job=job, email=email).exists():
                form.add_error('email', 'You have already applied for this job.')
                return render(request, "applications/apply.html", {
                    "form": form,
                    "job": job
                })

            # ==================================================================
            # If unique → save
            # ==================================================================
            app = form.save(commit=False)
            app.job = job
            app.save()

            # ---- PARSE RESUME ----
            parsed = parse_resume(app.resume.path, job)

            # ---- SCORE ----
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

            # PARSED RAW FIELDS
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
