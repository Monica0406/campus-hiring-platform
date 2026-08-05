from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    college = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.name
class Company(models.Model):
    company_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name