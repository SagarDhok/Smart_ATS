from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from applications.models import Application
from django.db.models import Q

import logging

from django.contrib.auth import get_user_model
from jobs.views.recruiter import job_queryset_for

User = get_user_model()
logger = logging.getLogger(__name__)


def application_queryset_for(user):
    if user.role == "ADMIN":
        return Application.objects.filter(job__is_deleted=False)

    return Application.objects.filter(job__created_by=user, job__is_deleted=False)


# =================================================================
#                    RECRUITER APPLICATION LIST
# =================================================================
@login_required
def recruiter_application_list(request):
    if request.user.role != "RECRUITER":
        raise PermissionDenied()

    qs = application_queryset_for(request.user).order_by("-applied_at")

    search = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status", "")

    if search:
        qs = qs.filter(Q(full_name__icontains=search) | Q(email__icontains=search))

    if status_filter:
        qs = qs.filter(status=status_filter)

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "recruiter/applications/list.html", {
        "applications_page": page,
        "page_obj": page,
    })


# =================================================================
#                    RECRUITER APPLICATION DETAIL
# =================================================================
@login_required
def recruiter_application_detail(request, pk):
    if request.user.role != "RECRUITER":
        raise PermissionDenied()

    application = get_object_or_404(
        application_queryset_for(request.user), pk=pk
    )

    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = dict(application._meta.get_field("status").choices).keys()

        if new_status in valid_statuses:
            application.status = new_status
            application.save()

        return redirect("recruiter_application_detail", pk=application.pk)

    return render(request, "recruiter/applications/detail.html", {
        "application": application,
    })


# =================================================================
#                    PREVIEW RESUME
# =================================================================
@login_required
def preview_resume(request, pk):
    application = get_object_or_404(
        Application, pk=pk, job__created_by=request.user, job__is_deleted=False
    )
    return redirect(application.resume_url)


# =================================================================
#              JOB-SPECIFIC APPLICATION LIST
# =================================================================
@login_required
def recruiter_job_applications(request, job_id):

    if request.user.role not in ["RECRUITER", "ADMIN"]:
        logger.warning(f"Unauthorized job-applications access by {request.user.email}")
        raise PermissionDenied()


    job = get_object_or_404(job_queryset_for(request.user), id=job_id)

    qs = (
        application_queryset_for(request.user)
        .filter(job=job)
        .order_by("-applied_at")
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        qs = qs.filter(Q(full_name__icontains=search) | Q(email__icontains=search))
    if status:
        qs = qs.filter(status=status)

    all_apps = application_queryset_for(request.user).filter(job=job)
    counts = {
        "screening": all_apps.filter(status="screening").count(),
        "review":    all_apps.filter(status="review").count(),
        "interview": all_apps.filter(status="interview").count(),
        "hired":     all_apps.filter(status="hired").count(),
        "rejected":  all_apps.filter(status="rejected").count(),
    }

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "recruiter/applications/list.html", {
        "job": job,
        "applications_page": page,
        "page_obj": page,
        "counts": counts,
    })
