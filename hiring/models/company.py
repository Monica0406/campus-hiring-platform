from django.db import models


class Company(models.Model):
    company_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name