"""
Student serializers for serialization and profile updates.
"""

from rest_framework import serializers
from hiring.models import Student


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Student profile details. Passwords are never exposed.
    """
    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "email",
            "college",
            "department",
            "cgpa",
            "resume",
        ]
        read_only_fields = ["id", "email"]


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating student profile.
    """
    class Meta:
        model = Student
        fields = [
            "name",
            "college",
            "department",
            "cgpa",
            "resume",
        ]
