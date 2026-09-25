"""
Interview model module: manages interview schedules, modes, and evaluation outcomes.
"""

from django.db import models
from .application import Application


class InterviewStatus(models.TextChoices):
    """
    Status choices representing interview evaluation outcomes.
    """
    SCHEDULED = "SCHEDULED", "Scheduled"
    CLEARED = "CLEARED", "Cleared"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class Interview(models.Model):
    """
    Represents an evaluation round scheduled for a shortlisted candidate.

    Attributes:
        application: Associated Application record for the candidate.
        interview_date: Scheduled date and time for the interview evaluation.
        mode: Meeting delivery format (e.g. 'Online' or 'In-Person').
        status: Outcome status (SCHEDULED, CLEARED, FAILED, or CANCELLED).
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews"
    )
    interview_date = models.DateTimeField()
    mode = models.CharField(max_length=50, default="Online")
    status = models.CharField(
        max_length=30,
        choices=InterviewStatus.choices,
        default=InterviewStatus.SCHEDULED
    )

    def __str__(self):
        return f"Interview - {self.application.student.name} ({self.status})"