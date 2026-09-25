"""
Offer API views for generating offers, responding to offers, and viewing offers.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from hiring.core.response import api_response
from hiring.core.exceptions import format_error_detail
from hiring.models import Offer, Application
from hiring.services import hiring_workflow_service
from hiring.services.exceptions import WorkflowError
from hiring.schemas.offer import (
    OfferSerializer,
    OfferCreateSerializer,
    OfferRespondSerializer,
)
from .permissions import IsCompany, IsStudent


class OfferListCreateView(APIView):
    """
    GET /api/offers/ - View student's received offers or company's extended offers
    POST /api/offers/ - Generate an offer for a candidate (company only)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Offers"],
        summary="List offers",
        description="Students see offers made to them. Companies see offers extended for their placement drives.",
        responses={
            200: OfferSerializer(many=True),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Access denied."),
        },
    )
    def get(self, request):
        user = request.user
        if hasattr(user, "student_profile") and user.student_profile:
            offers = Offer.objects.filter(
                application__student=user.student_profile
            ).select_related(
                "application__student",
                "application__drive__company",
                "application__drive",
            ).order_by("-offer_date")
        elif hasattr(user, "company_profile") and user.company_profile:
            offers = Offer.objects.filter(
                application__drive__company=user.company_profile
            ).select_related(
                "application__student",
                "application__drive__company",
                "application__drive",
            ).order_by("-offer_date")
        else:
            return api_response(
                success=False,
                data=None,
                message="User has neither student nor company role.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = OfferSerializer(offers, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Offers retrieved successfully.",
        )

    @extend_schema(
        tags=["Offers"],
        summary="Generate a job offer",
        description="Generate an offer for a candidate with SELECTED status and cleared interview. Company only.",
        request=OfferCreateSerializer,
        responses={
            201: OfferSerializer,
            400: OpenApiResponse(description="Candidate has not cleared interview or invalid input."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only the owning company can extend offers."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def post(self, request):
        if not (hasattr(request.user, "company_profile") and request.user.company_profile):
            return api_response(
                success=False,
                data=None,
                message="Only registered companies can generate offers.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = OfferCreateSerializer(data=request.data)
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
                message="You can only generate offers for candidates in your company's drives.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            offer = hiring_workflow_service.create_offer(
                application=application,
                position=serializer.validated_data["position"],
                salary=serializer.validated_data["salary"],
            )
            return api_response(
                success=True,
                data=OfferSerializer(offer).data,
                message="Offer generated successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        except WorkflowError as err:
            return api_response(
                success=False,
                data=None,
                message=str(err),
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class OfferDetailView(APIView):
    """
    GET /api/offers/{id}/ - Retrieve a single offer detail
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Offers"],
        summary="Retrieve offer details by ID",
        responses={
            200: OfferSerializer,
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Access restricted to candidate or offering company."),
            404: OpenApiResponse(description="Offer not found."),
        },
    )
    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)
        user = request.user
        is_student = hasattr(user, "student_profile") and offer.application.student == user.student_profile
        is_company = hasattr(user, "company_profile") and offer.application.drive.company == user.company_profile

        if not (is_student or is_company):
            return api_response(
                success=False,
                data=None,
                message="You do not have permission to view this offer.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return api_response(
            success=True,
            data=OfferSerializer(offer).data,
            message="Offer details retrieved.",
        )


class OfferRespondView(APIView):
    """
    POST /api/offers/{id}/respond/
    Allows a student to accept or reject an offer.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        tags=["Offers"],
        summary="Accept or reject a job offer",
        description="Candidate responds to their pending offer with accept: true or false.",
        request=OfferRespondSerializer,
        responses={
            200: OfferSerializer,
            400: OpenApiResponse(description="Offer is not in PENDING state or invalid input."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="You can only respond to your own offers."),
            404: OpenApiResponse(description="Offer not found."),
        },
    )
    def post(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        if offer.application.student != request.user.student_profile:
            return api_response(
                success=False,
                data=None,
                message="You can only respond to your own offers.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = OfferRespondSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                data=None,
                message=format_error_detail(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        accept = serializer.validated_data["accept"]

        try:
            updated_offer = hiring_workflow_service.respond_to_offer(
                offer=offer,
                accept=accept,
            )
            action_text = "accepted" if accept else "rejected"
            return api_response(
                success=True,
                data=OfferSerializer(updated_offer).data,
                message=f"Offer successfully {action_text}.",
            )
        except WorkflowError as err:
            return api_response(
                success=False,
                data=None,
                message=str(err),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
