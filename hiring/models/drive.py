"""
Drive model module: defines campus placement drives, criteria, and schedules.
"""

from django.db import models
from .company import Company


class Drive(models.Model):
    """
    Represents an active or historical campus recruitment drive published by a company.

    Attributes:
        company: The corporate entity hosting and funding the placement drive.
        title: Position or placement campaign title (e.g. Graduate Software Engineer).
        description: Comprehensive job overview, technical stack, and responsibilities.
        min_cgpa: Minimum academic CGPA required for candidate eligibility (0.0 to 10.0).
        allowed_departments: Comma-separated list of eligible branches or 'All'.
        eligibility: Freeform textual eligibility rules or guidelines.
        drive_date: Date on which the placement drive commences or registration closes.
        is_active: Boolean flag indicating whether the drive is currently accepting submissions.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="drives"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    min_cgpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    allowed_departments = models.CharField(
        max_length=255,
        default="All",
        help_text="Comma-separated allowed departments (e.g. CSE, IT, ECE) or 'All'"
    )
    eligibility = models.TextField(blank=True, default="")
    drive_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.company_name} - {self.title}"