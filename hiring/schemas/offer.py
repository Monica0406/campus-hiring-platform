"""
Offer serializers for creating, updating, and viewing job offers.
"""

from decimal import Decimal
from rest_framework import serializers
from hiring.models import Offer


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying offer details.
    """
    student_name = serializers.CharField(source="application.student.name", read_only=True)
    student_email = serializers.CharField(source="application.student.email", read_only=True)
    drive_title = serializers.CharField(source="application.drive.title", read_only=True)
    company_name = serializers.CharField(source="application.drive.company.company_name", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "application",
            "student_name",
            "student_email",
            "drive_title",
            "company_name",
            "position",
            "salary",
            "offer_date",
            "status",
        ]
        read_only_fields = [
            "id",
            "application",
            "student_name",
            "student_email",
            "drive_title",
            "company_name",
            "offer_date",
            "status",
        ]


class OfferCreateSerializer(serializers.Serializer):
    """
    Input serializer for creating an offer.
    """
    application_id = serializers.IntegerField(required=True)
    position = serializers.CharField(max_length=100, min_length=1, allow_blank=False, trim_whitespace=True, required=True)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"), required=True)


class OfferRespondSerializer(serializers.Serializer):
    """
    Input serializer for a student accepting or rejecting an offer.
    """
    accept = serializers.BooleanField(required=True)
