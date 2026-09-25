"""
Application API views for submitting applications, listing, and workflow actions.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from hiring.core.response import api_response
from hiring.core.exceptions import format_error_detail
from hiring.models import Application, Drive
from hiring.services import application_service, hiring_workflow_service
from hiring.services.exceptions import (
    EligibilityError,
    DuplicateApplicationError,
    WorkflowError,
)
from hiring.schemas.application import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationRejectSerializer,
)
from .permissions import IsCompany, IsApplicationParticipant


class ApplicationListCreateView(APIView):
    """
    GET /api/applications/ - View student's applications or company's received applications
    POST /api/applications/ - Submit an application to a drive (student only)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Applications"],
        summary="List applications",
        description="Students receive their submitted applications. Companies receive applications to their drives.",
        parameters=[
            OpenApiParameter(
                name="drive",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Filter applications to a specific drive (company only).",
                required=False,
            )
        ],
        responses={
            200: ApplicationSerializer(many=True),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Access denied."),
        },
    )
    def get(self, request):
        user = request.user
        if hasattr(user, "student_profile") and user.student_profile:
            apps = application_service.get_student_applications(user.student_profile)
        elif hasattr(user, "company_profile") and user.company_profile:
            drive_id = request.query_params.get("drive")
            if drive_id:
                drive = get_object_or_404(Drive, pk=drive_id, company=user.company_profile)
                apps = application_service.get_drive_applications(drive)
            else:
                apps = Application.objects.filter(
                    drive__company=user.company_profile
                ).select_related("student", "drive", "drive__company").order_by("-applied_date")
        else:
            return api_response(
                success=False,
                data=None,
                message="User has neither student nor company role.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApplicationSerializer(apps, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Applications retrieved successfully.",
        )

    @extend_schema(
        tags=["Applications"],
        summary="Apply to a placement drive",
        description="Students can apply to active drives for which they meet CGPA and department criteria.",
        request=ApplicationCreateSerializer,
        responses={
            201: ApplicationSerializer,
            400: OpenApiResponse(description="Eligibility criteria not met or duplicate application."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only students can apply to drives."),
            404: OpenApiResponse(description="Drive not found."),
        },
    )
    def post(self, request):
        if not (hasattr(request.user, "student_profile") and request.user.student_profile):
            return api_response(
                success=False,
                data=None,
                message="Only registered students can apply to placement drives.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApplicationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        drive_id = serializer.validated_data["drive_id"]
        drive = get_object_or_404(Drive, pk=drive_id)

        try:
            application = application_service.apply_to_drive(
                student=request.user.student_profile,
                drive=drive,
            )
            return api_response(
                success=True,
                data=ApplicationSerializer(application).data,
                message="Application submitted successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        except (EligibilityError, DuplicateApplicationError) as err:
            return api_response(
                success=False,
                data=None,
                message=str(err),
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class ApplicationDetailView(APIView):
    """
    GET /api/applications/{id}/ - Retrieve a single application detail
    """
    permission_classes = [IsAuthenticated, IsApplicationParticipant]

    @extend_schema(
        tags=["Applications"],
        summary="Retrieve application details by ID",
        responses={
            200: ApplicationSerializer,
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Access restricted to applicant or hosting company."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def get(self, request, pk):
        app = get_object_or_404(Application, pk=pk)
        self.check_object_permissions(request, app)
        return api_response(
            success=True,
            data=ApplicationSerializer(app).data,
            message="Application details retrieved.",
        )


class ApplicationShortlistView(APIView):
    """
    POST /api/applications/{id}/shortlist/
    Moves application to SHORTLISTED (owning company only).
    """
    permission_classes = [IsAuthenticated, IsCompany]

    @extend_schema(
        tags=["Application Workflow"],
        summary="Shortlist an applicant",
        description="Transitions application status from APPLIED to SHORTLISTED. Only owning company allowed.",
        request=None,
        responses={
            200: ApplicationSerializer,
            400: OpenApiResponse(description="Invalid workflow transition."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only the owning company can shortlist candidates."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def post(self, request, pk):
        app = get_object_or_404(Application, pk=pk)
        if app.drive.company != request.user.company_profile:
            return api_response(
                success=False,
                data=None,
                message="You can only shortlist applicants for your own drives.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            updated_app = hiring_workflow_service.shortlist_application(app)
            return api_response(
                success=True,
                data=ApplicationSerializer(updated_app).data,
                message="Application shortlisted successfully.",
            )
        except WorkflowError as err:
            return api_response(
                success=False,
                data=None,
                message=str(err),
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class ApplicationRejectView(APIView):
    """
    POST /api/applications/{id}/reject/
    Rejects application (owning company only).
    """
    permission_classes = [IsAuthenticated, IsCompany]

    @extend_schema(
        tags=["Application Workflow"],
        summary="Reject an applicant",
        description="Transitions application status to REJECTED. Only owning company allowed.",
        request=ApplicationRejectSerializer,
        responses={
            200: ApplicationSerializer,
            400: OpenApiResponse(description="Cannot reject application in current status."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only the owning company can reject candidates."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def post(self, request, pk):
        app = get_object_or_404(Application, pk=pk)
        if app.drive.company != request.user.company_profile:
            return api_response(
                success=False,
                data=None,
                message="You can only reject applicants for your own drives.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        reason = request.data.get("reason", "")
        try:
            updated_app = hiring_workflow_service.reject_application(app, reason=reason)
            return api_response(
                success=True,
                data=ApplicationSerializer(updated_app).data,
                message="Application marked as rejected.",
            )
        except WorkflowError as err:
            return api_response(
                success=False,
                data=None,
                message=str(err),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
