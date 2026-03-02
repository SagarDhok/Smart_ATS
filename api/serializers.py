from rest_framework import serializers
from users.models import User
from jobs.models import Job
from applications.models import Application
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
# ----------------------------------------
# USER SERIALIZER (one per model)
# ----------------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "is_active", "date_joined"]
        read_only_fields = ["id", "email", "role", "is_active", "date_joined"]


# ----------------------------------------
# JOB SERIALIZER (one per model)
# ----------------------------------------
class JobSerializer(serializers.ModelSerializer):
    salary_display = serializers.CharField(source="get_salary_display", read_only=True)
    posted_label = serializers.CharField(source="get_posted_label", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "title", "slug", "description",
            "required_skills", "jd_keywords",
            "min_experience", "max_experience",
            "salary_type", "min_salary", "max_salary",
            "salary_display", "posted_label",
            "location", "work_mode", "employment_type",
            "required_education", "vacancies", "deadline",
            "is_deleted",
            "created_by", "created_at",
        ]
        read_only_fields = ["id", "slug", "created_by", "created_at", "salary_display", "posted_label"]


# ----------------------------------------
# APPLICATION SERIALIZER (one per model)
# ----------------------------------------
class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = Application
        fields = "__all__"


# ----------------------------------------
# PUBLIC APPLICATION SERIALIZER
# ----------------------------------------
class PublicApplicationSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(required=True)

    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "resume"]

    def validate_full_name(self, value):
        name = value.strip()

        if len(name) < 3:
            raise serializers.ValidationError(
                "Full name must be at least 3 characters."
            )

        if not re.match(r"^[A-Za-z\s.]+$", name):
            raise serializers.ValidationError(
                "Name can contain only letters and spaces."
            )

        return name

    def validate_email(self, value):
        email = value.strip().lower()

        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError(
                "Enter a valid email address."
            )

        return email

    def validate_phone(self, value):
        raw = value.strip()

        if raw.startswith("+"):
            cleaned = "+" + re.sub(r"\D", "", raw[1:])
        else:
            cleaned = re.sub(r"\D", "", raw)

        digits_only = re.sub(r"\D", "", cleaned)

        if len(digits_only) < 7 or len(digits_only) > 15:
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

        return cleaned