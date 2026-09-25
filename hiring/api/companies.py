"""
Company API views for managing company profile.
"""

from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from hiring.core.response import api_response
from hiring.core.exceptions import format_error_detail
from hiring.schemas.company import CompanySerializer, CompanyProfileUpdateSerializer
from .permissions import IsCompany


class CompanyProfileView(APIView):
    """
    GET /api/companies/profile/
    PATCH /api/companies/profile/
    Allows an authenticated company to view or update its profile.
    """
    permission_classes = [IsCompany]

    @extend_schema(
        tags=["Companies"],
        summary="Retrieve authenticated company profile",
        responses={
            200: CompanySerializer,
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Company role required."),
        },
    )
    def get(self, request):
        company = request.user.company_profile
        serializer = CompanySerializer(company)
        return api_response(
            success=True,
            data=serializer.data,
            message="Company profile retrieved successfully.",
        )

    @extend_schema(
        tags=["Companies"],
        summary="Update authenticated company profile",
        request=CompanyProfileUpdateSerializer,
        responses={
            200: CompanySerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Company role required."),
        },
    )
    def patch(self, request):
        company = request.user.company_profile
        serializer = CompanyProfileUpdateSerializer(
            company,
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
            data=CompanySerializer(company).data,
            message="Company profile updated successfully.",
        )
