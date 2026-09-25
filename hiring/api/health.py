"""
Health check API endpoint.
"""

from django.db import connection
from rest_framework.views import APIView
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
        },
    )
    def get(self, request):
        db_status = "connected"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as exc:
            db_status = f"unhealthy ({str(exc)})"

        health_data = {
            "status": "healthy",
            "service": "Campus Hiring Platform API",
            "database": db_status,
        }

        return api_response(
            success=True,
            data=health_data,
            message="Service is operational.",
        )
