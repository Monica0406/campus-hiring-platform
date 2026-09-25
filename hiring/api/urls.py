"""
URL configuration for all REST API endpoints under /api/
"""

from django.urls import path
from .health import HealthCheckView
from .auth import (
    StudentRegisterView,
    CompanyRegisterView,
    LoginView,
    MeView,
    RefreshTokenView,
)
from .students import StudentProfileView
from .companies import CompanyProfileView
from .drives import DriveListCreateView, DriveDetailView
from .applications import (
    ApplicationListCreateView,
    ApplicationDetailView,
    ApplicationShortlistView,
    ApplicationRejectView,
)
from .interviews import InterviewListCreateView, InterviewDetailUpdateView
from .offers import OfferListCreateView, OfferDetailView, OfferRespondView

urlpatterns = [
    # Health check
    path("health/", HealthCheckView.as_view(), name="api_health"),

    # Authentication & Session
    path("auth/register/student/", StudentRegisterView.as_view(), name="api_auth_register_student"),
    path("auth/register/company/", CompanyRegisterView.as_view(), name="api_auth_register_company"),
    path("auth/login/", LoginView.as_view(), name="api_auth_login"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="api_auth_refresh"),
    path("auth/me/", MeView.as_view(), name="api_auth_me"),

    # Student profile
    path("students/profile/", StudentProfileView.as_view(), name="api_student_profile"),

    # Company profile
    path("companies/profile/", CompanyProfileView.as_view(), name="api_company_profile"),

    # Drives
    path("drives/", DriveListCreateView.as_view(), name="api_drives_list_create"),
    path("drives/<int:pk>/", DriveDetailView.as_view(), name="api_drives_detail"),

    # Applications
    path("applications/", ApplicationListCreateView.as_view(), name="api_applications_list_create"),
    path("applications/<int:pk>/", ApplicationDetailView.as_view(), name="api_applications_detail"),
    path("applications/<int:pk>/shortlist/", ApplicationShortlistView.as_view(), name="api_applications_shortlist"),
    path("applications/<int:pk>/reject/", ApplicationRejectView.as_view(), name="api_applications_reject"),

    # Interviews
    path("interviews/", InterviewListCreateView.as_view(), name="api_interviews_list_create"),
    path("interviews/<int:pk>/", InterviewDetailUpdateView.as_view(), name="api_interviews_detail_update"),

    # Offers
    path("offers/", OfferListCreateView.as_view(), name="api_offers_list_create"),
    path("offers/<int:pk>/", OfferDetailView.as_view(), name="api_offers_detail"),
    path("offers/<int:pk>/respond/", OfferRespondView.as_view(), name="api_offers_respond"),
]
