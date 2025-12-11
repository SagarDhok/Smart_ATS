from django.urls import path
from django.shortcuts import render
from applications.views.public import apply_job

from applications.views.hr import (
    HRApplicationListView, HRApplicationDetailView,
    preview_resume, download_resume,HRStatusUpdateView
)

urlpatterns = [
    path("apply/<slug:slug>/", apply_job, name="apply_job"),
    path("success/", lambda r: render(r, "applications/success.html"), name="application_success"),

    path("hr/list/", HRApplicationListView.as_view(), name="hr_applications_list"),
    path("hr/<int:pk>/", HRApplicationDetailView.as_view(), name="hr_application_detail"),

    # NEW
    path("hr/<int:pk>/status/", HRStatusUpdateView.as_view(), name="hr_application_status"),

    path("hr/<int:pk>/resume/preview/", preview_resume, name="preview_resume"),
    path("hr/<int:pk>/resume/download/", download_resume, name="download_resume"),
]
