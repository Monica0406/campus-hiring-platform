"""
Offer model module: represents formal employment offers extended to candidates.
"""

from django.db import models
from .application import Application


class OfferStatus(models.TextChoices):
    """
    Status choices representing student responses to job offers.
    """
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"


class Offer(models.Model):
    """
    Represents a formal job or internship offer extended to a cleared candidate.

    Attributes:
        application: Associated Application record for the candidate.
        offer_date: Date on which the offer was issued.
        position: Job designation or title (e.g. Associate Software Engineer).
        salary: Annual CTC or internship stipend value in local currency.
        status: Decision status (PENDING, ACCEPTED, or REJECTED).
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="offers"
    )
    offer_date = models.DateField(auto_now_add=True)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=30,
        choices=OfferStatus.choices,
        default=OfferStatus.PENDING
    )

    def __str__(self):
        return f"Offer - {self.application.student.name} ({self.position} - {self.status})"