"""
Interview serializers for scheduling, updating, and viewing interviews.
"""

from rest_framework import serializers
from hiring.models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying interview details.
    """
    student_name = serializers.CharField(source="application.student.name", read_only=True)
    student_email = serializers.CharField(source="application.student.email", read_only=True)
    drive_title = serializers.CharField(source="application.drive.title", read_only=True)
    company_name = serializers.CharField(source="application.drive.company.company_name", read_only=True)

    class Meta:
        model = Interview
        fields = [
            "id",
            "application",
            "student_name",
            "student_email",
            "drive_title",
            "company_name",
            "interview_date",
            "mode",
            "status",
        ]
        read_only_fields = [
            "id",
            "application",
            "student_name",
            "student_email",
            "drive_title",
            "company_name",
            "status",
        ]


class InterviewCreateSerializer(serializers.Serializer):
    """
    Input serializer for scheduling an interview.
    """
    application_id = serializers.IntegerField(required=True)
    interview_date = serializers.DateTimeField(required=True)
    mode = serializers.CharField(max_length=50, default="Online", required=False)


class InterviewResultSerializer(serializers.Serializer):
    """
    Input serializer for recording interview results (passed or failed).
    """
    passed = serializers.BooleanField(required=True)
