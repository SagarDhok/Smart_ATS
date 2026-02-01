from django.urls import path
from jobs.views.recruiter import (
    RecruiterJobListView, RecruiterJobCreateView,
    RecruiterJobDetailView, RecruiterJobUpdateView,
    RecruiterJobDeleteView
)
from jobs.views.public import PublicJobListView, PublicJobDetailView

urlpatterns = [
    # Recruiter/Admin
    path("recruiter/list/", RecruiterJobListView.as_view(), name="recruiter_job_list"),
    path("recruiter/create/", RecruiterJobCreateView.as_view(), name="recruiter_job_create"),
    path("recruiter/<int:id>/", RecruiterJobDetailView.as_view(), name="recruiter_job_detail"),
    path("recruiter/<int:id>/edit/", RecruiterJobUpdateView.as_view(), name="recruiter_job_edit"),
    path("recruiter/<int:id>/delete/", RecruiterJobDeleteView.as_view(), name="recruiter_job_delete"),

    # Public
    path("", PublicJobListView.as_view(), name="public_jobs_list"),
    path("<slug:slug>/", PublicJobDetailView.as_view(), name="public_job_detail"),
  

]
