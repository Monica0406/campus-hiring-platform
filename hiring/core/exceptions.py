"""
Custom exception handler and error formatting helpers for Django REST Framework.
Ensures all error responses strictly follow:
{
    "success": false,
    "data": null,
    "message": "Clear error message"
}
"""

import logging
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied

logger = logging.getLogger("hiring")


def format_error_detail(detail) -> str:
    """
    Recursively extract a clear, human-readable string from DRF error details.
    """
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        if not detail:
            return "An error occurred."
        return format_error_detail(detail[0])
    if isinstance(detail, dict):
        messages = []
        for key, val in detail.items():
            formatted_val = format_error_detail(val)
            if key in ["detail", "non_field_errors"]:
                messages.append(formatted_val)
            else:
                messages.append(f"{key}: {formatted_val}")
        return "; ".join(messages) if messages else "Validation failed."
    return str(detail)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that enforces the standardized error envelope:
    {
        "success": false,
        "data": null,
        "message": "<clear error message>"
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        message = format_error_detail(response.data)

        # Ensure clear standard messages for auth issues if blank or default
        if response.status_code == status.HTTP_401_UNAUTHORIZED and not message:
            message = "Authentication credentials were not provided or are invalid."
        elif response.status_code == status.HTTP_403_FORBIDDEN and not message:
            message = "You do not have permission to perform this action."
        elif response.status_code == status.HTTP_404_NOT_FOUND and not message:
            message = "Requested resource not found."

        response.data = {
            "success": False,
            "data": None,
            "message": message,
        }
    else:
        # Unhandled exceptions (500)
        logger.exception("Unhandled API exception: %s", exc)

    return response
