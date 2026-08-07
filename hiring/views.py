from django.shortcuts import render, redirect
from .models import Student, Company

def home(request):
    return render(request, "home.html")


def student_register(request):
    if request.method == "POST":
        Student.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            password=request.POST["password"],
            college=request.POST["college"],
            department=request.POST["department"],
            cgpa=request.POST["cgpa"]
        )
        return redirect("/")

    return render(request, "student_register.html")


def student_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            student = Student.objects.get(
                email=email,
                password=password
            )

            return render(
                request,
                "student_dashboard.html",
                {"student": student}
            )

        except Student.DoesNotExist:
            return render(
                request,
                "student_login.html",
                {"error": "Invalid Email or Password"}
            )

    return render(request, "student_login.html")

    return render(request, "student_login.html")
def company_register(request):
    if request.method == "POST":
        Company.objects.create(
            company_name=request.POST["company_name"],
            email=request.POST["email"],
            password=request.POST["password"],
            location=request.POST["location"]
        )
        return redirect("/")

    return render(request, "company_register.html")
def company_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            Company.objects.get(email=email, password=password)
            return render(request, "company_dashboard.html")
        except Company.DoesNotExist:
            return render(request, "company_login.html", {"error": "Invalid Email or Password"})

    return render(request, "company_login.html")