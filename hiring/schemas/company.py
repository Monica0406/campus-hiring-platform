"""
Company serializers for serialization and profile updates.
"""

from rest_framework import serializers
from hiring.models import Company


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for Company details. Passwords are never exposed.
    """
    class Meta:
        model = Company
        fields = [
            "id",
            "company_name",
            "email",
            "location",
        ]
        read_only_fields = ["id", "email"]


class CompanyProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating company profile.
    """
    class Meta:
        model = Company
        fields = [
            "company_name",
            "location",
        ]
