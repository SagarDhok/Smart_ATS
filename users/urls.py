from django.urls import path
from users.views.auth import (
    login_page, signup_page,
    forgot_password_request, reset_password_page,
    force_password_reset,logout_user,profile_view
)
from users.views.admin import (
    admin_dashboard, hr_management,
    suspend_hr, activate_hr,
    invite_page,admin_application_detail,admin_application_list,admin_job_detail,admin_job_list,admin_job_applications
)
from users.views.hr import hr_dashboard,hr_job_applications

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
    path("dashboard/hr/", hr_dashboard, name="hr_dashboard"),

    # HR MANAGEMENT
    path("dashboard/admin/hr-management/", hr_management, name="hr_management"),
    # path("dashboard/admin/hr/suspend/<int:user_id>/", suspend_hr, name="suspend_hr"),
    # path("dashboard/admin/hr/activate/<int:user_id>/", activate_hr, name="activate_hr"),
    path("dashboard/admin/suspend-hr/<int:user_id>/", suspend_hr, name="suspend_hr"),
    path("dashboard/admin/activate-hr/<int:user_id>/", activate_hr, name="activate_hr"),


    # INVITE HR
    path("invite/", invite_page, name="invite"),


    # ADMIN JOB VIEWS
    path("dashboard/admin/jobs/", admin_job_list, name="admin_job_list"),
    path("dashboard/admin/jobs/<int:id>/", admin_job_detail, name="admin_job_detail"),

    # ADMIN APPLICATION VIEWS
    path("dashboard/admin/applications/", admin_application_list, name="admin_application_list"),
    path("dashboard/admin/applications/<int:pk>/", admin_application_detail, name="admin_application_detail"),
    path("dashboard/admin/job/<int:id>/applications/", admin_job_applications, name="admin_job_applications"),
    path("dashboard/admin/applications/", admin_application_list, name="admin_application_list"),

    # HR job-specific applications list
   path('hr/applications/<int:id>/applications/', hr_job_applications, name='hr_job_applications'),





]
