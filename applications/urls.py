from django.urls import path
from django.shortcuts import render
from applications.views.public import apply_job

from applications.views.recruiter import (
    recruiter_application_list, recruiter_application_detail,
    preview_resume
)
from applications.views.admin import (
    admin_application_list, admin_application_detail, admin_job_applications
)

urlpatterns = [
    # Public
    path("applications/apply/<slug:slug>/", apply_job, name="apply_job"),
    path("applications/success/", lambda r: render(r, "applications/success.html"), name="application_success"),

    # Recruiter
    path("applications/recruiter/list/", recruiter_application_list, name="recruiter_applications_list"),
    path("applications/recruiter/<int:pk>/", recruiter_application_detail, name="recruiter_application_detail"),
    path("applications/recruiter/<int:pk>/resume/preview/", preview_resume, name="preview_resume"),

    # Admin
    path("dashboard/admin/applications/", admin_application_list, name="admin_application_list"),
    path("dashboard/admin/applications/<int:pk>/", admin_application_detail, name="admin_application_detail"),
    path("dashboard/admin/job/<int:id>/applications/", admin_job_applications, name="admin_job_applications"),
]
