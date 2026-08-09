from django.urls import path
from . import views


urlpatterns = [

    # Home
    path(
        "",
        views.home,
        name="home"
    ),

    # ---------------- STUDENT ----------------

    path(
        "student-register/",
        views.student_register,
        name="student_register"
    ),

    path(
        "student-login/",
        views.student_login,
        name="student_login"
    ),

    path(
        "student-dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "upload-resume/",
        views.upload_resume,
        name="upload_resume"
    ),

    # ---------------- COMPANY ----------------

    path(
        "company-register/",
        views.company_register,
        name="company_register"
    ),

    path(
        "company-login/",
        views.company_login,
        name="company_login"
    ),

    path(
        "company-dashboard/",
        views.company_dashboard,
        name="company_dashboard"
    ),
]