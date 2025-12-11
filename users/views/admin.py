from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User, Invite
from django.utils import timezone
from datetime import timedelta
import uuid
from jobs.models import Job
from applications.models import Application
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator



# ==========================
#    ADMIN DASHBOARD
# ==========================



@login_required
def admin_dashboard(request):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        return redirect("login")

    # ============================
    # HR USERS PAGINATION (10 PER PAGE)
    # ============================
    hr_qs = User.objects.filter(role="HR", is_active=True).order_by("-created_at")
    hr_paginator = Paginator(hr_qs, 10)
    hr_page_number = request.GET.get("hr_page")
    hr_page = hr_paginator.get_page(hr_page_number)

    # ============================
    # PENDING INVITES PAGINATION (10 PER PAGE)
    # ============================
    pending_invites_qs = Invite.objects.filter(
        used=False,
        expires_at__gt=timezone.now()
    ).order_by("-created_at")

    pending_invites_paginator = Paginator(pending_invites_qs, 10)
    pending_invites_page_number = request.GET.get("pending_page")
    pending_invites_page = pending_invites_paginator.get_page(pending_invites_page_number)

    # ============================
    # JOB STATS
    # ============================
    total_jobs = Job.objects.filter(is_deleted=False).count()


    # ============================
    # APPLICATION STATS
    # ============================
    total_applications = Application.objects.filter(job__is_deleted=False).count()
    screening = Application.objects.filter(status="screening", job__is_deleted=False).count()
    review = Application.objects.filter(status="review", job__is_deleted=False).count()
    interview = Application.objects.filter(status="interview", job__is_deleted=False).count()
    hired = Application.objects.filter(status="hired", job__is_deleted=False).count()
    rejected = Application.objects.filter(status="rejected", job__is_deleted=False).count()

    return render(request, "admin/admin_dashboard.html", {
        "hr_page": hr_page,
        "pending_invites_page": pending_invites_page,

        "total_jobs": total_jobs,

        "total_applications": total_applications,
        "screening": screening,
        "review": review,
        "interview": interview,
        "hired": hired,
        "rejected": rejected,
    })


# ==========================
#    HR MANAGEMENT PAGE
# ==========================
@login_required
def hr_management(request):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        return redirect("login")

    search = request.GET.get("search", "").strip()
    hr_users = User.objects.filter(role="HR").order_by("-created_at")

    if search:
        hr_users = hr_users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )

    paginator = Paginator(hr_users, 10)
    page_number = request.GET.get("page")
    hr_page = paginator.get_page(page_number)

    return render(request, "admin/hr_management.html", {
        "hr_page": hr_page,
        "search": search,
    })


# ==========================
#     ACTIVATE / SUSPEND HR
# ==========================

# “Initially I used the standard POST-redirect-GET pattern with pagination and filters, but that created multiple browser history entries because each action triggered a full page navigation. That naturally broke the back button UX.

# To fix this correctly, I converted the suspend/activate endpoints into POST-only JSON APIs secured with CSRF, and triggered them using fetch from the template. The UI then soft-reloads without adding a history entry, so pagination, filters, and browser navigation remain intact.

# This keeps the system server-rendered but avoids unnecessary navigation for state-changing actions.”


# “Why can’t pure Django redirects fix the back button issue?”

# Your reply:

# “Because each successful GET after redirect creates a new history entry at the browser level, and history behavior is controlled by the browser, not the server. So as long as we navigate using full requests, back navigation can’t be collapsed into one step. Only preventing navigation altogether using async requests avoids that.”


# Since Django’s CSRF protection relies on cookies and headers, I extracted the csrftoken from the cookie and explicitly passed it in the X-CSRFToken header with credentials: same-origin to ensure the cookie is sent.”




# ✅ For project submission & interviews → leave pagination history as it is (normal behavior)“Because pagination uses normal anchor navigation, and browsers preserve exact navigation order. If we want linear back behavior, we must override it using history.replaceState or location.replace on the frontend. Backend alone cannot control browser history.” ye sahi hai 


# “My core hands-on experience is in backend with Django, but to improve the user experience and avoid unnecessary full-page reloads, I implemented AJAX for state-changing actions like suspend and activate.

# As for pagination history, that is normal browser navigation behavior because pagination uses anchor-based routing. Controlling how the back button behaves is a frontend concern using history.replaceState or location.replace. Since it wasn’t a functional bug and preserving deep links is important, I intentionally kept the default behavior.”
    
#     “My core hands-on experience is in backend with Django, but to improve the user experience and avoid unnecessary full-page reloads, I implemented AJAX for state-changing actions like suspend and activate.

