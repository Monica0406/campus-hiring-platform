"""
Role-based and object-level permission classes for the hiring API.
"""

from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """
    Allows access only to authenticated users with a student profile.
    """
    message = "Only registered students can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "student_profile")
            and request.user.student_profile is not None
        )


class IsCompany(BasePermission):
    """
    Allows access only to authenticated users with a company profile.
    """
    message = "Only registered companies can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "company_profile")
            and request.user.company_profile is not None
        )


class IsDriveOwner(BasePermission):
    """
    Allows access only if the drive belongs to the authenticated company.
    """
    message = "You can only modify or manage drives created by your company."

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, "company_profile")):
            return False
        # obj is a Drive instance
        return obj.company == request.user.company_profile


class IsApplicationParticipant(BasePermission):
    """
    Allows access if the user is the applying student or the company hosting the drive.
    """
    message = "You do not have permission to view or manage this application."

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        if hasattr(request.user, "student_profile") and request.user.student_profile:
            return obj.student == request.user.student_profile

        if hasattr(request.user, "company_profile") and request.user.company_profile:
            return obj.drive.company == request.user.company_profile

        return False
