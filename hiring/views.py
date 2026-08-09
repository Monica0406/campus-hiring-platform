from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

from .models import Student, Company


# ---------------- HOME ----------------

def home(request):
    return render(request, "home.html")


# ---------------- STUDENT ----------------

def student_register(request):
    if request.method == "POST":
        Student.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            password=make_password(request.POST["password"]),
            college=request.POST["college"],
            department=request.POST["department"],
            cgpa=request.POST["cgpa"]
        )

        return redirect("/student-login/")

    return render(request, "student_register.html")


def student_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        student = Student.objects.filter(email=email).first()

        if student and check_password(password, student.password):
            request.session["student_id"] = student.id
            return redirect("/student-dashboard/")

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
        Company.objects.create(
            company_name=request.POST["company_name"],
            email=request.POST["email"],
            password=make_password(request.POST["password"]),
            location=request.POST["location"]
        )

        return redirect("/company-login/")

    return render(request, "company_register.html")


def company_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        company = Company.objects.filter(email=email).first()

        if company and check_password(password, company.password):
            request.session["company_id"] = company.id
            return redirect("/company-dashboard/")

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