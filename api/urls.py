from django.urls import path
from .views import api_jobs, api_job_detail, api_apply_job, api_parse_resume, api_score

urlpatterns = [
    path("jobs/", api_jobs),
    path("jobs/<slug:slug>/", api_job_detail),
    path("jobs/<slug:slug>/apply/", api_apply_job),
    path("parse-resume/", api_parse_resume),
    path("score/", api_score),
]
