"""
Tests for authentication, registration, login, JWT handling, and bcrypt compliance.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.contrib.auth.hashers import identify_hasher, make_password
from hiring.models import Student, Company


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_payload():
    return {
        "name": "Sarah Connor",
        "email": "sarah@campus.edu",
        "password": "Password123!",
        "college": "Tech Institute",
        "department": "CSE",
        "cgpa": "8.90",
    }


@pytest.fixture
def company_payload():
    return {
        "company_name": "Cyberdyne Systems",
        "email": "hr@cyberdyne.com",
        "password": "Password123!",
        "location": "Sunnyvale",
    }


@pytest.mark.django_db
def test_student_registration(api_client, student_payload):
    """Verify student registration creates User + Student records, hashes with bcrypt, and returns JWT."""
    response = api_client.post("/api/auth/register/student/", student_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["success"] is True
    assert "access" in response.data["data"]
    assert "refresh" in response.data["data"]
    assert response.data["data"]["role"] == "STUDENT"

    # Password should never be exposed in response
    assert "password" not in response.data["data"]["student"]

    # Verify DB user and hashed password
    user = User.objects.filter(email=student_payload["email"]).first()
    assert user is not None
    # Verify bcrypt hashing
    assert user.password.startswith("bcrypt")
    assert identify_hasher(user.password).algorithm in ("bcrypt_sha256", "bcrypt")
    # Verify plaintext password is not stored
    assert user.password != student_payload["password"]
    assert student_payload["password"] not in user.password

    # Verify Student profile password hash
    assert hasattr(user, "student_profile")
    assert user.student_profile.password.startswith("bcrypt")
    assert user.student_profile.password != student_payload["password"]
    assert student_payload["password"] not in user.student_profile.password

    # Verify authentication
    assert user.check_password(student_payload["password"]) is True
    assert user.check_password("WrongPassword999!") is False
    assert user.student_profile.name == "Sarah Connor"


@pytest.mark.django_db
def test_company_registration(api_client, company_payload):
    """Verify company registration creates User + Company records, hashes with bcrypt, and returns JWT."""
    response = api_client.post("/api/auth/register/company/", company_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["success"] is True
    assert "access" in response.data["data"]
    assert "refresh" in response.data["data"]
    assert response.data["data"]["role"] == "COMPANY"

    # Password should never be exposed in response
    assert "password" not in response.data["data"]["company"]

    # Verify DB
    user = User.objects.filter(email=company_payload["email"]).first()
    assert user is not None
    # Verify bcrypt hashing
    assert user.password.startswith("bcrypt")
    assert identify_hasher(user.password).algorithm in ("bcrypt_sha256", "bcrypt")
    # Verify plaintext password is not stored
    assert user.password != company_payload["password"]
    assert company_payload["password"] not in user.password

    # Verify Company profile password hash
    assert hasattr(user, "company_profile")
    assert user.company_profile.password.startswith("bcrypt")
    assert user.company_profile.password != company_payload["password"]
    assert company_payload["password"] not in user.company_profile.password

    # Verify authentication
    assert user.check_password(company_payload["password"]) is True
    assert user.check_password("WrongPassword999!") is False
    assert user.company_profile.company_name == "Cyberdyne Systems"


@pytest.mark.django_db
def test_duplicate_email_registration_rejected(api_client, student_payload):
    """Verify attempting to register with an already registered email is rejected with 400."""
    res1 = api_client.post("/api/auth/register/student/", student_payload, format="json")
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = api_client.post("/api/auth/register/student/", student_payload, format="json")
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert res2.data["success"] is False
    assert res2.data["data"] is None
    assert "already exists" in res2.data["message"].lower()


@pytest.mark.django_db
def test_login_success(api_client, student_payload):
    """Verify login with correct credentials returns JWT tokens and role."""
    api_client.post("/api/auth/register/student/", student_payload, format="json")

    login_res = api_client.post(
        "/api/auth/login/",
        {"email": student_payload["email"], "password": student_payload["password"]},
        format="json",
    )

    assert login_res.status_code == status.HTTP_200_OK
    assert login_res.data["success"] is True
    assert "access" in login_res.data["data"]
    assert "refresh" in login_res.data["data"]
    assert login_res.data["data"]["role"] == "STUDENT"


@pytest.mark.django_db
def test_login_wrong_password_rejected(api_client, student_payload):
    """Verify login with incorrect password returns 400."""
    api_client.post("/api/auth/register/student/", student_payload, format="json")

    login_res = api_client.post(
        "/api/auth/login/",
        {"email": student_payload["email"], "password": "WrongPassword999!"},
        format="json",
    )

    assert login_res.status_code == status.HTTP_400_BAD_REQUEST
    assert login_res.data["success"] is False
    assert login_res.data["data"] is None
    assert "invalid email or password" in login_res.data["message"].lower()


@pytest.mark.django_db
def test_jwt_authentication_me(api_client, student_payload):
    """Verify accessing /api/auth/me/ with Bearer token returns current user data."""
    reg_res = api_client.post("/api/auth/register/student/", student_payload, format="json")
    access_token = reg_res.data["data"]["access"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    me_res = api_client.get("/api/auth/me/")

    assert me_res.status_code == status.HTTP_200_OK
    assert me_res.data["success"] is True
    assert me_res.data["data"]["email"] == student_payload["email"]
    assert me_res.data["data"]["role"] == "STUDENT"
    # Verify password is not in me response
    assert "password" not in me_res.data["data"]
    assert "password" not in me_res.data["data"]["profile"]


@pytest.mark.django_db
def test_token_refresh(api_client, student_payload):
    """Verify refreshing access token using valid refresh token."""
    reg_res = api_client.post("/api/auth/register/student/", student_payload, format="json")
    refresh_token = reg_res.data["data"]["refresh"]

    refresh_res = api_client.post(
        "/api/auth/refresh/",
        {"refresh": refresh_token},
        format="json",
    )

    assert refresh_res.status_code == status.HTTP_200_OK
    assert refresh_res.data["success"] is True
    assert "access" in refresh_res.data["data"]


@pytest.mark.django_db
def test_bcrypt_password_security_guarantees(api_client, student_payload, company_payload):
    """
    Explicitly test all Capstone security requirements:
    1. Newly created passwords use bcrypt hasher.
    2. Plaintext password is never stored in DB.
    3. Password hash is never exposed in any API response.
    4. Correct password authenticates successfully.
    5. Incorrect password is rejected.
    6. JWT tokens function correctly for protected endpoints.
    """
    # 1. Student Registration
    res = api_client.post("/api/auth/register/student/", student_payload, format="json")
    assert res.status_code == status.HTTP_201_CREATED
    assert "password" not in str(res.data)

    user = User.objects.get(email=student_payload["email"])
    hasher = identify_hasher(user.password)
    assert hasher.algorithm in ("bcrypt_sha256", "bcrypt")
    assert user.password.startswith("bcrypt")
    assert user.password != student_payload["password"]
    assert student_payload["password"] not in user.password

    # 2. Login with correct bcrypt password
    login_res = api_client.post(
        "/api/auth/login/",
        {"email": student_payload["email"], "password": student_payload["password"]},
        format="json",
    )
    assert login_res.status_code == status.HTTP_200_OK
    assert "password" not in str(login_res.data)
    token = login_res.data["data"]["access"]

    # 3. Access protected endpoint with JWT
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    me_res = api_client.get("/api/auth/me/")
    assert me_res.status_code == status.HTTP_200_OK
    assert "password" not in str(me_res.data)
    api_client.credentials()

    # 4. Login rejection with incorrect password
    bad_login = api_client.post(
        "/api/auth/login/",
        {"email": student_payload["email"], "password": "IncorrectPassword99!"},
        format="json",
    )
    assert bad_login.status_code == status.HTTP_400_BAD_REQUEST

    # 5. Company Registration with bcrypt
    comp_res = api_client.post("/api/auth/register/company/", company_payload, format="json")
    assert comp_res.status_code == status.HTTP_201_CREATED
    assert "password" not in str(comp_res.data)

    comp_user = User.objects.get(email=company_payload["email"])
    comp_hasher = identify_hasher(comp_user.password)
    assert comp_hasher.algorithm in ("bcrypt_sha256", "bcrypt")
    assert comp_user.password.startswith("bcrypt")
    assert comp_user.password != company_payload["password"]
    assert company_payload["password"] not in comp_user.password


@pytest.mark.django_db
def test_backwards_compatibility_with_pbkdf2():
    """Verify that existing PBKDF2 password hashes can still be authenticated by Django."""
    raw_password = "LegacyUserPassword123!"
    pbkdf2_hash = make_password(raw_password, hasher="pbkdf2_sha256")
    assert pbkdf2_hash.startswith("pbkdf2_sha256$")

    user = User.objects.create(
        username="legacy@campus.edu",
        email="legacy@campus.edu",
        password=pbkdf2_hash,
    )

    assert user.check_password(raw_password) is True
    assert user.check_password("WrongPassword") is False
