"""
Company model module: defines corporate recruiter profiles and organization data.
"""

from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    """
    Represents an enterprise or corporate recruiter organization hosting placement drives.

    Attributes:
        user: Associated Django auth User instance providing authentication credentials.
        company_name: Name of the corporate organization or hiring entity.
        email: Unique corporate recruiter contact email address.
        password: Password hash for credential references.
        location: Primary corporate headquarters or office city location.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="company_profile",
        null=True,
        blank=True
    )
    company_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name