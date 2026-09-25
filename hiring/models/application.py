"""
Application model module: represents candidate applications to placement drives.
"""

from django.db import models
from .student import Student
from .drive import Drive


class ApplicationStatus(models.TextChoices):
    """
    Recruitment workflow status choices representing lifecycle states.
    """
    APPLIED = "APPLIED", "Applied"
    SHORTLISTED = "SHORTLISTED", "Shortlisted"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED", "Interview Scheduled"
    SELECTED = "SELECTED", "Selected"
    OFFERED = "OFFERED", "Offered"
    REJECTED = "REJECTED", "Rejected"


class Application(models.Model):
    """
    Connects an eligible candidate to a specific placement drive.

    Enforces unique application constraint ensuring a student cannot submit multiple
    applications to the same recruitment drive.

    Attributes:
        student: The applying Student candidate.
        drive: The Drive targeted by the application.
        applied_date: Timestamp recording initial application submission.
        status: Current position of the application in the hiring lifecycle.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    drive = models.ForeignKey(
        Drive,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "drive"],
                name="unique_student_drive_application"
            )
        ]

    def __str__(self):
        return f"{self.student.name} - {self.drive.title} ({self.status})"