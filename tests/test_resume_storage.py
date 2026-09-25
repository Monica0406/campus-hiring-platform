"""
Tests for student resume upload functionality, file storage references, and clean media isolation.
"""

import os
import shutil
import tempfile
import pytest
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from hiring.models import Student


@pytest.fixture
def temp_media_root():
    """Create and tear down a temporary MEDIA_ROOT directory for test isolation."""
    temp_dir = tempfile.mkdtemp(prefix="test_media_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_student_client(db, api_client):
    """Creates a student, authenticates with JWT, and returns the client and student."""
    user = User.objects.create_user(
        username="student_resume_test@campus.edu",
        email="student_resume_test@campus.edu",
        password="ValidPassword123!",
    )
    student = Student.objects.create(
        user=user,
        name="Alex Mercer",
        email=user.email,
        college="Engineering College",
        department="CSE",
        cgpa="9.10",
    )

    # Login to get JWT
    login_res = api_client.post(
        "/api/auth/login/",
        {"email": user.email, "password": "ValidPassword123!"},
        format="json",
    )
    token = login_res.data["data"]["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client, student


@pytest.mark.django_db
def test_student_resume_upload_via_api(temp_media_root, authenticated_student_client):
    """
    Verify student can upload a PDF resume via PATCH /api/students/profile/.
    Verify DB stores file path string reference, NOT binary content.
    Verify uploaded file exists in the media/resumes/ directory hierarchy.
    """
    client, student = authenticated_student_client

    with override_settings(MEDIA_ROOT=temp_media_root):
        fake_pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        resume_file = SimpleUploadedFile(
            "my_resume.pdf",
            fake_pdf_content,
            content_type="application/pdf",
        )

        response = client.patch(
            "/api/students/profile/",
            {"resume": resume_file},
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

        # Refresh from DB
        student.refresh_from_db()
        assert student.resume is not None
        assert student.resume.name is not None

        # Verify DB stores path reference string, not binary
        resume_path_str = str(student.resume)
        assert resume_path_str.startswith("resumes/")
        assert resume_path_str.endswith(".pdf")
        assert isinstance(resume_path_str, str)
        assert resume_path_str != fake_pdf_content

        # Verify file is physically saved under media resumes/
        saved_file_full_path = os.path.join(temp_media_root, resume_path_str)
        assert os.path.exists(saved_file_full_path)
        with open(saved_file_full_path, "rb") as f:
            assert f.read() == fake_pdf_content


@pytest.mark.django_db
def test_student_resume_upload_via_template_view(temp_media_root, client):
    """
    Verify resume upload via the session-based /upload-resume/ endpoint.
    Verify file path reference is stored and physical file exists.
    """
    with override_settings(MEDIA_ROOT=temp_media_root):
        user = User.objects.create_user(
            username="student_tpl@campus.edu",
            email="student_tpl@campus.edu",
            password="ValidPassword123!",
        )
        student = Student.objects.create(
            user=user,
            name="Session Student",
            email=user.email,
            college="Engineering College",
            department="ECE",
            cgpa="8.50",
        )

        # Set session for view
        session = client.session
        session["student_id"] = student.id
        session.save()

        fake_pdf_content = b"%PDF-1.5 test resume document"
        resume_file = SimpleUploadedFile(
            "session_resume.pdf",
            fake_pdf_content,
            content_type="application/pdf",
        )

        response = client.post(
            "/upload-resume/",
            {"resume": resume_file},
        )

        assert response.status_code == status.HTTP_200_OK

        student.refresh_from_db()
        assert student.resume is not None
        assert str(student.resume).startswith("resumes/")
        assert str(student.resume).endswith(".pdf")

        # Verify saved on disk in temp MEDIA_ROOT
        saved_file_full_path = os.path.join(temp_media_root, str(student.resume))
        assert os.path.exists(saved_file_full_path)


@pytest.mark.django_db
def test_real_media_resumes_directory_not_polluted():
    """
    Verify that the repository's media/resumes/ directory remains clean
    and does not contain test residue or sample files.
    """
    from django.conf import settings
    real_resumes_dir = os.path.join(settings.MEDIA_ROOT, "resumes")
    if os.path.exists(real_resumes_dir):
        files = [f for f in os.listdir(real_resumes_dir) if f.endswith(".pdf")]
        assert len(files) == 0, f"Found unexpected PDF files in real media/resumes: {files}"
