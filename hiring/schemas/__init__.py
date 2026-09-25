"""
Export all schemas/serializers.
"""

from .auth import (
    StudentRegisterSerializer,
    CompanyRegisterSerializer,
    LoginSerializer,
)
from .student import (
    StudentSerializer,
    StudentProfileUpdateSerializer,
)
from .company import (
    CompanySerializer,
    CompanyProfileUpdateSerializer,
)
from .drive import (
    DriveSerializer,
    DriveCreateUpdateSerializer,
)
from .application import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationRejectSerializer,
)
from .interview import (
    InterviewSerializer,
    InterviewCreateSerializer,
    InterviewResultSerializer,
)
from .offer import (
    OfferSerializer,
    OfferCreateSerializer,
    OfferRespondSerializer,
)

__all__ = [
    "StudentRegisterSerializer",
    "CompanyRegisterSerializer",
    "LoginSerializer",
    "StudentSerializer",
    "StudentProfileUpdateSerializer",
    "CompanySerializer",
    "CompanyProfileUpdateSerializer",
    "DriveSerializer",
    "DriveCreateUpdateSerializer",
    "ApplicationSerializer",
    "ApplicationCreateSerializer",
    "ApplicationRejectSerializer",
    "InterviewSerializer",
    "InterviewCreateSerializer",
    "InterviewResultSerializer",
    "OfferSerializer",
    "OfferCreateSerializer",
    "OfferRespondSerializer",
]
