"""
Tests for role-based permissions and access control.
"""

import pytest
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from hiring.models import Drive


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_auth(api_client, db):
    """Registers and authenticates a student, returning the access token and data."""
    payload = {
        "name": "Perm Student",
        "email": "perm_stu@campus.edu",
        "password": "Password123!",
        "college": "Tech College",
        "department": "CSE",
        "cgpa": "8.50",
    }
    res = api_client.post("/api/auth/register/student/", payload, format="json")
    return {
        "token": res.data["data"]["access"],
        "student": res.data["data"]["student"],
    }


@pytest.fixture
def other_student_auth(api_client, db):
    """Registers and authenticates a second student."""
    payload = {
        "name": "Other Student",
        "email": "other_stu@campus.edu",
        "password": "Password123!",
        "college": "Tech College",
        "department": "IT",
        "cgpa": "8.20",
    }
    res = api_client.post("/api/auth/register/student/", payload, format="json")
    return {
        "token": res.data["data"]["access"],
        "student": res.data["data"]["student"],
    }


@pytest.fixture
def company_auth(api_client, db):
    """Registers and authenticates a company."""
    payload = {
        "company_name": "Alpha Corp",
        "email": "alpha@corp.com",
        "password": "Password123!",
        "location": "New York",
    }
    res = api_client.post("/api/auth/register/company/", payload, format="json")
    return {
        "token": res.data["data"]["access"],
        "company": res.data["data"]["company"],
    }


@pytest.fixture
def other_company_auth(api_client, db):
    """Registers and authenticates a second company."""
    payload = {
        "company_name": "Beta Corp",
        "email": "beta@corp.com",
        "password": "Password123!",
        "location": "Chicago",
    }
    res = api_client.post("/api/auth/register/company/", payload, format="json")
    return {
        "token": res.data["data"]["access"],
        "company": res.data["data"]["company"],
    }


