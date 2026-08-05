from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('student-register/', views.student_register, name='student_register'),
    path('student-login/', views.student_login, name='student_login'),
    path('company-register/', views.company_register, name='company_register'),
    path('company-login/', views.company_login, name='company_login'),
]