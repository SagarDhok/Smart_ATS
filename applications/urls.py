from django.urls import path
from django.shortcuts import render
from applications.views.public import apply_job

from applications.views.recruiter import (
    RecruiterApplicationListView, RecruiterApplicationDetailView,
    preview_resume,RecruiterStatusUpdateView
)

urlpatterns = [
    path("apply/<slug:slug>/", apply_job, name="apply_job"),
    path("success/", lambda r: render(r, "applications/success.html"), name="application_success"),

    path("recruiter/list/", RecruiterApplicationListView.as_view(), name="recruiter_applications_list"),
    path("recruiter/<int:pk>/", RecruiterApplicationDetailView.as_view(), name="recruiter_application_detail"),

    # NEW
    path("recruiter/<int:pk>/status/", RecruiterStatusUpdateView.as_view(), name="recruiter_application_status"),

    path("recruiter/<int:pk>/resume/preview/", preview_resume, name="preview_resume"),
]
