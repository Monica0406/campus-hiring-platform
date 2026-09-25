"""
Application serializers for student applications and company applicant review.
"""

from rest_framework import serializers
from hiring.models import Application
from .student import StudentSerializer
from .drive import DriveSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying Application information with embedded drive/student summaries.
    """
    student_name = serializers.CharField(source="student.name", read_only=True)
    student_email = serializers.CharField(source="student.email", read_only=True)
    student_department = serializers.CharField(source="student.department", read_only=True)
    student_cgpa = serializers.DecimalField(source="student.cgpa", max_digits=3, decimal_places=2, read_only=True)
    student_resume = serializers.FileField(source="student.resume", read_only=True)
    drive_title = serializers.CharField(source="drive.title", read_only=True)
    company_name = serializers.CharField(source="drive.company.company_name", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "student",
            "student_name",
            "student_email",
            "student_department",
            "student_cgpa",
            "student_resume",
            "drive",
            "drive_title",
            "company_name",
            "applied_date",
            "status",
        ]
        read_only_fields = [
            "id",
            "student",
            "student_name",
            "student_email",
            "student_department",
            "student_cgpa",
            "student_resume",
            "drive_title",
            "company_name",
            "applied_date",
            "status",
        ]


class ApplicationCreateSerializer(serializers.Serializer):
    """
    Input serializer for submitting an application to a drive.
    """
    drive_id = serializers.IntegerField(required=True)


class ApplicationRejectSerializer(serializers.Serializer):
    """
    Input serializer for rejecting an application with an optional reason.
    """
    reason = serializers.CharField(required=False, default="", allow_blank=True)
