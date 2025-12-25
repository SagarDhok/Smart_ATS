from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from applications.models import Application
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


def app_queryset_for(user):
    if user.role == "ADMIN":
        return Application.objects.filter(job__is_deleted=False)

    return Application.objects.filter(
        job__created_by=user,
        job__is_deleted=False,
    )


class HRApplicationListView(LoginRequiredMixin, ListView):
    template_name = "hr/applications/list.html"
    context_object_name = "apps_page"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "HR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = app_queryset_for(self.request.user).order_by("-applied_at")

        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(Q(full_name__icontains=search) | Q(email__icontains=search))

        status_filter = self.request.GET.get("status", "")
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs


class HRApplicationDetailView(LoginRequiredMixin, DetailView):
    template_name = "hr/applications/detail.html"
    context_object_name = "app"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "HR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return app_queryset_for(self.request.user)


class HRStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    fields = ["status"]
    template_name = "hr/applications/status_update.html"
    context_object_name = "app"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "HR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return app_queryset_for(self.request.user)

    def form_valid(self, form):
        form.save()
        return redirect("hr_application_detail", pk=self.object.pk)


@login_required
def preview_resume(request, pk):
    app = get_object_or_404(
        Application,
        pk=pk,
        job__created_by=request.user,
        job__is_deleted=False,
    )
    return redirect(app.resume_url)


@login_required
def download_resume(request, pk):
    app = get_object_or_404(
        Application,
        pk=pk,
        job__created_by=request.user,
        job__is_deleted=False,
    )
    return redirect(app.resume_url)
