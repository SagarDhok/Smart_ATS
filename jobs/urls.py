from django.urls import path
from jobs.views.hr import (
    HRJobListView, HRJobCreateView,
    HRJobDetailView, HRJobUpdateView,
    HRJobDeleteView
)
from jobs.views.public import PublicJobListView, PublicJobDetailView

urlpatterns = [
    # HR/Admin
    path("hr/list/", HRJobListView.as_view(), name="hr_job_list"),
    path("hr/create/", HRJobCreateView.as_view(), name="hr_job_create"),
    path("hr/<int:id>/", HRJobDetailView.as_view(), name="hr_job_detail"),
    path("hr/<int:id>/edit/", HRJobUpdateView.as_view(), name="hr_job_edit"),
    path("hr/<int:id>/delete/", HRJobDeleteView.as_view(), name="hr_job_delete"),

    # Public
    path("", PublicJobListView.as_view(), name="public_jobs_list"),
    path("<slug:slug>/", PublicJobDetailView.as_view(), name="public_job_detail"),
  

]
