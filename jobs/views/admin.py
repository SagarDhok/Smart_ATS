from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from jobs.models import Job

import logging

# ---------------- LOGGING ----------------
logger = logging.getLogger(__name__)


# =================================================================
#                       ADMIN JOB LIST
# =================================================================
@login_required
def admin_job_list(request):
    if request.user.role != "ADMIN":
        logger.warning(f"Unauthorized job list access attempt by {request.user.email}")
        raise PermissionDenied()

    jobs_qs = Job.objects.filter(is_deleted=False).order_by("-created_at")

    search = request.GET.get("search", "").strip()
    if search:
        jobs_qs = jobs_qs.filter(title__icontains=search)

    paginator = Paginator(jobs_qs, 10)
    jobs_page = paginator.get_page(request.GET.get("page"))

    return render(request, "admin/jobs/jobs_list.html", {
        "jobs_page": jobs_page,
    })


# =================================================================
#                       ADMIN JOB DETAIL
# =================================================================
@login_required
def admin_job_detail(request, id):
    if request.user.role != "ADMIN":
        logger.warning(f"Unauthorized job detail access attempt by {request.user.email}")
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, is_deleted=False)
    return render(request, "admin/jobs/job_detail.html", {"job": job})
