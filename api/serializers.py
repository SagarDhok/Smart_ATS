from rest_framework import serializers
from jobs.models import Job
from applications.models import Application

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id", "title", "slug", "description", "required_skills",
            "jd_keywords", "min_experience", "max_experience",
            "location", "employment_type", "work_mode",
            "status", "created_at"
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id", "full_name", "email", "phone",
            "match_score", "matched_skills", "missing_skills",
            "skill_score", "experience_score", "keyword_score",
            "status", "applied_at", "job"
        ]


class ResumeParseSerializer(serializers.Serializer):
    resume = serializers.FileField()
