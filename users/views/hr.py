from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from jobs.models import Job
from applications.models import Application
from django.core.exceptions import PermissionDenied

@login_required
def hr_dashboard(request):

    jobs = Job.objects.filter(created_by=request.user, is_deleted=False)
    total_jobs = jobs.count()


    apps = Application.objects.filter(job__created_by=request.user, job__is_deleted=False ,)

    context = {
        "total_jobs": total_jobs,

        "total_applications": apps.count(),
        "screening": apps.filter(status="screening").count(),
        "review": apps.filter(status="review").count(),
        "interview": apps.filter(status="interview").count(),
        "hired": apps.filter(status="hired").count(),
        "rejected": apps.filter(status="rejected").count(),
    }

    return render(request, "hr/hr_dashboard.html", context)



@login_required
def hr_job_applications(request, id):
    if request.user.role != "HR":
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, created_by=request.user, is_deleted=False)

    applications = Application.objects.filter(job=job).order_by("-applied_at")

    return render(request, "hr/applications/job_applications.html", {
        "job": job,
        "applications": applications
    })
