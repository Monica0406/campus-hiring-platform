"""
Authentication serializers for registration, login, and profile summary.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from hiring.models import Student, Company


class StudentRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    college = serializers.CharField(max_length=100, required=True)
    department = serializers.CharField(max_length=100, required=True)
    cgpa = serializers.DecimalField(max_digits=3, decimal_places=2, required=True)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists() or Student.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email


class CompanyRegisterSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    location = serializers.CharField(max_length=100, required=True)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists() or Company.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
