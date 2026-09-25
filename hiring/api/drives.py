"""
Drive API views for listing, creating, and managing placement drives.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from hiring.core.response import api_response
from hiring.core.exceptions import format_error_detail
from hiring.models import Drive
from hiring.services import drive_service
from hiring.schemas.drive import DriveSerializer, DriveCreateUpdateSerializer
from .permissions import IsCompany, IsDriveOwner


class DriveListCreateView(APIView):
    """
    GET /api/drives/ - List active drives (public/authenticated)
    POST /api/drives/ - Create drive (authenticated company only)
    """
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCompany()]
        return [AllowAny()]

    @extend_schema(
        tags=["Drives"],
        summary="List placement drives",
        description="Public/students can view active drives. Companies can view their own drives using ?mine=true.",
        parameters=[
            OpenApiParameter(
                name="mine",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="If true, returns only drives created by the authenticated company.",
                required=False,
            )
        ],
        responses={
            200: DriveSerializer(many=True),
        },
    )
    def get(self, request):
        if (
            request.user.is_authenticated
            and hasattr(request.user, "company_profile")
            and request.query_params.get("mine") == "true"
        ):
            drives = drive_service.get_company_drives(request.user.company_profile)
        else:
            drives = drive_service.get_active_drives()

        serializer = DriveSerializer(drives, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Drives retrieved successfully.",
        )

    @extend_schema(
        tags=["Drives"],
        summary="Create a new placement drive",
        request=DriveCreateUpdateSerializer,
        responses={
            201: DriveSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only companies can create drives."),
        },
    )
    def post(self, request):
        serializer = DriveCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        company = request.user.company_profile

        drive = drive_service.create_drive(
            company=company,
            title=data["title"],
            description=data["description"],
            drive_date=data["drive_date"],
            min_cgpa=data.get("min_cgpa", 0.0),
            allowed_departments=data.get("allowed_departments", "All"),
            eligibility_notes=data.get("eligibility", ""),
        )

        return api_response(
            success=True,
            data=DriveSerializer(drive).data,
            message="Drive created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class DriveDetailView(APIView):
    """
    GET /api/drives/{id}/ - Retrieve drive details
    PATCH /api/drives/{id}/ - Update drive (owning company only)
    DELETE /api/drives/{id}/ - Delete drive (owning company only)
    """
    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsCompany(), IsDriveOwner()]
        return [AllowAny()]

    @extend_schema(
        tags=["Drives"],
        summary="Retrieve drive details by ID",
        responses={
            200: DriveSerializer,
            404: OpenApiResponse(description="Drive not found."),
        },
    )
    def get(self, request, pk):
        drive = get_object_or_404(Drive, pk=pk)
        return api_response(
            success=True,
            data=DriveSerializer(drive).data,
            message="Drive details retrieved.",
        )

    @extend_schema(
        tags=["Drives"],
        summary="Update placement drive details",
        request=DriveCreateUpdateSerializer,
        responses={
            200: DriveSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only the owning company can update this drive."),
            404: OpenApiResponse(description="Drive not found."),
        },
    )
    def patch(self, request, pk):
        drive = get_object_or_404(Drive, pk=pk)
        self.check_object_permissions(request, drive)

        serializer = DriveCreateUpdateSerializer(drive, data=request.data, partial=True)
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
            data=DriveSerializer(drive).data,
            message="Drive updated successfully.",
        )

    @extend_schema(
        tags=["Drives"],
        summary="Delete placement drive",
        responses={
            200: OpenApiResponse(description="Drive deleted successfully."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only the owning company can delete this drive."),
            404: OpenApiResponse(description="Drive not found."),
        },
    )
    def delete(self, request, pk):
        drive = get_object_or_404(Drive, pk=pk)
        self.check_object_permissions(request, drive)

        drive.delete()
        return api_response(
            success=True,
            data=None,
            message="Drive deleted successfully.",
        )
