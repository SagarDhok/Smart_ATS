import logging
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from users.models import User
from jobs.models import Job
from applications.models import Application

from .serializers import (
    UserSerializer, JobSerializer,
    ApplicationSerializer, PublicApplicationSerializer
)

from .permissions import IsHR
from applications.parsing import parse_resume
from applications.utils import compute_match_score, generate_summary, evaluate_candidate, fit_category


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
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"})


class MeAPI(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ============================================================
# PUBLIC JOB APIs
# ============================================================

class PublicJobListAPI(ListAPIView):
    queryset = Job.objects.filter(is_deleted=False)
    serializer_class = JobSerializer
    permission_classes = [AllowAny]


class PublicJobDetailAPI(RetrieveAPIView):
    queryset = Job.objects.filter(is_deleted=False)
    serializer_class = JobSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


# ============================================================
# HR JOB APIs
# ============================================================

class HRJobCreateAPI(CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsHR]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class HRJobUpdateAPI(UpdateAPIView):
    queryset = Job.objects.filter(is_deleted=False)
    serializer_class = JobSerializer
    permission_classes = [IsHR]
    lookup_field = "id"


class HRJobDeleteAPI(DestroyAPIView):
    queryset = Job.objects.filter(is_deleted=False)
    serializer_class = JobSerializer
    permission_classes = [IsHR]
    lookup_field = "id"

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


# ============================================================
# APPLY JOB API
# ============================================================

class ApplyJobAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        job = get_object_or_404(Job, slug=slug)

        serializer = PublicApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        app = serializer.save(job=job)

        parsed = parse_resume(app.resume.path, job)
        scoring = compute_match_score(parsed, job)

        # Scoring fields
        app.match_score = scoring["final_score"]
        app.skill_score = scoring["skill_score"]
        app.experience_score = scoring["experience_score"]
        app.keyword_score = scoring["keyword_score"]
        app.summary = generate_summary(parsed, scoring["final_score"])
        app.evaluation = evaluate_candidate(scoring["final_score"])
        app.fit_category = fit_category(scoring["final_score"])
        app.save()

        return Response({"message": "Application submitted successfully"})


# ============================================================
# HR APPLICATION APIs
# ============================================================

class HRApplicationListAPI(ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsHR]

    def get_queryset(self):
        return Application.objects.filter(
            job__created_by=self.request.user,
            job__is_deleted=False
        ).order_by("-applied_at")


class HRApplicationDetailAPI(RetrieveAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsHR]
    lookup_field = "id"

    def get_queryset(self):
        return Application.objects.filter(
            job__created_by=self.request.user
        )


class HRUpdateStatusAPI(APIView):
    permission_classes = [IsHR]

    def patch(self, request, id):
        app = get_object_or_404(
            Application, id=id, job__created_by=request.user
        )

        status_value = request.data.get("status")
        valid = ["screening", "review", "interview", "hired", "rejected"]

        if status_value not in valid:
            return Response({"error": "Invalid status"}, status=400)

        app.status = status_value
        app.save()

        return Response({"message": "Status updated"})
