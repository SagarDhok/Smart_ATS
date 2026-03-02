from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count
from jobs.models import Job
from jobs.forms import JobForm
from django.views.decorators.http import require_POST

import logging

logger = logging.getLogger(__name__)


# ============================
# QUERYSET HELPER
# ============================
def job_queryset_for(user):
    if user.role == "ADMIN":
        return Job.objects.filter(is_deleted=False)
    return Job.objects.filter(created_by=user, is_deleted=False)


# =================================================================
#                       RECRUITER JOB LIST
# =================================================================
@login_required
def recruiter_job_list(request):
    if request.user.role not in ["RECRUITER", "ADMIN"]:
        logger.warning(f"Unauthorized job list access attempt by {request.user.email}")
        raise PermissionDenied()

    qs = job_queryset_for(request.user).annotate(
        application_count=Count('applications')
    ).order_by("-created_at")

    search = request.GET.get("search")
    location = request.GET.get("location")
    work_mode = request.GET.get("work_mode")

    if search:
        qs = qs.filter(title__icontains=search)
    if location:
        qs = qs.filter(location__icontains=location)
    if work_mode:
        qs = qs.filter(work_mode=work_mode)

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "recruiter/jobs/list.html", {
        "jobs": page,
        "page_obj": page,
    })


# =================================================================
#                       RECRUITER JOB CREATE
# =================================================================
@login_required
def recruiter_job_create(request):
    if request.user.role != "RECRUITER":
        logger.warning(f"Unauthorized job creation attempt by {request.user.email}")
        return HttpResponseForbidden()

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()

            logger.info(f"Job created: id={job.id} by {request.user.email}")
            messages.success(request, "Job created successfully!")
            return redirect("recruiter_job_list")
    else:
        form = JobForm()

    return render(request, "recruiter/jobs/create.html", {"form": form})


# =================================================================
#                       RECRUITER JOB DETAIL
# =================================================================
@login_required
def recruiter_job_detail(request, id):
    if request.user.role not in ["RECRUITER", "ADMIN"]:
        logger.warning(f"Unauthorized job detail access attempt by {request.user.email}")
        raise PermissionDenied()

    job = get_object_or_404(job_queryset_for(request.user), id=id)
    return render(request, "recruiter/jobs/detail.html", {"job": job})


# =================================================================
#                       RECRUITER JOB UPDATE
# =================================================================
@login_required
def recruiter_job_edit(request, id):
    if request.user.role != "RECRUITER":
        return HttpResponseForbidden("Admins cannot edit recruiter-created jobs.")

    job = get_object_or_404(job_queryset_for(request.user), id=id)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()

            messages.success(request, "Job updated successfully!")

            action = request.POST.get("action")

            if action == "save_list":
                return redirect("recruiter_job_list")

            if action == "save_detail":
                return redirect("recruiter_job_detail", id=job.id)

            return redirect("recruiter_job_list")
    else:
        form = JobForm(instance=job)

    return render(request, "recruiter/jobs/edit.html", {"form": form, "job": job})


# =================================================================
#                       RECRUITER JOB DELETE
# =================================================================
@login_required
@require_POST
def recruiter_job_delete(request, id):
    queryset = job_queryset_for(request.user)
    job = get_object_or_404(queryset, id=id)

    job.is_deleted = True
    job.save()

    messages.success(request, "Job deleted successfully!")
    return redirect("recruiter_job_list")