from django.db import models
from .company import Company


class Drive(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="drives"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    eligibility = models.TextField()
    drive_date = models.DateField()

    def __str__(self):
        return self.title