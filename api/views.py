import logging
import tempfile
import os
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate


from users.models import User
from jobs.models import Job
from applications.models import Application

from .serializers import (
    UserSerializer, JobSerializer,
    ApplicationSerializer, PublicApplicationSerializer
)

from .permissions import IsRecruiter, IsAdmin
from applications.parsing import parse_resume
from applications.utils import compute_match_score, generate_summary, evaluate_candidate, fit_category
from applications.supabase_client import upload_resume


logger = logging.getLogger(__name__)


# ============================================================
# AUTH APIs
# ============================================================
class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if not user:
            logger.warning(f"API Login failed for email={email}")
            return Response({"error": "Invalid credentials"}, status=400)

        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f"API Login success for {email}")

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({"message": "Logged out successfully"})


class MeAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ============================================================
# PUBLIC JOB APIs

# ============================================================

class PublicJobListAPI(ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Job.objects.filter(is_deleted=False).order_by("-created_at")


class PublicJobDetailAPI(RetrieveAPIView):
    serializer_class = JobSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Job.objects.filter(is_deleted=False)


# ============================================================
# RECRUITER JOB APIs
# ============================================================

class RecruiterJobListAPI(ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Job.objects.filter(
            is_deleted=False,
            created_by=self.request.user
        ).order_by("-created_at")


class RecruiterJobCreateAPI(CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RecruiterJobDetailAPI(RetrieveAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(created_by = self.request.user ,is_deleted=False)


class RecruiterJobUpdateAPI(UpdateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(is_deleted=False, created_by=self.request.user)


class RecruiterJobDeleteAPI(DestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(is_deleted=False, created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


# ============================================================
# ADMIN JOB APIs
# ============================================================

class AdminJobListAPI(ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Job.objects.filter(is_deleted=False).order_by("-created_at")


class AdminJobDetailAPI(RetrieveAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAdmin]
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(is_deleted=False)


# ============================================================
# RECRUITER APPLICATION APIs

# ============================================================

class RecruiterApplicationListAPI(ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Application.objects.select_related("job").filter(
            job__created_by=self.request.user,
            job__is_deleted=False
        ).order_by("-applied_at")


class RecruiterApplicationDetailAPI(RetrieveAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return Application.objects.select_related("job").filter(
            job__created_by=self.request.user
        )


class RecruiterUpdateStatusAPI(APIView):
    permission_classes = [IsRecruiter]

    def patch(self, request, id):
        application = get_object_or_404(
            Application, id=id, job__created_by=request.user
        )

        status_value = request.data.get("status")
        valid = [choice[0] for choice in Application._meta.get_field("status").choices]

        if status_value not in valid:
            return Response({"error": "Invalid status"}, status=400)

        application.status = status_value
        application.save()

        return Response({"message": "Status updated"})


# ============================================================
# ADMIN APPLICATION APIs
# ============================================================

class AdminApplicationListAPI(ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Application.objects.select_related("job").all().order_by("-applied_at")


class AdminApplicationDetailAPI(RetrieveAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdmin]
    lookup_field = "id"

    def get_queryset(self):
        return Application.objects.select_related("job").all()

# ============================================================
# APPLY JOB API (PUBLIC)
# ============================================================
class ApplyJobAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        job = get_object_or_404(Job, slug=slug, is_deleted=False)

        serializer = PublicApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]

        if Application.objects.filter(job=job, email=email).exists():
            return Response(
                {"error": "You have already applied for this job."},
                status=400,
            )

        resume_file = serializer.validated_data.pop("resume")


        try:
            resume_file.seek(0)
            parsed = parse_resume(resume_file, job) or {}
        except Exception as e:
            logger.warning(f"Resume parsing failed: {e}")
            parsed = {}

        try:
            resume_file.seek(0)
            resume_url = upload_resume(resume_file, job.slug)
        except Exception as e:
            logger.error(f"Supabase upload failed for job={slug}: {e}")
            return Response(
                {"error": "Failed to upload resume. Please try again."},
                status=500,
            )

        scoring = compute_match_score(parsed, job)
        print("SCORING:", scoring)

        try:
            application = Application(
                job=job,
                full_name=serializer.validated_data["full_name"],
                email=email,
                phone=serializer.validated_data["phone"],
                resume_url=resume_url,
                # Parsed fields
                parsed_skills=parsed.get("skills"),
                parsed_experience=parsed.get("experience_years"),
                parsed_projects=parsed.get("projects"),
                parsed_education=parsed.get("education"),
                parsed_certifications=parsed.get("certifications"),
                # Scoring fields
                match_score=scoring["final_score"],
                skill_score=scoring["skill_score"],
                experience_score=scoring["experience_score"],
                keyword_score=scoring["keyword_score"],
                matched_skills=scoring.get("matched_skills", []),
                missing_skills=scoring.get("missing_skills", []),
                summary=generate_summary(parsed, scoring["final_score"]),
                evaluation=evaluate_candidate(scoring["final_score"]),
                fit_category=fit_category(scoring["final_score"]),
            )
            application.save()
        except IntegrityError:
            return Response(
                {"error": "You have already applied for this job."},
                status=400,
            )

        return Response({"message": "Application submitted successfully"})

