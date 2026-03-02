from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Max
from jobs.models import Job


# =================================================================
#                    PUBLIC JOB LIST
# =================================================================
def public_job_list(request):
    qs = Job.objects.filter(is_deleted=False)

    # ---------- filters ----------
    search = request.GET.get("search")
    location = request.GET.get("location")
    work_mode = request.GET.get("work_mode")
    job_type = request.GET.get("job_type")
    min_salary = request.GET.get("min_salary")
    max_salary = request.GET.get("max_salary")

    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(required_skills__icontains=search)
        )

    if location:
        qs = qs.filter(location__icontains=location)

    if work_mode:
        qs = qs.filter(work_mode=work_mode)

    if job_type:
        qs = qs.filter(employment_type=job_type)

    if min_salary:
        qs = qs.filter(min_salary__isnull=False, min_salary__gte=min_salary)

    if max_salary:
        qs = qs.filter(max_salary__isnull=False, max_salary__lte=max_salary)

    qs = qs.order_by("-created_at")

    # ---------- pagination ----------
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))

    # ---------- global salary range ----------
    salary_range = Job.objects.aggregate(max_salary_global=Max("max_salary"))

    context = {
        "jobs": page,                          
        "page_obj": page,                      
        "paginator": paginator,
        "salary_min_global": 0,
        "salary_max_global": salary_range["max_salary_global"] or 1000000,
    }

    return render(request, "jobs/public_jobs_list.html", context)


# =================================================================
#                    PUBLIC JOB DETAIL
# =================================================================
def public_job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug, is_deleted=False)
    return render(request, "jobs/public_job_detail.html", {"job": job})
