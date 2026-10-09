"""
Health check API endpoint.
"""

from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from hiring.core.response import api_response


class HealthCheckView(APIView):
    """
    GET /api/health/
    Returns service health status and database connectivity.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Health"],
        summary="Service health and database connectivity check",
        responses={
            200: OpenApiResponse(description="API service is operational and database connected."),
            503: OpenApiResponse(description="Service unavailable: database connectivity check failed."),
        },
    )
    def get(self, request):
        is_healthy = True
        db_status = "connected"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as exc:
            is_healthy = False
            db_status = f"unhealthy ({str(exc)})"

        health_data = {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "Campus Hiring Platform API",
            "database": db_status,
        }

        if not is_healthy:
            return Response(
                {
                    "success": False,
                    "data": health_data,
                    "message": "Service is unavailable: database check failed.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return api_response(
            success=True,
            data=health_data,
            message="Service is operational.",
            status_code=status.HTTP_200_OK,
        )
