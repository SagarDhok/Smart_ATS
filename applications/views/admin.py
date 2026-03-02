from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from applications.models import Application
from jobs.models import Job

import logging

# ---------------- LOGGING ----------------
logger = logging.getLogger(__name__)


# =================================================================
#                    ADMIN APPLICATION LIST
# =================================================================
@login_required
def admin_application_list(request):
    if request.user.role != "ADMIN":
        logger.warning(f"Unauthorized application list access by {request.user.email}")
        raise PermissionDenied()

    applications = Application.objects.select_related("job").filter(job__is_deleted=False)

    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    if search:
        applications = applications.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    # COUNTS
    all_counts = Application.objects.filter(job__is_deleted=False)
    counts = {
        "screening": all_counts.filter(status="screening").count(),
        "review": all_counts.filter(status="review").count(),
        "interview": all_counts.filter(status="interview").count(),
        "hired": all_counts.filter(status="hired").count(),
        "rejected": all_counts.filter(status="rejected").count(),
    }

    paginator = Paginator(applications.order_by("-applied_at"), 10)
    applications_page = paginator.get_page(request.GET.get("page", 1))

    return render(request, "admin/applications/apps_list.html", {
        "applications_page": applications_page,
        "counts": counts,
    })


# =================================================================
#                    ADMIN APPLICATION DETAIL
# =================================================================
@login_required
def admin_application_detail(request, pk):
    if request.user.role != "ADMIN":
        raise PermissionDenied()

    application = get_object_or_404(Application, pk=pk)
    return render(request, "admin/applications/app_detail.html", {"application": application})


# =================================================================
#                    ADMIN JOB APPLICATIONS
# =================================================================
@login_required
def admin_job_applications(request, id):
    if request.user.role != "ADMIN":
        logger.warning(f"Unauthorized job applications access by {request.user.email}")
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, is_deleted=False)
    applications = Application.objects.filter(job=job).order_by("-applied_at")

    return render(request, "admin/applications/job_applications.html", {
        "job": job,
        "applications": applications,
    })
