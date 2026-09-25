"""
Interview API views for scheduling, updating results, and viewing scheduled interviews.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from hiring.core.response import api_response
from hiring.core.exceptions import format_error_detail
from hiring.models import Interview, Application
from hiring.services import hiring_workflow_service
from hiring.services.exceptions import WorkflowError
from hiring.schemas.interview import (
    InterviewSerializer,
    InterviewCreateSerializer,
    InterviewResultSerializer,
)
from .permissions import IsCompany, IsApplicationParticipant


class InterviewListCreateView(APIView):
    """
    GET /api/interviews/ - List student's or company's interviews
    POST /api/interviews/ - Schedule an interview (company only)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Interviews"],
        summary="List interviews",
        description="Students see their own scheduled interviews. Companies see interviews scheduled for their drives.",
        responses={
            200: InterviewSerializer(many=True),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Access denied."),
        },
    )
    def get(self, request):
        user = request.user
        if hasattr(user, "student_profile") and user.student_profile:
            interviews = Interview.objects.filter(
                application__student=user.student_profile
            ).select_related(
                "application__student",
                "application__drive__company",
                "application__drive",
            ).order_by("interview_date")
        elif hasattr(user, "company_profile") and user.company_profile:
            interviews = Interview.objects.filter(
                application__drive__company=user.company_profile
            ).select_related(
                "application__student",
                "application__drive__company",
                "application__drive",
            ).order_by("interview_date")
        else:
            return api_response(
                success=False,
                data=None,
                message="User has neither student nor company role.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = InterviewSerializer(interviews, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Interviews retrieved successfully.",
        )

    @extend_schema(
        tags=["Interviews"],
        summary="Schedule an interview",
        description="Schedule an interview for a SHORTLISTED applicant. Company only.",
        request=InterviewCreateSerializer,
        responses={
            201: InterviewSerializer,
            400: OpenApiResponse(description="Application is not in SHORTLISTED status or invalid input."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only the owning company can schedule interviews."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def post(self, request):
        if not (hasattr(request.user, "company_profile") and request.user.company_profile):
            return api_response(
                success=False,
                data=None,
                message="Only registered companies can schedule interviews.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = InterviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        app_id = serializer.validated_data["application_id"]
        application = get_object_or_404(Application, pk=app_id)

        if application.drive.company != request.user.company_profile:
            return api_response(
                success=False,
                data=None,
                message="You can only schedule interviews for your company's drives.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            interview = hiring_workflow_service.schedule_interview(
                application=application,
                interview_date=serializer.validated_data["interview_date"],
                mode=serializer.validated_data.get("mode", "Online"),
            )
            return api_response(
                success=True,
                data=InterviewSerializer(interview).data,
                message="Interview scheduled successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        except WorkflowError as err:
            return api_response(
                success=False,
                data=None,
                message=str(err),
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class InterviewDetailUpdateView(APIView):
    """
    GET /api/interviews/{id}/ - Retrieve interview details
    PATCH /api/interviews/{id}/ - Record result (passed: true/false) or update details (company only)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Interviews"],
        summary="Retrieve interview details by ID",
        responses={
            200: InterviewSerializer,
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Access denied."),
            404: OpenApiResponse(description="Interview not found."),
        },
    )
    def get(self, request, pk):
        interview = get_object_or_404(Interview, pk=pk)
        user = request.user
        is_student = hasattr(user, "student_profile") and interview.application.student == user.student_profile
        is_company = hasattr(user, "company_profile") and interview.application.drive.company == user.company_profile

        if not (is_student or is_company):
            return api_response(
                success=False,
                data=None,
                message="You do not have permission to view this interview.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return api_response(
            success=True,
            data=InterviewSerializer(interview).data,
            message="Interview details retrieved.",
        )

    @extend_schema(
        tags=["Interviews"],
        summary="Update interview or record pass/fail result",
        description="Company can record interview outcome (passed: true/false) which transitions candidate to SELECTED or REJECTED.",
        request=InterviewResultSerializer,
        responses={
            200: InterviewSerializer,
            400: OpenApiResponse(description="Invalid workflow transition or result."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only the owning company can manage this interview."),
            404: OpenApiResponse(description="Interview not found."),
        },
    )
    def patch(self, request, pk):
        if not (hasattr(request.user, "company_profile") and request.user.company_profile):
            return api_response(
                success=False,
                data=None,
                message="Only registered companies can update interviews.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        interview = get_object_or_404(Interview, pk=pk)
        if interview.application.drive.company != request.user.company_profile:
            return api_response(
                success=False,
                data=None,
                message="You can only manage interviews for your company's drives.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Record pass/fail result if provided
        if "passed" in request.data:
            passed = str(request.data["passed"]).lower() in ["true", "1", "yes"]
            try:
                updated_interview = hiring_workflow_service.record_interview_result(
                    interview=interview,
                    passed=passed,
                )
                return api_response(
                    success=True,
                    data=InterviewSerializer(updated_interview).data,
                    message="Interview result recorded successfully.",
                )
            except WorkflowError as err:
                return api_response(
                    success=False,
                    data=None,
                    message=str(err),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        # General field update (mode, date)
        if "mode" in request.data:
            interview.mode = str(request.data["mode"]).strip()
        if "interview_date" in request.data:
            interview.interview_date = request.data["interview_date"]
        interview.save()

        return api_response(
            success=True,
            data=InterviewSerializer(interview).data,
            message="Interview updated successfully.",
        )
