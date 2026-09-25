import logging
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

from .models import Student, Company

logger = logging.getLogger("hiring")


# ---------------- HOME ----------------

def home(request):
    return render(request, "home.html")


# ---------------- STUDENT ----------------

def student_register(request):
    if request.method == "POST":
        email = request.POST["email"].strip().lower()

        if Student.objects.filter(email=email).exists():
            logger.warning("Student registration failed: email already exists: %s", email)
            return render(
                request,
                "student_register.html",
                {"error": "An account with this email already exists."}
            )

        student = Student.objects.create(
            name=request.POST["name"].strip(),
            email=email,
            password=make_password(request.POST["password"]),
            college=request.POST["college"].strip(),
            department=request.POST["department"].strip(),
            cgpa=request.POST["cgpa"]
        )
        logger.info("Student registered successfully: id=%s, email=%s", student.id, student.email)

        return redirect("/student-login/")

    return render(request, "student_register.html")


def student_login(request):
    if request.method == "POST":
        email = request.POST["email"].strip().lower()
        password = request.POST["password"]

        student = Student.objects.filter(email=email).first()

        if student and check_password(password, student.password):
            request.session["student_id"] = student.id
            logger.info("Student login successful: id=%s, email=%s", student.id, student.email)
            return redirect("/student-dashboard/")

        logger.warning("Student login failed for email: %s", email)
        return render(
            request,
            "student_login.html",
            {"error": "Invalid Email or Password"}
        )

    return render(request, "student_login.html")


def student_dashboard(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("/student-login/")

    student = Student.objects.get(id=student_id)

    return render(
        request,
        "student_dashboard.html",
        {"student": student}
    )


def upload_resume(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("/student-login/")

    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        resume = request.FILES.get("resume")

        if resume and resume.name.lower().endswith(".pdf"):
            student.resume = resume
            student.save()

            return render(
                request,
                "student_dashboard.html",
                {
                    "student": student,
                    "success": "Resume uploaded successfully!"
                }
            )

        return render(
            request,
            "student_dashboard.html",
            {
                "student": student,
                "error": "Please upload a PDF file."
            }
        )

    return redirect("/student-dashboard/")


# ---------------- COMPANY ----------------

def company_register(request):
    if request.method == "POST":
        email = request.POST["email"].strip().lower()

        if Company.objects.filter(email=email).exists():
            logger.warning("Company registration failed: email already exists: %s", email)
            return render(
                request,
                "company_register.html",
                {"error": "An account with this email already exists."}
            )

        company = Company.objects.create(
            company_name=request.POST["company_name"].strip(),
            email=email,
            password=make_password(request.POST["password"]),
            location=request.POST["location"].strip()
        )
        logger.info("Company registered successfully: id=%s, email=%s", company.id, company.email)

        return redirect("/company-login/")

    return render(request, "company_register.html")


def company_login(request):
    if request.method == "POST":
        email = request.POST["email"].strip().lower()
        password = request.POST["password"]

        company = Company.objects.filter(email=email).first()

        if company and check_password(password, company.password):
            request.session["company_id"] = company.id
            logger.info("Company login successful: id=%s, email=%s", company.id, company.email)
            return redirect("/company-dashboard/")

        logger.warning("Company login failed for email: %s", email)
        return render(
            request,
            "company_login.html",
            {"error": "Invalid Email or Password"}
        )

    return render(request, "company_login.html")


def company_dashboard(request):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("/company-login/")

    company = Company.objects.get(id=company_id)

    return render(
        request,
        "company_dashboard.html",
        {"company": company}
    )