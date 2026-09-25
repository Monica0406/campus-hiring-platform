"""
Application service module: handles student applications, eligibility checks,
and duplicate prevention.
"""

import logging
from typing import Tuple
from django.db import IntegrityError
from hiring.models import Application, ApplicationStatus, Drive, Student
from .exceptions import DuplicateApplicationError, EligibilityError

logger = logging.getLogger("hiring")


def check_student_eligibility(student: Student, drive: Drive) -> Tuple[bool, str]:
    """
    Evaluates whether a student meets the criteria defined for a drive.
    Criteria:
    1. Student CGPA must be >= drive.min_cgpa.
    2. Student department must be included in drive.allowed_departments (or 'All').
    """
    if student.cgpa < drive.min_cgpa:
        return (
            False,
            f"Eligibility requirement not met: Minimum CGPA required is {drive.min_cgpa}, but your CGPA is {student.cgpa}."
        )

    allowed_raw = drive.allowed_departments or "All"
    allowed_list = [d.strip().upper() for d in allowed_raw.split(",") if d.strip()]

    if "ALL" not in allowed_list:
        student_dept = (student.department or "").strip().upper()
        if student_dept not in allowed_list:
            return (
                False,
                f"Eligibility requirement not met: Department '{student.department}' is not eligible. Allowed: {drive.allowed_departments}."
            )

    return True, ""


def apply_to_drive(student: Student, drive: Drive) -> Application:
    """
    Applies a student to a placement drive.
    Validates:
    1. Student has not already applied to this drive.
    2. Drive is currently active.
    3. Student meets CGPA and department eligibility.
    """
    if not drive.is_active:
        raise EligibilityError("This placement drive is currently inactive or closed.")

    # 1. Duplicate check (application-level)
    if Application.objects.filter(student=student, drive=drive).exists():
        logger.warning(
            "Duplicate application rejected: student_id=%s, drive_id=%s",
            student.id,
            drive.id,
        )
        raise DuplicateApplicationError("You have already applied to this placement drive.")

    # 2. Eligibility validation
    is_eligible, reason = check_student_eligibility(student, drive)
    if not is_eligible:
        logger.info(
            "Ineligible application rejected: student_id=%s, drive_id=%s, reason='%s'",
            student.id,
            drive.id,
            reason,
        )
        raise EligibilityError(reason)

    # 3. Create application (enforcing DB constraint)
    try:
        application = Application.objects.create(
            student=student,
            drive=drive,
            status=ApplicationStatus.APPLIED,
        )
        logger.info(
            "Application created: app_id=%s, student_id=%s, drive_id=%s",
            application.id,
            student.id,
            drive.id,
        )
        return application
    except IntegrityError:
        logger.warning(
            "Database integrity blocked duplicate application: student_id=%s, drive_id=%s",
            student.id,
            drive.id,
        )
        raise DuplicateApplicationError("You have already applied to this placement drive.")


def get_student_applications(student: Student):
    """
    Returns all applications submitted by a student.
    """
    return Application.objects.filter(student=student).select_related(
        "drive", "drive__company"
    ).order_by("-applied_date")


def get_drive_applications(drive: Drive):
    """
    Returns all applications received for a drive.
    """
    return Application.objects.filter(drive=drive).select_related("student").order_by("-applied_date")
