"""
Custom service exceptions for the Internship & Campus Hiring Platform.
"""

class HiringServiceError(Exception):
    """Base exception for all hiring business rule violations."""
    pass


class EligibilityError(HiringServiceError):
    """Raised when a student does not meet drive eligibility criteria."""
    pass


class DuplicateApplicationError(HiringServiceError):
    """Raised when a student attempts to apply for the same drive multiple times."""
    pass


class WorkflowError(HiringServiceError):
    """Raised when an invalid status transition or out-of-order action is attempted."""
    pass
