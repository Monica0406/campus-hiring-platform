"""
Comprehensive API and Business Logic verification tests for Step 2.
"""

from datetime import date, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from hiring.models import (
    Student,
    Company,
    Drive,
    Application,
    ApplicationStatus,
    Interview,
    InterviewStatus,
    Offer,
    OfferStatus,
)
from hiring.services import (
    application_service,
    drive_service,
    hiring_workflow_service,
)
from hiring.services.exceptions import (
    EligibilityError,
    DuplicateApplicationError,
    WorkflowError,
)


class CampusHiringAPITests(APITestCase):
    """
    Test suite covering API endpoints, SimpleJWT authentication,
    role-based access control, and end-to-end recruitment lifecycle.
    """

    def setUp(self):
        self.client = APIClient()

        # Student test registration data
        self.student_data = {
            "name": "Jane Doe",
            "email": "jane@campus.edu",
            "password": "SecurePassword123!",
            "college": "Tech Institute",
            "department": "CSE",
            "cgpa": "8.75",
        }

        # Company test registration data
        self.company_data = {
            "company_name": "Apex Innovations",
            "email": "hiring@apex.com",
            "password": "CompanySecret123!",
            "location": "San Francisco",
        }

    # ============================================================
    # 1. Student Registration
    # ============================================================
    def test_01_student_registration_success(self):
        response = self.client.post(
            "/api/auth/register/student/",
            self.student_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertEqual(response.data["data"]["role"], "STUDENT")
        self.assertEqual(response.data["data"]["student"]["email"], "jane@campus.edu")
        self.assertNotIn("password", response.data["data"]["student"])

        # Check DB user
        user = User.objects.filter(email="jane@campus.edu").first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("SecurePassword123!"))
        self.assertTrue(user.password.startswith("bcrypt"))
        self.assertNotEqual(user.password, "SecurePassword123!")

    # ============================================================
    # 2. Company Registration
    # ============================================================
    def test_02_company_registration_success(self):
        response = self.client.post(
            "/api/auth/register/company/",
            self.company_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertEqual(response.data["data"]["role"], "COMPANY")
        self.assertEqual(response.data["data"]["company"]["company_name"], "Apex Innovations")
        self.assertNotIn("password", response.data["data"]["company"])

        # Check DB company user
        user = User.objects.filter(email="hiring@apex.com").first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("CompanySecret123!"))
        self.assertTrue(user.password.startswith("bcrypt"))
        self.assertNotEqual(user.password, "CompanySecret123!")

    # ============================================================
    # 3. Login returns JWT tokens
    # ============================================================
    def test_03_login_returns_jwt(self):
        # Register student first
        self.client.post("/api/auth/register/student/", self.student_data, format="json")

        login_response = self.client.post(
            "/api/auth/login/",
            {"email": "jane@campus.edu", "password": "SecurePassword123!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue(login_response.data["success"])
        self.assertIn("access", login_response.data["data"])
        self.assertIn("refresh", login_response.data["data"])
        self.assertEqual(login_response.data["data"]["role"], "STUDENT")

    # ============================================================
    # 4. Authenticated student can access profile
    # ============================================================
    def test_04_authenticated_student_can_access_profile(self):
        reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        access_token = reg.data["data"]["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get("/api/students/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Jane Doe")
        self.assertEqual(response.data["data"]["department"], "CSE")

        # PATCH profile
        patch_response = self.client.patch(
            "/api/students/profile/",
            {"name": "Jane Updated"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["data"]["name"], "Jane Updated")

    # ============================================================
    # 5. Unauthenticated protected endpoint returns 401
    # ============================================================
    def test_05_unauthenticated_protected_endpoint_returns_401(self):
        self.client.credentials()  # No token
        response = self.client.get("/api/students/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertIsNone(response.data["data"])

    # ============================================================
    # 6. Student cannot create a Drive (403)
    # ============================================================
    def test_06_student_cannot_create_drive(self):
        reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        access_token = reg.data["data"]["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        drive_payload = {
            "title": "Software Engineer Intern",
            "description": "Building next gen cloud apps",
            "drive_date": str(date.today() + timedelta(days=14)),
            "min_cgpa": "7.50",
            "allowed_departments": "CSE,IT",
        }
        response = self.client.post("/api/drives/", drive_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    # ============================================================
    # 7. Company can create a Drive (201)
    # ============================================================
    def test_07_company_can_create_drive(self):
        reg = self.client.post("/api/auth/register/company/", self.company_data, format="json")
        access_token = reg.data["data"]["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        drive_payload = {
            "title": "Backend Engineering Intern",
            "description": "Python, Django, distributed architectures",
            "drive_date": str(date.today() + timedelta(days=21)),
            "min_cgpa": "7.00",
            "allowed_departments": "CSE,IT,ECE",
        }
        response = self.client.post("/api/drives/", drive_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["title"], "Backend Engineering Intern")
        self.assertEqual(response.data["data"]["company_name"], "Apex Innovations")

    # ============================================================
    # 8. Student can view active Drives
    # ============================================================
    def test_08_student_can_view_active_drives(self):
        # Create company and drive
        comp_reg = self.client.post("/api/auth/register/company/", self.company_data, format="json")
        comp_token = comp_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {comp_token}")
        self.client.post(
            "/api/drives/",
            {
                "title": "Full Stack Drive",
                "description": "React + Django full stack drive",
                "drive_date": str(date.today() + timedelta(days=10)),
                "min_cgpa": "6.50",
            },
            format="json",
        )

        # Login as student
        stu_reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        stu_token = stu_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {stu_token}")

        response = self.client.get("/api/drives/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertGreaterEqual(len(response.data["data"]), 1)

    # ============================================================
    # 9. Student can apply to an eligible Drive
    # ============================================================
    def test_09_student_can_apply_to_eligible_drive(self):
        # Setup company and drive
        comp_reg = self.client.post("/api/auth/register/company/", self.company_data, format="json")
        comp_token = comp_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {comp_token}")
        drive_res = self.client.post(
            "/api/drives/",
            {
                "title": "Data Engineering Internship",
                "description": "Pipelines and Spark",
                "drive_date": str(date.today() + timedelta(days=15)),
                "min_cgpa": "8.00",
                "allowed_departments": "CSE,IT",
            },
            format="json",
        )
        drive_id = drive_res.data["data"]["id"]

        # Student with CGPA 8.75 and dept CSE applies
        stu_reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        stu_token = stu_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {stu_token}")

        apply_res = self.client.post(
            "/api/applications/",
            {"drive_id": drive_id},
            format="json",
        )
        self.assertEqual(apply_res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(apply_res.data["success"])
        self.assertEqual(apply_res.data["data"]["status"], ApplicationStatus.APPLIED)

    # ============================================================
    # 10. Duplicate application is rejected (400)
    # ============================================================
    def test_10_duplicate_application_is_rejected(self):
        # Setup company and drive
        comp_reg = self.client.post("/api/auth/register/company/", self.company_data, format="json")
        comp_token = comp_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {comp_token}")
        drive_res = self.client.post(
            "/api/drives/",
            {
                "title": "Systems Internship",
                "description": "Low-level C/Rust",
                "drive_date": str(date.today() + timedelta(days=12)),
                "min_cgpa": "7.00",
                "allowed_departments": "All",
            },
            format="json",
        )
        drive_id = drive_res.data["data"]["id"]

        # Student applies first time
        stu_reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        stu_token = stu_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {stu_token}")

        first_apply = self.client.post(
            "/api/applications/",
            {"drive_id": drive_id},
            format="json",
        )
        self.assertEqual(first_apply.status_code, status.HTTP_201_CREATED)

        # Attempt duplicate application
        second_apply = self.client.post(
            "/api/applications/",
            {"drive_id": drive_id},
            format="json",
        )
        self.assertEqual(second_apply.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(second_apply.data["success"])
        self.assertIn("already applied", second_apply.data["message"].lower())

    # ============================================================
    # 11. Ineligible student application rejection (CGPA & Department)
    # ============================================================
    def test_11_eligibility_rejections(self):
        # Company sets min_cgpa 9.00 and department ECE only
        comp_reg = self.client.post("/api/auth/register/company/", self.company_data, format="json")
        comp_token = comp_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {comp_token}")
        drive_res = self.client.post(
            "/api/drives/",
            {
                "title": "Hardware Intern",
                "description": "VLSI and FPGA",
                "drive_date": str(date.today() + timedelta(days=10)),
                "min_cgpa": "9.00",
                "allowed_departments": "ECE",
            },
            format="json",
        )
        drive_id = drive_res.data["data"]["id"]

        # Student has CGPA 8.75 and Dept CSE
        stu_reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        stu_token = stu_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {stu_token}")

        apply_res = self.client.post(
            "/api/applications/",
            {"drive_id": drive_id},
            format="json",
        )
        self.assertEqual(apply_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(apply_res.data["success"])
        self.assertIn("cgpa", apply_res.data["message"].lower())

    # ============================================================
    # 12. Full Recruitment Lifecycle: Shortlist -> Interview -> Offer -> Response
    # ============================================================
    def test_12_full_recruitment_workflow(self):
        # 1. Company creates drive
        comp_reg = self.client.post("/api/auth/register/company/", self.company_data, format="json")
        comp_token = comp_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {comp_token}")
        drive_res = self.client.post(
            "/api/drives/",
            {
                "title": "AI Research Intern",
                "description": "LLMs and Agents",
                "drive_date": str(date.today() + timedelta(days=20)),
                "min_cgpa": "8.00",
                "allowed_departments": "All",
            },
            format="json",
        )
        drive_id = drive_res.data["data"]["id"]

        # 2. Student applies
        stu_reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        stu_token = stu_reg.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {stu_token}")
        app_res = self.client.post("/api/applications/", {"drive_id": drive_id}, format="json")
        app_id = app_res.data["data"]["id"]
        self.assertEqual(app_res.data["data"]["status"], ApplicationStatus.APPLIED)

        # 3. Company shortlists candidate
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {comp_token}")
        shortlist_res = self.client.post(f"/api/applications/{app_id}/shortlist/", format="json")
        self.assertEqual(shortlist_res.status_code, status.HTTP_200_OK)
        self.assertEqual(shortlist_res.data["data"]["status"], ApplicationStatus.SHORTLISTED)

        # 4. Company schedules interview
        interview_time = (timezone.now() + timedelta(days=3)).isoformat()
        interview_res = self.client.post(
            "/api/interviews/",
            {
                "application_id": app_id,
                "interview_date": interview_time,
                "mode": "Google Meet",
            },
            format="json",
        )
        self.assertEqual(interview_res.status_code, status.HTTP_201_CREATED)
        interview_id = interview_res.data["data"]["id"]

        # 5. Company marks interview passed -> Application status moves to SELECTED
        result_res = self.client.patch(
            f"/api/interviews/{interview_id}/",
            {"passed": True},
            format="json",
        )
        self.assertEqual(result_res.status_code, status.HTTP_200_OK)
        self.assertEqual(result_res.data["data"]["status"], InterviewStatus.CLEARED)

        # Verify application status transitioned to SELECTED
        app_check = self.client.get(f"/api/applications/{app_id}/")
        self.assertEqual(app_check.data["data"]["status"], ApplicationStatus.SELECTED)

        # 6. Company generates job offer -> Application moves to OFFERED
        offer_res = self.client.post(
            "/api/offers/",
            {
                "application_id": app_id,
                "position": "Junior AI Engineer",
                "salary": "95000.00",
            },
            format="json",
        )
        self.assertEqual(offer_res.status_code, status.HTTP_201_CREATED)
        offer_id = offer_res.data["data"]["id"]
        self.assertEqual(offer_res.data["data"]["status"], OfferStatus.PENDING)

        # 7. Student accepts job offer
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {stu_token}")
        respond_res = self.client.post(
            f"/api/offers/{offer_id}/respond/",
            {"accept": True},
            format="json",
        )
        self.assertEqual(respond_res.status_code, status.HTTP_200_OK)
        self.assertEqual(respond_res.data["data"]["status"], OfferStatus.ACCEPTED)

    # ============================================================
    # 13. Role Boundaries: Company cannot apply, Student cannot schedule
    # ============================================================
    def test_13_role_boundary_enforcement(self):
        comp_reg = self.client.post("/api/auth/register/company/", self.company_data, format="json")
        comp_token = comp_reg.data["data"]["access"]

        stu_reg = self.client.post("/api/auth/register/student/", self.student_data, format="json")
        stu_token = stu_reg.data["data"]["access"]

        # Company attempts to apply as student
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {comp_token}")
        apply_attempt = self.client.post("/api/applications/", {"drive_id": 1}, format="json")
        self.assertEqual(apply_attempt.status_code, status.HTTP_403_FORBIDDEN)

        # Student attempts to schedule interview
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {stu_token}")
        interview_attempt = self.client.post(
            "/api/interviews/",
            {"application_id": 1, "interview_date": str(timezone.now())},
            format="json",
        )
        self.assertEqual(interview_attempt.status_code, status.HTTP_403_FORBIDDEN)

    # ============================================================
    # 14. Health Check Endpoint
    # ============================================================
    def test_14_health_check(self):
        self.client.credentials()  # Unauthenticated
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], "healthy")
