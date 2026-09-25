"""
Standardized API response helpers for REST endpoints.
"""

from rest_framework.response import Response
from rest_framework import status


def api_response(
    success: bool = True,
    data=None,
    message: str = "",
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """
    Provides a uniform JSON response structure across all REST APIs:
    Success:
    {
        "success": true,
        "data": { ... },
        "message": "..."
    }
    Error:
    {
        "success": false,
        "data": null,
        "message": "Clear error message"
    }
    """
    return Response(
        {
            "success": success,
            "data": data if success else None,
            "message": message,
        },
        status=status_code,
    )
