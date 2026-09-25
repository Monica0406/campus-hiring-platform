"""
Unit tests for hiring/services/drive_service.py
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from hiring.models import Company, Drive
from hiring.services import drive_service


@pytest.fixture
def test_company(db):
    """Creates and returns a test company."""
    user = User.objects.create_user(
        username="drive_test_comp@example.com",
        email="drive_test_comp@example.com",
        password="password123",
    )
    return Company.objects.create(
        user=user,
        company_name="DriveTech Corp",
        email="drive_test_comp@example.com",
        password="hashed_pw",
        location="Seattle",
    )


@pytest.fixture
def other_company(db):
    """Creates and returns a second test company."""
    user = User.objects.create_user(
        username="other_comp@example.com",
        email="other_comp@example.com",
        password="password123",
    )
    return Company.objects.create(
        user=user,
        company_name="OtherCorp",
        email="other_comp@example.com",
        password="hashed_pw",
        location="Boston",
    )


@pytest.mark.django_db
def test_create_valid_drive(test_company):
    """Verify creating a drive with full parameters."""
    drive_date = date.today() + timedelta(days=14)
    drive = drive_service.create_drive(
        company=test_company,
        title="Full Stack Software Engineer",
        description="Develop modern web applications with Django and React.",
        drive_date=drive_date,
        min_cgpa=7.50,
        allowed_departments="CSE, IT",
        eligibility_notes="No active backlogs",
    )

    assert drive.id is not None
    assert drive.company == test_company
    assert drive.title == "Full Stack Software Engineer"
    assert drive.min_cgpa == Decimal("7.50")
    assert drive.allowed_departments == "CSE, IT"
    assert drive.eligibility == "No active backlogs"
    assert drive.is_active is True
    assert drive.drive_date == drive_date


@pytest.mark.django_db
def test_create_drive_defaults(test_company):
    """Verify creating a drive with default optional parameters."""
    drive_date = date.today() + timedelta(days=7)
    drive = drive_service.create_drive(
        company=test_company,
        title="General Hiring Drive",
        description="Open for all departments",
        drive_date=drive_date,
    )

    assert drive.min_cgpa == Decimal("0.0")
    assert drive.allowed_departments == "All"
    assert drive.eligibility == ""
    assert drive.is_active is True


@pytest.mark.django_db
def test_get_active_drives(test_company):
    """Verify retrieving only active drives ordered by drive_date."""
    today = date.today()
    d1 = drive_service.create_drive(
        company=test_company,
        title="Active Drive 1",
        description="Desc 1",
        drive_date=today + timedelta(days=10),
    )
    d2 = drive_service.create_drive(
        company=test_company,
        title="Active Drive 2",
        description="Desc 2",
        drive_date=today + timedelta(days=5),
    )
    # Create an inactive drive
    inactive_drive = Drive.objects.create(
        company=test_company,
        title="Inactive Drive",
        description="Closed",
        drive_date=today + timedelta(days=2),
        is_active=False,
    )

    active_drives = list(drive_service.get_active_drives())

    assert d1 in active_drives
    assert d2 in active_drives
    assert inactive_drive not in active_drives
    # d2 should appear before d1 because drive_date is earlier
    assert active_drives.index(d2) < active_drives.index(d1)


@pytest.mark.django_db
def test_get_company_drives(test_company, other_company):
    """Verify retrieving drives scoped to a specific company."""
    today = date.today()
    c1_drive = drive_service.create_drive(
        company=test_company,
        title="Test Company Drive",
        description="Desc",
        drive_date=today + timedelta(days=10),
    )
    c2_drive = drive_service.create_drive(
        company=other_company,
        title="Other Company Drive",
        description="Desc",
        drive_date=today + timedelta(days=10),
    )

    company_drives = list(drive_service.get_company_drives(test_company))

    assert c1_drive in company_drives
    assert c2_drive not in company_drives


@pytest.mark.django_db
def test_get_drive_by_id(test_company):
    """Verify retrieving a drive by its primary key with company details."""
    drive = drive_service.create_drive(
        company=test_company,
        title="Lookup Drive",
        description="Test description",
        drive_date=date.today() + timedelta(days=15),
    )

    retrieved = drive_service.get_drive_by_id(drive.id)
    assert retrieved.id == drive.id
    assert retrieved.title == "Lookup Drive"
    assert retrieved.company.company_name == "DriveTech Corp"


@pytest.mark.django_db
def test_get_drive_by_id_not_found():
    """Verify Drive.DoesNotExist is raised when drive ID does not exist."""
    with pytest.raises(Drive.DoesNotExist):
        drive_service.get_drive_by_id(999999)
