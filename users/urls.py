from django.urls import path
from users.views.auth import (
    login_page, signup_page,
    forgot_password_request, reset_password_page,
    force_password_reset,logout_user,profile_view
)
from users.views.admin import (
    admin_dashboard, recruiter_management,
    suspend_recruiter, activate_recruiter,
    invite_page
)
from users.views.recruiter import recruiter_dashboard
from applications.views.recruiter import recruiter_job_applications

urlpatterns = [

    # AUTH
    path("login/", login_page, name="login"),
    path("logout/", logout_user, name="logout_user"),
    path("profile/", profile_view, name="profile"),

    path("signup/", signup_page, name="signup"),
    path("forgot-password/", forgot_password_request, name="forgot_password"),
    path("reset-password/", reset_password_page, name="reset_password"),
    path("force-reset/", force_password_reset, name="force_password_reset"),

    # DASHBOARDS
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/recruiter/", recruiter_dashboard, name="recruiter_dashboard"),

    # RECRUITER MANAGEMENT
    path("dashboard/admin/recruiter-management/", recruiter_management, name="recruiter_management"),
    path("dashboard/admin/suspend-recruiter/<int:user_id>/", suspend_recruiter, name="suspend_recruiter"),
    path("dashboard/admin/activate-recruiter/<int:user_id>/", activate_recruiter, name="activate_recruiter"),

    # INVITE RECRUITER
    path("invite/", invite_page, name="invite"),

    # RECRUITER job-specific applications list
    path('recruiter/jobs/<int:job_id>/applications/', recruiter_job_applications, name='recruiter_job_applications'),

]
