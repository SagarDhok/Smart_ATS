from rest_framework.decorators import api_view
from rest_framework.response import Response

from jobs.models import Job
from applications.models import Application
from .serializers import JobSerializer, ApplicationSerializer, ResumeParseSerializer

from applications.parsing import parse_resume
from applications.utils import compute_match_score


@api_view(["GET"])
def api_jobs(request):
    jobs = Job.objects.filter(is_deleted=False, status="active").order_by("-created_at")
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def api_job_detail(request, slug):
    try:
        job = Job.objects.get(slug=slug, is_deleted=False)
    except Job.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    return Response(JobSerializer(job).data)


@api_view(["POST"])
def api_apply_job(request, slug):
    try:
        job = Job.objects.get(slug=slug, is_deleted=False)
    except:
        return Response({"error": "Job not found"}, status=404)

    full_name = request.data.get("full_name")
    email = request.data.get("email")
    phone = request.data.get("phone")
    resume = request.FILES.get("resume")

    if not resume:
        return Response({"error": "Resume file is required"}, status=400)

    app = Application.objects.create(
        job=job,
        full_name=full_name,
        email=email,
        phone=phone,
        resume=resume
    )

    parsed = parse_resume(app.resume.path)
    scoring = compute_match_score(parsed, job)

    Application.objects.filter(id=app.id).update(
        match_score=scoring["final_score"],
        matched_skills=scoring["matched_skills"],
        missing_skills=scoring["missing_skills"],
        skill_score=scoring["skill_score"],
        experience_score=scoring["experience_score"],
        keyword_score=scoring["keyword_score"],
    )

    return Response({"message": "Application submitted", "score": scoring})


@api_view(["POST"])
def api_parse_resume(request):
    serializer = ResumeParseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    file = serializer.validated_data["resume"]

    with open("/tmp/temp.pdf", "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    parsed = parse_resume("/tmp/temp.pdf")
    return Response(parsed)


@api_view(["POST"])
def api_score(request):
    parsed = request.data.get("parsed_data")
    job_id = request.data.get("job_id")

    if not parsed or not job_id:
        return Response({"error": "parsed_data and job_id required"}, status=400)

    try:
        job = Job.objects.get(id=job_id)
    except:
        return Response({"error": "Job not found"}, status=404)

    score = compute_match_score(parsed, job)
    return Response({"score": score})
