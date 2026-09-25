"""
Unit tests for hiring/services/application_service.py
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from hiring.models import Student, Company, Drive, Application, ApplicationStatus
from hiring.services import application_service, drive_service
from hiring.services.exceptions import EligibilityError, DuplicateApplicationError


@pytest.fixture
def test_company(db):
    user = User.objects.create_user(
        username="app_test_comp@example.com",
        email="app_test_comp@example.com",
        password="password123",
    )
    return Company.objects.create(
        user=user,
        company_name="Cloud Corp",
        email="app_test_comp@example.com",
        password="hashed_pw",
        location="Austin",
    )


@pytest.fixture
def eligible_student(db):
    user = User.objects.create_user(
        username="eligible@campus.edu",
        email="eligible@campus.edu",
        password="password123",
    )
    return Student.objects.create(
        user=user,
        name="Alice Eligible",
        email="eligible@campus.edu",
        password="hashed_pw",
        college="Institute of Tech",
        department="CSE",
        cgpa=Decimal("8.50"),
    )


@pytest.fixture
def low_cgpa_student(db):
    user = User.objects.create_user(
        username="lowcgpa@campus.edu",
        email="lowcgpa@campus.edu",
        password="password123",
    )
    return Student.objects.create(
        user=user,
        name="Bob LowCGPA",
        email="lowcgpa@campus.edu",
        password="hashed_pw",
        college="Institute of Tech",
        department="CSE",
        cgpa=Decimal("6.20"),
    )


@pytest.fixture
def other_dept_student(db):
    user = User.objects.create_user(
        username="mech_stu@campus.edu",
        email="mech_stu@campus.edu",
        password="password123",
    )
    return Student.objects.create(
        user=user,
        name="Charlie Mech",
        email="mech_stu@campus.edu",
        password="hashed_pw",
        college="Institute of Tech",
        department="MECH",
        cgpa=Decimal("9.00"),
    )


@pytest.fixture
def standard_drive(test_company):
    return drive_service.create_drive(
        company=test_company,
        title="Software Internship",
        description="Core software roles",
        drive_date=date.today() + timedelta(days=20),
        min_cgpa=7.50,
        allowed_departments="CSE, IT",
    )


@pytest.mark.django_db
def test_eligible_student_can_apply(eligible_student, standard_drive):
    """Verify that an eligible student can successfully apply to an active drive."""
    application = application_service.apply_to_drive(
        student=eligible_student,
        drive=standard_drive,
    )

    assert application.id is not None
    assert application.student == eligible_student
    assert application.drive == standard_drive
    assert application.status == ApplicationStatus.APPLIED


@pytest.mark.django_db
def test_low_cgpa_rejected(low_cgpa_student, standard_drive):
    """Verify that a student with CGPA below min_cgpa is rejected with EligibilityError."""
    with pytest.raises(EligibilityError) as exc_info:
        application_service.apply_to_drive(
            student=low_cgpa_student,
            drive=standard_drive,
        )

    assert "Minimum CGPA required is 7.5" in str(exc_info.value)
    assert not Application.objects.filter(student=low_cgpa_student, drive=standard_drive).exists()


@pytest.mark.django_db
def test_wrong_department_rejected(other_dept_student, standard_drive):
    """Verify that a student with an excluded department is rejected with EligibilityError."""
    with pytest.raises(EligibilityError) as exc_info:
        application_service.apply_to_drive(
            student=other_dept_student,
            drive=standard_drive,
        )

    assert "Department 'MECH' is not eligible" in str(exc_info.value)
    assert not Application.objects.filter(student=other_dept_student, drive=standard_drive).exists()


@pytest.mark.django_db
def test_all_departments_allowed(other_dept_student, test_company):
    """Verify that when allowed_departments is 'All', students from any dept can apply."""
    open_drive = drive_service.create_drive(
        company=test_company,
        title="Open Drive",
        description="Any branch welcome",
        drive_date=date.today() + timedelta(days=10),
        min_cgpa=6.00,
        allowed_departments="All",
    )

    application = application_service.apply_to_drive(
        student=other_dept_student,
        drive=open_drive,
    )

    assert application.id is not None
    assert application.status == ApplicationStatus.APPLIED


@pytest.mark.django_db
def test_duplicate_application_rejected(eligible_student, standard_drive):
    """Verify that applying twice to the same drive raises DuplicateApplicationError."""
    # First application succeeds
    application_service.apply_to_drive(
        student=eligible_student,
        drive=standard_drive,
    )

    # Second application must fail
    with pytest.raises(DuplicateApplicationError) as exc_info:
        application_service.apply_to_drive(
            student=eligible_student,
            drive=standard_drive,
        )

    assert "already applied" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_inactive_drive_rejected(eligible_student, test_company):
    """Verify that applying to an inactive or closed drive raises EligibilityError."""
    inactive_drive = Drive.objects.create(
        company=test_company,
        title="Closed Drive",
        description="Already ended",
        drive_date=date.today() - timedelta(days=5),
        min_cgpa=Decimal("6.00"),
        allowed_departments="All",
        is_active=False,
    )

    with pytest.raises(EligibilityError) as exc_info:
        application_service.apply_to_drive(
            student=eligible_student,
            drive=inactive_drive,
        )

    assert "inactive or closed" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_student_applications_history(eligible_student, standard_drive, test_company):
    """Verify get_student_applications returns the student's submission history."""
    app1 = application_service.apply_to_drive(eligible_student, standard_drive)

    drive2 = drive_service.create_drive(
        company=test_company,
        title="Drive 2",
        description="Desc",
        drive_date=date.today() + timedelta(days=30),
        min_cgpa=7.00,
        allowed_departments="All",
    )
    app2 = application_service.apply_to_drive(eligible_student, drive2)

    history = list(application_service.get_student_applications(eligible_student))

    assert app1 in history
    assert app2 in history
    assert len(history) == 2


@pytest.mark.django_db
def test_drive_applications_list(eligible_student, standard_drive, db):
    """Verify get_drive_applications returns applications for a specific drive."""
    # Another eligible student
    user2 = User.objects.create_user(username="stu2@campus.edu", email="stu2@campus.edu", password="pw")
    student2 = Student.objects.create(
        user=user2,
        name="Student Two",
        email="stu2@campus.edu",
        password="hash",
        college="Tech",
        department="CSE",
        cgpa=Decimal("8.00"),
    )

    app1 = application_service.apply_to_drive(eligible_student, standard_drive)
    app2 = application_service.apply_to_drive(student2, standard_drive)

    drive_apps = list(application_service.get_drive_applications(standard_drive))

    assert app1 in drive_apps
    assert app2 in drive_apps
    assert len(drive_apps) == 2
