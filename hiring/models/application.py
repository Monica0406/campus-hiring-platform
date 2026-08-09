from django.db import models
from .student import Student
from .drive import Drive


class Application(models.Model):
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
    status = models.CharField(max_length=50, default="Applied")

    def __str__(self):
        return f"{self.student.name} - {self.drive.title}"