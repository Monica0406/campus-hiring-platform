from django.db import models
from .application import Application


class Interview(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews"
    )
    interview_date = models.DateTimeField()
    mode = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="Scheduled")

    def __str__(self):
        return f"Interview - {self.application.student.name}"