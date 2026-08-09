from django.db import models
from .application import Application


class Offer(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="offers"
    )
    offer_date = models.DateField(auto_now_add=True)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="Pending")

    def __str__(self):
        return f"Offer - {self.application.student.name}"