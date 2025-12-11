
# jobs/views/hr.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from jobs.models import Job
from jobs.forms import JobForm
from django.contrib import messages

# ============================
# 🔥 ADMIN SEES ALL JOBS
# 🔥 HR SEES ONLY THEIR JOBS
# ============================

def job_queryset_for(user):
    if user.role == "ADMIN":
        return Job.objects.filter(is_deleted=False)
    return Job.objects.filter(created_by=user, is_deleted=False)

from django.db.models import Count 

class HRJobListView(LoginRequiredMixin, ListView):
    template_name = "hr/jobs/list.html"
    context_object_name = "jobs"
    paginate_by = 10

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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filters"] = self.request.GET
        return ctx



class HRJobCreateView(LoginRequiredMixin, CreateView):
    form_class = JobForm
    template_name = "hr/jobs/create.html"

    def dispatch(self, request, *a, **kw):
        if request.user.role != "HR":
            return HttpResponseForbidden()
        return super().dispatch(request, *a, **kw)

    def form_valid(self, form):
        job = form.save(commit=False)
        job.created_by = self.request.user
        job.save()
        form.save()  

        messages.success(self.request, "Job created successfully!")

        return redirect("hr_job_list")



class HRJobDetailView(LoginRequiredMixin, DetailView):
    template_name = "hr/jobs/detail.html"
    context_object_name = "job"
    pk_url_kwarg = "id"

    def get_queryset(self):
        return job_queryset_for(self.request.user)


class HRJobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = "hr/jobs/edit.html"
    pk_url_kwarg = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN":
            return Job.objects.filter(is_deleted=False)
        return Job.objects.filter(created_by=user)

    def dispatch(self, request, *a, **kw):
        job = get_object_or_404(Job, id=kw["id"])

        if request.user.role == "ADMIN":
            return HttpResponseForbidden("Admins cannot edit recruiter-created jobs.")

        if job.created_by != request.user:
            return HttpResponseForbidden("Not allowed.")

        return super().dispatch(request, *a, **kw)

    def form_valid(self, form):
        job = form.save()
        messages.success(self.request, "Job updated successfully!")

        action = self.request.POST.get("action")

        # Go back to job list
        if action == "save_list":
            return redirect("hr_job_list")

        # Go to job detail page
        if action == "save_detail":
            return redirect("hr_job_detail", id=job.id)

        # Default fallback
        return redirect("hr_job_list")


class HRJobDeleteView(LoginRequiredMixin, View):
    def post(self, request, id):
        job = get_object_or_404(Job, id=id)

        if request.user.role != "HR" or job.created_by != request.user:
            return HttpResponseForbidden("You cannot delete this job.")

        job.is_deleted = True
        job.save()

        messages.success(request, "Job deleted successfully!")
        return redirect("hr_job_list")


