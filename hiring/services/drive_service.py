"""
Drive service module: handles drive creation, retrieval, and updates.
"""

import logging
from decimal import Decimal
from hiring.models import Drive, Company

logger = logging.getLogger("hiring")


def create_drive(
    company: Company,
    title: str,
    description: str,
    drive_date,
    min_cgpa=0.0,
    allowed_departments: str = "All",
    eligibility_notes: str = ""
) -> Drive:
    """
    Creates and saves a new placement drive for a company.
    """
    if isinstance(min_cgpa, (int, float, str)):
        min_cgpa = Decimal(str(min_cgpa))

    drive = Drive.objects.create(
        company=company,
        title=title.strip(),
        description=description.strip(),
        drive_date=drive_date,
        min_cgpa=min_cgpa,
        allowed_departments=allowed_departments.strip() or "All",
        eligibility=eligibility_notes.strip(),
        is_active=True,
    )
    logger.info(
        "Drive created successfully: id=%s, company='%s', title='%s', min_cgpa=%s",
        drive.id,
        company.company_name,
        drive.title,
        drive.min_cgpa,
    )
    return drive


def get_active_drives():
    """
    Returns all active placement drives ordered by drive date.
    """
    return Drive.objects.filter(is_active=True).select_related("company").order_by("drive_date")


def get_company_drives(company: Company):
    """
    Returns all placement drives belonging to a specific company.
    """
    return Drive.objects.filter(company=company).order_by("-drive_date")


def get_drive_by_id(drive_id: int) -> Drive:
    """
    Retrieves a drive by its primary key with related company info.
    """
    return Drive.objects.select_related("company").get(id=drive_id)