@pytest.mark.django_db
def test_unauthenticated_cannot_access_protected_endpoints(api_client):
    """Verify unauthenticated requests to protected endpoints return 401."""
    api_client.credentials()  # No token

    # Protected student profile
    res1 = api_client.get("/api/students/profile/")
    assert res1.status_code == status.HTTP_401_UNAUTHORIZED
    assert res1.data["success"] is False
    assert res1.data["data"] is None

    # Protected company profile
    res2 = api_client.get("/api/companies/profile/")
    assert res2.status_code == status.HTTP_401_UNAUTHORIZED

    # Protected auth me
    res3 = api_client.get("/api/auth/me/")
    assert res3.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_student_cannot_create_update_delete_drives(api_client, student_auth, company_auth):
    """Verify students receive HTTP 403 when attempting drive creation, updates, or deletion."""
    # Company creates a drive first
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {company_auth['token']}")
    drive_res = api_client.post(
        "/api/drives/",
        {
            "title": "Engineer Intern",
            "description": "Backend",
            "drive_date": str(date.today() + timedelta(days=10)),
        },
        format="json",
    )
    drive_id = drive_res.data["data"]["id"]

    # Student tries to create drive -> 403
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_auth['token']}")
    create_res = api_client.post(
        "/api/drives/",
        {
            "title": "Fake Drive",
            "description": "Hacked",
            "drive_date": str(date.today() + timedelta(days=10)),
        },
        format="json",
    )
    assert create_res.status_code == status.HTTP_403_FORBIDDEN

    # Student tries to update drive -> 403
    patch_res = api_client.patch(
        f"/api/drives/{drive_id}/",
        {"title": "Modified by Student"},
        format="json",
    )
    assert patch_res.status_code == status.HTTP_403_FORBIDDEN

    # Student tries to delete drive -> 403
    del_res = api_client.delete(f"/api/drives/{drive_id}/")
    assert del_res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_company_cannot_apply_as_student(api_client, company_auth):
    """Verify authenticated companies cannot submit applications to drives (HTTP 403)."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {company_auth['token']}")
    drive_res = api_client.post(
        "/api/drives/",
        {
            "title": "Dev Drive",
            "description": "Desc",
            "drive_date": str(date.today() + timedelta(days=10)),
        },
        format="json",
    )
    drive_id = drive_res.data["data"]["id"]

    # Company attempts to apply
    apply_res = api_client.post("/api/applications/", {"drive_id": drive_id}, format="json")
    assert apply_res.status_code == status.HTTP_403_FORBIDDEN
    assert "only registered students" in apply_res.data["message"].lower()


@pytest.mark.django_db
def test_student_cannot_schedule_interviews(api_client, student_auth):
    """Verify students cannot call interview scheduling endpoint (HTTP 403)."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_auth['token']}")
    res = api_client.post(
        "/api/interviews/",
        {"application_id": 1, "interview_date": str(date.today())},
        format="json",
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_company_cannot_modify_other_company_drives(api_client, company_auth, other_company_auth):
    """Verify a company cannot update or delete drives created by another company (HTTP 403)."""
    # Company 1 creates a drive
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {company_auth['token']}")
    drive_res = api_client.post(
        "/api/drives/",
        {
            "title": "Alpha Drive",
            "description": "Alpha desc",
            "drive_date": str(date.today() + timedelta(days=10)),
        },
        format="json",
    )
    drive_id = drive_res.data["data"]["id"]

    # Company 2 attempts to patch Company 1's drive
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_company_auth['token']}")
    patch_res = api_client.patch(
        f"/api/drives/{drive_id}/",
        {"title": "Hijacked Drive"},
        format="json",
    )
    assert patch_res.status_code == status.HTTP_403_FORBIDDEN

    # Company 2 attempts to delete Company 1's drive
    del_res = api_client.delete(f"/api/drives/{drive_id}/")
    assert del_res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_student_cannot_access_other_students_applications(
    api_client,
    company_auth,
    student_auth,
    other_student_auth,
):
    """Verify a student receives HTTP 403 when trying to access another student's application."""
    # Create drive
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {company_auth['token']}")
    drive_res = api_client.post(
        "/api/drives/",
        {
            "title": "Drive for Apps",
            "description": "Desc",
            "drive_date": str(date.today() + timedelta(days=10)),
        },
        format="json",
    )
    drive_id = drive_res.data["data"]["id"]

    # Student 1 applies
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_auth['token']}")
    app_res = api_client.post("/api/applications/", {"drive_id": drive_id}, format="json")
    app_id = app_res.data["data"]["id"]

    # Student 2 tries to view Student 1's application
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_student_auth['token']}")
    view_res = api_client.get(f"/api/applications/{app_id}/")
    assert view_res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_student_cannot_respond_to_other_students_offers(
    api_client,
    company_auth,
    student_auth,
    other_student_auth,
):
    """Verify a student receives HTTP 403 when trying to accept/reject another student's offer."""
    # 1. Company creates drive
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {company_auth['token']}")
    drive_res = api_client.post(
        "/api/drives/",
        {
            "title": "Offer Drive",
            "description": "Desc",
            "drive_date": str(date.today() + timedelta(days=10)),
        },
        format="json",
    )
    drive_id = drive_res.data["data"]["id"]

    # 2. Student 1 applies
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_auth['token']}")
    app_res = api_client.post("/api/applications/", {"drive_id": drive_id}, format="json")
    app_id = app_res.data["data"]["id"]

    # 3. Company shortlists, schedules, clears, and offers
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {company_auth['token']}")
    api_client.post(f"/api/applications/{app_id}/shortlist/")
    int_res = api_client.post(
        "/api/interviews/",
        {"application_id": app_id, "interview_date": str(date.today() + timedelta(days=1))},
        format="json",
    )
    int_id = int_res.data["data"]["id"]
    api_client.patch(f"/api/interviews/{int_id}/", {"passed": True}, format="json")
    offer_res = api_client.post(
        "/api/offers/",
        {"application_id": app_id, "position": "Software Engineer", "salary": "75000.00"},
        format="json",
    )
    offer_id = offer_res.data["data"]["id"]

    # 4. Student 2 tries to accept Student 1's offer
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_student_auth['token']}")
    respond_res = api_client.post(f"/api/offers/{offer_id}/respond/", {"accept": True}, format="json")
    assert respond_res.status_code == status.HTTP_403_FORBIDDEN
    assert "only respond to your own offers" in respond_res.data["message"].lower()
