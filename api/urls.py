from django.urls import path
from .views import (
    LoginAPI, LogoutAPI, MeAPI,
    PublicJobListAPI, PublicJobDetailAPI,
    HRJobCreateAPI, HRJobUpdateAPI, HRJobDeleteAPI,
    ApplyJobAPI,
    HRApplicationListAPI, HRApplicationDetailAPI, HRUpdateStatusAPI
)

urlpatterns = [
    # Authentication
    path("auth/login/", LoginAPI.as_view()),
    path("auth/logout/", LogoutAPI.as_view()),
    path("auth/me/", MeAPI.as_view()),

    # Public Jobs
    path("jobs/", PublicJobListAPI.as_view()),
    path("jobs/<slug:slug>/", PublicJobDetailAPI.as_view()),

    # HR Job Management
    path("jobs/create/", HRJobCreateAPI.as_view()),
    path("jobs/<int:id>/update/", HRJobUpdateAPI.as_view()),
    path("jobs/<int:id>/delete/", HRJobDeleteAPI.as_view()),

    # Apply API (public)
    path("apply/<slug:slug>/", ApplyJobAPI.as_view()),

    # HR Application Management
    path("applications/", HRApplicationListAPI.as_view()),
    path("applications/<int:id>/", HRApplicationDetailAPI.as_view()),
    path("applications/<int:id>/status/", HRUpdateStatusAPI.as_view()),
]
