from rest_framework import serializers
from users.models import User
from jobs.models import Job
from applications.models import Application


# ----------------------------------------
# USER SERIALIZER
# ----------------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role"]


# ----------------------------------------
# JOB SERIALIZER
# ----------------------------------------
class JobSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "title", "slug", "description",
            "required_skills", "jd_keywords",
            "min_experience", "max_experience",
            "min_salary", "max_salary",
            "location", "work_mode",
            "employment_type",
            "created_by", "created_at"
        ]


# ----------------------------------------
# APPLICATION SERIALIZER (HR USE)
# ----------------------------------------
class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = Application
        fields = "__all__"


# ----------------------------------------
# PUBLIC APPLY FORM
# ----------------------------------------
class PublicApplicationSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(required=True)

    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "resume"]

    def validate_resume(self, value):
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Only PDF files are allowed.")
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Resume size cannot exceed 5MB.")
        return value

    def validate_email(self, value):
        return value.strip().lower()
