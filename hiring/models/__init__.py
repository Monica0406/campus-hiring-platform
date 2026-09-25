"""
Domain models package for the Campus & Internship Hiring Platform.

Exports core domain entities:
- Student: Academic candidate profile
- Company: Corporate recruiter entity
- Drive: Campus recruitment placement drive
- Application: Student-to-drive application with unique constraint
- Interview: Evaluation round and result
- Offer: Formal employment offer and student response
"""

from .student import Student
from .company import Company
from .drive import Drive
from .application import Application, ApplicationStatus
from .interview import Interview, InterviewStatus
from .offer import Offer, OfferStatus

__all__ = [
    "Student",
    "Company",
    "Drive",
    "Application",
    "ApplicationStatus",
    "Interview",
    "InterviewStatus",
    "Offer",
    "OfferStatus",
]