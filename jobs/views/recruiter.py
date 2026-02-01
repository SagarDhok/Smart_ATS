# jobs/views/hr.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from jobs.models import Job
from jobs.forms import JobForm
from django.contrib import messages
from django.db.models import Count
import logging

from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


# ============================
# ADMIN SEES ALL JOBS / RECRUITER sees their own
# ============================

def job_queryset_for(user):
    if user.role == "ADMIN":
        return Job.objects.filter(is_deleted=False)
    return Job.objects.filter(created_by=user, is_deleted=False)


class RecruiterJobListView(LoginRequiredMixin, ListView):
    template_name = "recruiter/jobs/list.html"
    context_object_name = "jobs"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["RECRUITER", "ADMIN"]:
            logger.warning(f"Unauthorized job list access attempt by {request.user.email}")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = job_queryset_for(self.request.user).annotate(
            app_count=Count('applications')
        ).order_by("-created_at")

        search = self.request.GET.get("search")
        location = self.request.GET.get("location")
        work_mode = self.request.GET.get("work_mode")

        if search:
            qs = qs.filter(title__icontains=search)
        if location:
            qs = qs.filter(location__icontains=location)
        if work_mode:
            qs = qs.filter(work_mode=work_mode)

        return qs


class RecruiterJobCreateView(LoginRequiredMixin, CreateView):
    form_class = JobForm
    template_name = "recruiter/jobs/create.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "RECRUITER":
            logger.warning(f"Unauthorized job creation attempt by {request.user.email}")
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        job = form.save(commit=False)
        job.created_by = self.request.user
        job.save()
        form.save()

        logger.info(f"Job created: id={job.id} by {self.request.user.email}")
        messages.success(self.request, "Job created successfully!")
        return redirect("recruiter_job_list")


class RecruiterJobDetailView(LoginRequiredMixin, DetailView):
    template_name = "recruiter/jobs/detail.html"
    context_object_name = "job"
    pk_url_kwarg = "id"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["RECRUITER", "ADMIN"]:
            logger.warning(f"Unauthorized job detail access attempt by {request.user.email}")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return job_queryset_for(self.request.user)


class RecruiterJobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = "recruiter/jobs/edit.html"
    pk_url_kwarg = "id"

    def dispatch(self, request, *args, **kwargs):
        job = get_object_or_404(Job, id=kwargs["id"])

        if request.user.role == "ADMIN":
            logger.warning(f"Admin attempted to edit Recruiter job {job.id}")
            return HttpResponseForbidden("Admins cannot edit recruiter-created jobs.")

        if job.created_by != request.user:
            logger.warning(f"Unauthorized job edit attempt by {request.user.email} on job {job.id}")
            return HttpResponseForbidden("Not allowed.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        job = form.save()
        logger.info(f"Job updated: id={job.id} by {self.request.user.email}")
        messages.success(self.request, "Job updated successfully!")

        action = self.request.POST.get("action")

        if action == "save_list":
            return redirect("recruiter_job_list")
        if action == "save_detail":
            return redirect("recruiter_job_detail", id=job.id)
        return redirect("recruiter_job_list")


class RecruiterJobDeleteView(LoginRequiredMixin, View):
    def post(self, request, id):
        job = get_object_or_404(Job, id=id)

        if request.user.role != "RECRUITER" or job.created_by != request.user:
            logger.warning(f"Unauthorized job delete attempt by {request.user.email} on job {job.id}")
            return HttpResponseForbidden("You cannot delete this job.")

        job.is_deleted = True
        job.save()

        logger.info(f"Job soft-deleted: id={job.id} by {request.user.email}")
        messages.success(request, "Job deleted successfully!")
        return redirect("recruiter_job_list")
