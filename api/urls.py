from django.urls import path
from .views import (
    # Auth
    LoginAPI, LogoutAPI, MeAPI,
    # Public Jobs
    PublicJobListAPI, PublicJobDetailAPI,
    # Recruiter Jobs
    RecruiterJobListAPI, RecruiterJobCreateAPI, RecruiterJobUpdateAPI, RecruiterJobDeleteAPI,RecruiterApplicationDetailAPI,
    # Admin Jobs
    AdminJobListAPI, AdminJobDetailAPI,
    # Apply
    ApplyJobAPI,
    # Recruiter Applications
    RecruiterApplicationListAPI, RecruiterApplicationDetailAPI, RecruiterUpdateStatusAPI,
    # Admin Applications
    AdminApplicationListAPI, AdminApplicationDetailAPI,
)

urlpatterns = [
    path("auth/login/", LoginAPI.as_view(), name="api-login"),
    path("auth/logout/", LogoutAPI.as_view(), name="api-logout"),
    path("auth/me/", MeAPI.as_view(), name="api-me"),

    path("jobs/", PublicJobListAPI.as_view(), name="api-public-jobs"),
    path("jobs/<slug:slug>/", PublicJobDetailAPI.as_view(), name="api-public-job-detail"),

    path("recruiter/jobs/", RecruiterJobListAPI.as_view(), name="api-recruiter-jobs"),
    path("recruiter/jobs/detail/<int:id>",RecruiterApplicationDetailAPI.as_view(), name="api-recruiter-jobs"),
    path("recruiter/jobs/create/", RecruiterJobCreateAPI.as_view(), name="api-recruiter-job-create"),
    path("recruiter/jobs/<int:id>/update/", RecruiterJobUpdateAPI.as_view(), name="api-recruiter-job-update"),
    path("recruiter/jobs/<int:id>/delete/", RecruiterJobDeleteAPI.as_view(), name="api-recruiter-job-delete"),

    path("admin/jobs/", AdminJobListAPI.as_view(), name="api-admin-jobs"),
    path("admin/jobs/<int:id>/", AdminJobDetailAPI.as_view(), name="api-admin-job-detail"),

    path("apply/<slug:slug>/", ApplyJobAPI.as_view(), name="api-apply"),

    path("recruiter/applications/", RecruiterApplicationListAPI.as_view(), name="api-recruiter-applications"),
    path("recruiter/applications/<int:id>/", RecruiterApplicationDetailAPI.as_view(), name="api-recruiter-application-detail"),
    path("recruiter/applications/<int:id>/status/", RecruiterUpdateStatusAPI.as_view(), name="api-recruiter-update-status"),

    path("admin/applications/", AdminApplicationListAPI.as_view(), name="api-admin-applications"),
    path("admin/applications/<int:id>/", AdminApplicationDetailAPI.as_view(), name="api-admin-application-detail"),
]
