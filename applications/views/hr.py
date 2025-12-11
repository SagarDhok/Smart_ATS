from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from applications.models import Application
from jobs.models import Job
from django.db.models import Q



# ------------------------------
# GLOBAL APPLICATION QUERYSET
# ------------------------------
def app_queryset_for(user):
    if user.role == "ADMIN":
        return Application.objects.filter(job__is_deleted=False)

    return Application.objects.filter(
        job__created_by=user,
        job__is_deleted=False
    )


# ------------------------------
# LIST VIEW
# ------------------------------
class HRApplicationListView(LoginRequiredMixin, ListView):
    template_name = "hr/applications/list.html"
    context_object_name = "apps_page"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user

        qs = Application.objects.filter(
            job__created_by=user,
            job__is_deleted=False
        ).order_by("-applied_at")

        # SEARCH
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search)
            )

        # STATUS FILTER
        status_filter = self.request.GET.get("status", "")
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user = self.request.user

        # Counts for status dropdown
        base_qs = Application.objects.filter(
            job__created_by=user,
            job__is_deleted=False
        )

        ctx["counts"] = {
            "screening": base_qs.filter(status="screening").count(),
            "review": base_qs.filter(status="review").count(),
            "interview": base_qs.filter(status="interview").count(),
            "hired": base_qs.filter(status="hired").count(),
            "rejected": base_qs.filter(status="rejected").count(),
        }

        ctx["search"] = self.request.GET.get("search", "")
        ctx["status_filter"] = self.request.GET.get("status", "")

        return ctx



# ------------------------------
# DETAIL VIEW
# ------------------------------
class HRApplicationDetailView(LoginRequiredMixin, DetailView):
    template_name = "hr/applications/detail.html"
    context_object_name = "app"

    def get_queryset(self):
        return app_queryset_for(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        app = ctx["app"]

        if isinstance(app.job.required_skills, str):
            app.job.required_skills = [
                s.strip() for s in app.job.required_skills.split(",") if s.strip()
            ]

        ctx["app"] = app
        return ctx

# ------------------------------
# STATUS UPDATE VIEW
# ------------------------------
class HRStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    fields = ["status"]
    template_name = "hr/applications/status_update.html"
    context_object_name = "app"

    def get_queryset(self):
        return app_queryset_for(self.request.user)

    def form_valid(self, form):
        form.save()
        return redirect("hr_application_detail", pk=self.object.pk)


# ------------------------------
# PDF PREVIEW
# ------------------------------
def preview_resume(request, pk):
    app = get_object_or_404(
        Application,
        pk=pk,
        job__created_by=request.user,
        job__is_deleted=False
    )

    file_path = app.resume.path
    response = FileResponse(open(file_path, "rb"), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{app.resume.name}"'
    return response


# ------------------------------
# PDF DOWNLOAD
# ------------------------------
def download_resume(request, pk):
    app = get_object_or_404(
        Application,
        pk=pk,
        job__created_by=request.user,
        job__is_deleted=False
    )

    file_path = app.resume.path
    response = FileResponse(open(file_path, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{app.resume.name}"'
    return response
