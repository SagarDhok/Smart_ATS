from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import logging

from jobs.models import Job
from applications.models import Application

logger = logging.getLogger(__name__)


# ===============================================================
#                         RECRUITER DASHBOARD
# ===============================================================
@login_required
def recruiter_dashboard(request):
    if request.user.role != "RECRUITER":
        logger.warning(f"Unauthorized Recruiter dashboard access attempt by {request.user.email}")
        raise PermissionDenied()

    jobs = Job.objects.filter(created_by=request.user, is_deleted=False)
    total_jobs = jobs.count()

    apps = Application.objects.filter(job__created_by=request.user, job__is_deleted=False)

    context = {
        "total_jobs": total_jobs,
        "total_applications": apps.count(),
        "screening": apps.filter(status="screening").count(),
        "review": apps.filter(status="review").count(),
        "interview": apps.filter(status="interview").count(),
        "hired": apps.filter(status="hired").count(),
        "rejected": apps.filter(status="rejected").count(),
    }

    return render(request, "recruiter/recruiter_dashboard.html", context)
