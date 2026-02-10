from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User, Invite
from django.utils import timezone
from datetime import timedelta
import uuid
from jobs.models import Job
from applications.models import Application
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import logging
from core.utils.email import send_brevo_email



# ---------------- LOGGING ----------------
logger = logging.getLogger(__name__)


# =================================================================
#                           ADMIN DASHBOARD
# =================================================================
@login_required
def admin_dashboard(request):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized admin dashboard access attempt by {request.user.email}")
        return redirect("login")

    # RECRUITER USERS PAGINATION
    recruiter_qs = User.objects.filter(role="RECRUITER", is_active=True).order_by("-created_at")
    recruiter_paginator = Paginator(recruiter_qs, 10)  #10 pages 1 , 2 3 
    recruiter_page = recruiter_paginator.get_page(request.GET.get("recruiter_page"))

    # PENDING INVITES PAGINATION
    pending_invites_qs = Invite.objects.filter(
        used=False, expires_at__gt=timezone.now()
    ).order_by("-created_at")
    pending_invites_paginator = Paginator(pending_invites_qs, 10)
    pending_invites_page = pending_invites_paginator.get_page(request.GET.get("pending_page"))

    # JOB STATS
    total_jobs = Job.objects.filter(is_deleted=False).count()

    # APPLICATION STATS
    total_applications = Application.objects.filter(job__is_deleted=False).count()
    screening = Application.objects.filter(status="screening", job__is_deleted=False).count()
    review = Application.objects.filter(status="review", job__is_deleted=False).count()
    interview = Application.objects.filter(status="interview", job__is_deleted=False).count()
    hired = Application.objects.filter(status="hired", job__is_deleted=False).count()
    rejected = Application.objects.filter(status="rejected", job__is_deleted=False).count()

    return render(request, "admin/admin_dashboard.html", {
        "recruiter_page": recruiter_page,
        "pending_invites_page": pending_invites_page,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "screening": screening,
        "review": review,
        "interview": interview,
        "hired": hired,
        "rejected": rejected,
    })


# =================================================================
#                         RECRUITER MANAGEMENT PAGE
# =================================================================
@login_required
def recruiter_management(request):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized Recruiter management access attempt by {request.user.email}")
        return redirect("login")

    search = request.GET.get("search", "").strip()
    recruiter_users = User.objects.filter(role="RECRUITER").order_by("-created_at")

    if search:
        recruiter_users = recruiter_users.filter(Q(first_name__icontains=search) |Q(last_name__icontains=search) |Q(email__icontains=search)) #or

    paginator = Paginator(recruiter_users, 10)
    recruiter_page = paginator.get_page(request.GET.get("page"))

    return render(request, "admin/recruiter_management.html", {
        "recruiter_page": recruiter_page,
        "search": search,
    })


# =================================================================
#                ACTIVATE / SUSPEND RECRUITER 
# =================================================================
@login_required
@require_POST
def suspend_recruiter(request, user_id):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized Recruiter suspend attempt by {request.user.email}")
        raise PermissionDenied()

    recruiter = get_object_or_404(User, id=user_id, role="RECRUITER")
    recruiter.is_active = False
    recruiter.save()

    logger.info(f"Recruiter suspended: id={recruiter.id}, email={recruiter.email}, by={request.user.email}")

    return JsonResponse({"status": "suspended"})


@login_required
@require_POST
def activate_recruiter(request, user_id):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized Recruiter activate attempt by {request.user.email}")
        raise PermissionDenied()

    recruiter = get_object_or_404(User, id=user_id, role="RECRUITER")
    recruiter.is_active = True
    recruiter.save()

    logger.info(f"Recruiter activated: id={recruiter.id}, email={recruiter.email}, by={request.user.email}")

    return JsonResponse({"status": "activated"})


