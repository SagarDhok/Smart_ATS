from django.urls import path
from jobs.views.recruiter import (
    recruiter_job_list, recruiter_job_create,
    recruiter_job_detail, recruiter_job_edit,
    recruiter_job_delete
)
from jobs.views.public import public_job_list, public_job_detail
from jobs.views.admin import admin_job_list, admin_job_detail

urlpatterns = [
    # Recruiter
    path("jobs/recruiter/list/", recruiter_job_list, name="recruiter_job_list"),
    path("jobs/recruiter/create/", recruiter_job_create, name="recruiter_job_create"),
    path("jobs/recruiter/<int:id>/", recruiter_job_detail, name="recruiter_job_detail"),
    path("jobs/recruiter/<int:id>/edit/", recruiter_job_edit, name="recruiter_job_edit"),
    path("jobs/recruiter/<int:id>/delete/", recruiter_job_delete, name="recruiter_job_delete"),

    # Public
    path("jobs/", public_job_list, name="public_jobs_list"),
    path("jobs/<slug:slug>/", public_job_detail, name="public_job_detail"),

    # Admin
    path("dashboard/admin/jobs/", admin_job_list, name="admin_job_list"),
    path("dashboard/admin/jobs/<int:id>/", admin_job_detail, name="admin_job_detail"),
]
