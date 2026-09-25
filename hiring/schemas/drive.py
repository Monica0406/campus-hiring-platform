"""
Drive serializers for creating, updating, and displaying placement drives.
"""

from rest_framework import serializers
from hiring.models import Drive


class DriveSerializer(serializers.ModelSerializer):
    """
    Serializer for Drive model.
    """
    company_name = serializers.CharField(source="company.company_name", read_only=True)
    company_id = serializers.IntegerField(source="company.id", read_only=True)

    class Meta:
        model = Drive
        fields = [
            "id",
            "company_id",
            "company_name",
            "title",
            "description",
            "min_cgpa",
            "allowed_departments",
            "eligibility",
            "drive_date",
            "is_active",
        ]
        read_only_fields = ["id", "company_id", "company_name"]


class DriveCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating placement drives.
    """
    class Meta:
        model = Drive
        fields = [
            "title",
            "description",
            "min_cgpa",
            "allowed_departments",
            "eligibility",
            "drive_date",
            "is_active",
        ]
        extra_kwargs = {
            "min_cgpa": {"required": False, "default": 0.0},
            "allowed_departments": {"required": False, "default": "All"},
            "eligibility": {"required": False, "default": ""},
            "is_active": {"required": False, "default": True},
        }