# =================================================================
#                            INVITE RECRUITER PAGE
# =================================================================
@login_required
def invite_page(request):

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized invite page access by {request.user.email}")
        messages.error(request, "You are not authorized to access the invite page.")
        return redirect("login")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Email is required.")
            return redirect("invite") 

        # Prevent duplicate active invites
        if Invite.objects.filter(
            email=email,
            used=False,
            expires_at__gt=timezone.now()
        ).exists():
            logger.warning(f"Duplicate invite attempt for {email}")
            messages.warning(
                request,
                f"Invite already sent to {email} and is still active."
            )
            return redirect("invite")

        token = uuid.uuid4()
        signup_link = request.build_absolute_uri(f"/signup/?token={token}")

        # SEND EMAIL FIRST 
        email_sent = send_brevo_email(
            to_email=email,
            subject="Your Smart ATS Signup Link",
            html_content=f"""
                <p>Hello,</p>

                <p>You have been invited to join <strong>Smart ATS</strong> as a Recruiter.</p>

                <p>
                    <a href="{signup_link}">
                        Click here to create your account
                    </a>
                </p>

                <p>This link is valid for <strong>48 hours</strong>.</p>

                <p>— Smart ATS Admin</p>
            """
        )

        if not email_sent:
            logger.error(f"Invite email failed for {email}")
            messages.error(request, "Email could not be sent. Please try again later.")
            return redirect("invite")

        # SAVE INVITE ONLY IF EMAIL SUCCESS
        Invite.objects.create(
            email=email,
            token=token,
            created_by=request.user,
            created_by_email=request.user.email,
            expires_at=timezone.now() + timedelta(hours=48)
        )

        logger.info(f"Invite sent successfully to {email} by {request.user.email}")
        messages.success(request, f"Invite sent successfully to {email}")
        return redirect("invite")

    return render(request, "recruiter/invite.html")


# =================================================================
#                       JOB MANAGEMENT
# =================================================================
@login_required
def admin_job_list(request):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized job list access attempt by {request.user.email}")
        raise PermissionDenied()

    search = request.GET.get("search", "").strip()
    jobs_qs = Job.objects.filter(is_deleted=False).order_by("-created_at")

    if search:
        jobs_qs = jobs_qs.filter(title__icontains=search)

    paginator = Paginator(jobs_qs, 10)
    jobs_page = paginator.get_page(request.GET.get("page"))

    return render(request, "admin/jobs_list.html", {
        "jobs_page": jobs_page,
        "search": search,
    })


@login_required
def admin_job_detail(request, id):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized job detail access attempt by {request.user.email}")
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, is_deleted=False)
    return render(request, "admin/job_detail.html", {"job": job})


# =================================================================
#                    APPLICATION MANAGEMENT
# =================================================================
@login_required
def admin_application_list(request):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized application list access by {request.user.email}")
        raise PermissionDenied()

    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    applications = Application.objects.select_related("job").filter(job__is_deleted=False)

    if search:
        applications = applications.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    # COUNTS
    all_counts = Application.objects.filter(job__is_deleted=False)
    counts = {
        "screening": all_counts.filter(status="screening").count(),
        "review": all_counts.filter(status="review").count(),
        "interview": all_counts.filter(status="interview").count(),
        "hired": all_counts.filter(status="hired").count(),
        "rejected": all_counts.filter(status="rejected").count(),
    }

    paginator = Paginator(applications.order_by("-applied_at"), 10)
    apps_page = paginator.get_page(request.GET.get("page", 1))

    return render(request, "admin/apps_list.html", {
        "apps_page": apps_page,
        "search": search,
        "status_filter": status_filter,
        "counts": counts,
    })


@login_required
def admin_application_detail(request, pk):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    app = get_object_or_404(Application, pk=pk)
    return render(request, "admin/app_detail.html", {"app": app})


@login_required
def admin_job_applications(request, id):
    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        logger.warning(f"Unauthorized job applications access by {request.user.email}")
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, is_deleted=False)
    applications = Application.objects.filter(job=job).order_by("-applied_at")

    return render(request, "admin/job_applications.html", {
        "job": job,
        "applications": applications
    })