# As for pagination history, that is normal browser navigation behavior because pagination uses anchor-based routing. Controlling how the back button behaves is a frontend concern using history.replaceState or location.replace. Since it wasn’t a functional bug and preserving deep links is important, I intentionally kept the default behavior.”

# This version makes you sound:
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@login_required
@require_POST
def suspend_hr(request, user_id):
    hr = get_object_or_404(User, id=user_id, role="HR")
    hr.is_active = False
    hr.save()
    return JsonResponse({"status": "suspended"})


@login_required
@require_POST
def activate_hr(request, user_id):
    hr = get_object_or_404(User, id=user_id, role="HR")
    hr.is_active = True
    hr.save()
    return JsonResponse({"status": "activated"})


# ==========================
#      INVITE HR PAGE
# ==========================
@login_required
def invite_page(request):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        messages.error(request, "You are not authorized to access the invite page.")
        return redirect("login")

    if request.method == "POST":
        email = request.POST.get("email")

        if Invite.objects.filter(email=email, used=False, expires_at__gt=timezone.now()).exists():
            messages.warning(request, f"Invite already sent to {email} and is still active.")
            return redirect("invite")

        token = uuid.uuid4()

        Invite.objects.create(
            email=email,
            token=token,
            created_by=request.user,
            created_by_email=request.user.email,
            expires_at=timezone.now() + timedelta(hours=48)
        )

        signup_link = request.build_absolute_uri(f"/signup/?token={token}")


        send_mail(
            subject="Your ATS Signup Link",
            message=f"""
Hello,

You have been invited to join the Smart ATS platform as an HR user.
Please use the link below to complete your account setup:

{signup_link}

This link is valid for 48 hours and can be used only once.

Regards,
Smart ATS Admin
""",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, f"Invite sent successfully to {email}")
        return redirect("invite")

    return render(request, "hr/invite.html")


# ==========================
#     JOB MANAGEMENT
# ==========================
@login_required
def admin_job_list(request):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        raise PermissionDenied()

    search = request.GET.get("search", "").strip()

    jobs_qs = Job.objects.filter(is_deleted=False).order_by("-created_at")

    # 🔍 SEARCH by job title
    if search:
        jobs_qs = jobs_qs.filter(title__icontains=search)

    # 📄 PAGINATION — 10 per page
    paginator = Paginator(jobs_qs, 10)
    page_number = request.GET.get("page")
    jobs_page = paginator.get_page(page_number)

    return render(request, "admin/jobs_list.html", {
        "jobs_page": jobs_page,
        "search": search,
    })


@login_required
def admin_job_detail(request, id):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, is_deleted=False)
    return render(request, "admin/job_detail.html", {"job": job})


# ==========================
#   APPLICATION MANAGEMENT
# ==========================
@login_required
def admin_application_list(request):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        raise PermissionDenied()

    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    applications = Application.objects.select_related("job").filter(job__is_deleted=False)

    # SEARCH
    if search:
        applications = applications.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )

    # STATUS FILTER
    if status_filter:
        applications = applications.filter(status=status_filter)

    # COUNTS FOR DROPDOWN
    all_counts = Application.objects.filter(job__is_deleted=False)
    counts = {
        "screening": all_counts.filter(status="screening").count(),
        "review": all_counts.filter(status="review").count(),
        "interview": all_counts.filter(status="interview").count(),
        "hired": all_counts.filter(status="hired").count(),
        "rejected": all_counts.filter(status="rejected").count(),
    }

    # PAGINATION
    paginator = Paginator(applications.order_by("-applied_at"), 15)
    apps_page = paginator.get_page(request.GET.get("page", 1))

    return render(request, "admin/apps_list.html", {
        "apps_page": apps_page,
        "search": search,
        "status_filter": status_filter,
        "counts": counts,
    })


@login_required
def admin_application_detail(request, pk):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        raise PermissionDenied()

    app = get_object_or_404(Application, pk=pk)
    return render(request, "admin/app_detail.html", {"app": app})


@login_required
def admin_job_applications(request, id):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, is_deleted=False)
    applications = Application.objects.filter(job=job).order_by("-applied_at")

    return render(request, "admin/job_applications.html", {
        "job": job,
        "applications": applications
    })


# ==========================
#       DOWNLOAD RESUME
# ==========================
import os
from django.http import FileResponse



@login_required
def admin_resume_download(request, pk):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        raise PermissionDenied()

    app = get_object_or_404(Application, pk=pk)

    if not os.path.exists(app.resume.path):
        messages.error(request, "Resume file not found on server.")
        return redirect("admin_application_detail", pk=pk)

    return FileResponse(
        open(app.resume.path, "rb"),
        as_attachment=True,
        filename=os.path.basename(app.resume.name)
    )
