"""
Authentication views for Student and Company registration, login, and profile check.
"""

import logging
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from hiring.core.response import api_response
from hiring.core.exceptions import format_error_detail
from hiring.models import Student, Company
from hiring.schemas.auth import (
    StudentRegisterSerializer,
    CompanyRegisterSerializer,
    LoginSerializer,
)
from hiring.schemas.student import StudentSerializer
from hiring.schemas.company import CompanySerializer

logger = logging.getLogger("hiring")


class StudentRegisterView(APIView):
    """
    POST /api/auth/register/student/
    Registers a new student, generates JWT tokens, and returns profile info.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Register a new student account",
        request=StudentRegisterSerializer,
        responses={
            201: OpenApiResponse(description="Student registered successfully and JWT returned."),
            400: OpenApiResponse(description="Validation error or email already exists."),
        },
    )
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        email = data["email"].strip().lower()

        user = User.objects.create_user(
            username=email,
            email=email,
            password=data["password"],
        )

        student = Student.objects.create(
            user=user,
            name=data["name"].strip(),
            email=email,
            password=make_password(data["password"]),
            college=data["college"].strip(),
            department=data["department"].strip(),
            cgpa=data["cgpa"],
        )

        refresh = RefreshToken.for_user(user)
        logger.info("New student registered via API: id=%s, email=%s", student.id, student.email)

        return api_response(
            success=True,
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": "STUDENT",
                "student": StudentSerializer(student).data,
            },
            message="Student registered successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class CompanyRegisterView(APIView):
    """
    POST /api/auth/register/company/
    Registers a new company, generates JWT tokens, and returns company info.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Register a new company account",
        request=CompanyRegisterSerializer,
        responses={
            201: OpenApiResponse(description="Company registered successfully and JWT returned."),
            400: OpenApiResponse(description="Validation error or email already exists."),
        },
    )
    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        email = data["email"].strip().lower()

        user = User.objects.create_user(
            username=email,
            email=email,
            password=data["password"],
        )

        company = Company.objects.create(
            user=user,
            company_name=data["company_name"].strip(),
            email=email,
            password=make_password(data["password"]),
            location=data["location"].strip(),
        )

        refresh = RefreshToken.for_user(user)
        logger.info("New company registered via API: id=%s, company=%s", company.id, company.company_name)

        return api_response(
            success=True,
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": "COMPANY",
                "company": CompanySerializer(company).data,
            },
            message="Company registered successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Logs in either Student or Company and returns JWT tokens.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Login with email and password",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful with JWT access and refresh tokens."),
            400: OpenApiResponse(description="Invalid credentials or missing fields."),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            logger.warning("Failed API login attempt for email: %s", email)
            return api_response(
                success=False,
                data=None,
                message="Invalid email or password.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)

        role = "UNKNOWN"
        profile_data = {}

        if hasattr(user, "student_profile") and user.student_profile:
            role = "STUDENT"
            profile_data = StudentSerializer(user.student_profile).data
        elif hasattr(user, "company_profile") and user.company_profile:
            role = "COMPANY"
            profile_data = CompanySerializer(user.company_profile).data

        logger.info("Successful API login: user_id=%s, role=%s", user.id, role)

        return api_response(
            success=True,
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": role,
                "profile": profile_data,
            },
            message="Login successful.",
            status_code=status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    GET /api/auth/me/
    Returns the profile and role of the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Get current user identity and profile",
        responses={
            200: OpenApiResponse(description="User profile retrieved."),
            401: OpenApiResponse(description="Authentication required."),
        },
    )
    def get(self, request):
        user = request.user
        role = "UNKNOWN"
        profile = {}

        if hasattr(user, "student_profile") and user.student_profile:
            role = "STUDENT"
            profile = StudentSerializer(user.student_profile).data
        elif hasattr(user, "company_profile") and user.company_profile:
            role = "COMPANY"
            profile = CompanySerializer(user.company_profile).data

        return api_response(
            success=True,
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role,
                "profile": profile,
            },
            message="User profile retrieved.",
        )


class RefreshTokenView(TokenRefreshView):
    """
    POST /api/auth/refresh/
    Refreshes an access token using a valid refresh token.
    """
    @extend_schema(
        tags=["Authentication"],
        summary="Refresh JWT access token",
        responses={
            200: OpenApiResponse(description="New access token returned."),
            400: OpenApiResponse(description="Invalid refresh token."),
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return api_response(
                success=True,
                data=response.data,
                message="Access token refreshed successfully.",
            )
        return api_response(
            success=False,
            data=None,
            message=format_error_detail(response.data),
            status_code=response.status_code,
        )
