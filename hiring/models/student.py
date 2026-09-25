"""
Student model module: defines the academic profile and credentials of students.
"""

from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    """
    Represents an enrolled student candidate eligible for campus placement drives.

    Attributes:
        user: Associated Django auth User instance providing authentication credentials.
        name: Full legal name of the candidate.
        email: Unique institutional or personal contact email address.
        password: Password hash for fallback or credential references.
        college: University or affiliated engineering institute name.
        department: Major academic branch (e.g. CSE, IT, ECE, ME).
        cgpa: Cumulative Grade Point Average evaluated on a 10.0 scale.
        resume: FileField path storing the student's uploaded PDF resume document.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    college = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    def __str__(self):
        return self.name