"""
Student API views for managing student profile.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiResponse

from hiring.core.response import api_response
from hiring.core.exceptions import format_error_detail
from hiring.schemas.student import StudentSerializer, StudentProfileUpdateSerializer
from .permissions import IsStudent


class StudentProfileView(APIView):
    """
    GET /api/students/profile/
    PATCH /api/students/profile/
    Allows an authenticated student to retrieve or update their profile.
    """
    permission_classes = [IsStudent]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        tags=["Students"],
        summary="Retrieve authenticated student profile",
        responses={
            200: StudentSerializer,
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Student role required."),
        },
    )
    def get(self, request):
        student = request.user.student_profile
        serializer = StudentSerializer(student)
        return api_response(
            success=True,
            data=serializer.data,
            message="Student profile retrieved successfully.",
        )

    @extend_schema(
        tags=["Students"],
        summary="Update authenticated student profile",
        request=StudentProfileUpdateSerializer,
        responses={
            200: StudentSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Student role required."),
        },
    )
    def patch(self, request):
        student = request.user.student_profile
        serializer = StudentProfileUpdateSerializer(
            student,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return api_response(
            success=True,
            data=StudentSerializer(student).data,
            message="Profile updated successfully.",
        )
