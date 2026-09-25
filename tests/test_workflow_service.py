"""
Unit tests for hiring/services/hiring_workflow_service.py
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from hiring.models import (
    Student,
    Company,
    Drive,
    Application,
    ApplicationStatus,
    Interview,
    InterviewStatus,
    Offer,
    OfferStatus,
)
from hiring.services import (
    application_service,
    drive_service,
    hiring_workflow_service,
)
from hiring.services.exceptions import WorkflowError


@pytest.fixture
def test_setup(db):
    """Creates a basic setup with company, drive, and applied candidate."""
    comp_user = User.objects.create_user(username="wk_comp@test.com", email="wk_comp@test.com", password="pw")
    company = Company.objects.create(
        user=comp_user,
        company_name="Workflow Corp",
        email="wk_comp@test.com",
        password="hash",
        location="NY",
    )
    drive = drive_service.create_drive(
        company=company,
        title="Software Engineer Drive",
        description="Full-time software role",
        drive_date=date.today() + timedelta(days=15),
        min_cgpa=7.00,
        allowed_departments="CSE,IT",
    )
    stu_user = User.objects.create_user(username="wk_stu@test.com", email="wk_stu@test.com", password="pw")
    student = Student.objects.create(
        user=stu_user,
        name="Diana Prince",
        email="wk_stu@test.com",
        password="hash",
        college="Tech Univ",
        department="CSE",
        cgpa=Decimal("8.80"),
    )
    application = application_service.apply_to_drive(student, drive)
    return {
        "company": company,
        "drive": drive,
        "student": student,
        "application": application,
    }


@pytest.mark.django_db
def test_shortlist_application_success(test_setup):
    """Verify application moves from APPLIED to SHORTLISTED."""
    app = test_setup["application"]
    assert app.status == ApplicationStatus.APPLIED

    updated_app = hiring_workflow_service.shortlist_application(app)
    assert updated_app.status == ApplicationStatus.SHORTLISTED
    app.refresh_from_db()
    assert app.status == ApplicationStatus.SHORTLISTED


@pytest.mark.django_db
def test_invalid_shortlist_transition_rejected(test_setup):
    """Verify that shortlisting an application that is not APPLIED raises WorkflowError."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)  # Now SHORTLISTED

    with pytest.raises(WorkflowError) as exc_info:
        hiring_workflow_service.shortlist_application(app)

    assert "Cannot shortlist application" in str(exc_info.value)


@pytest.mark.django_db
def test_schedule_interview_success(test_setup):
    """Verify scheduling interview moves application to INTERVIEW_SCHEDULED and creates Interview."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)

    interview_time = timezone.now() + timedelta(days=2)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=interview_time,
        mode="Video Call",
    )

    assert interview.id is not None
    assert interview.status == InterviewStatus.SCHEDULED
    assert interview.mode == "Video Call"
    app.refresh_from_db()
    assert app.status == ApplicationStatus.INTERVIEW_SCHEDULED


@pytest.mark.django_db
def test_interview_cannot_be_scheduled_before_shortlist(test_setup):
    """Verify an interview cannot be scheduled while application is still APPLIED."""
    app = test_setup["application"]
    assert app.status == ApplicationStatus.APPLIED

    interview_time = timezone.now() + timedelta(days=2)
    with pytest.raises(WorkflowError) as exc_info:
        hiring_workflow_service.schedule_interview(
            application=app,
            interview_date=interview_time,
        )

    assert "only be scheduled for a 'SHORTLISTED' application" in str(exc_info.value)


@pytest.mark.django_db
def test_passed_interview_cleared_and_selected(test_setup):
    """Verify passing interview marks interview CLEARED and application SELECTED."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=timezone.now() + timedelta(days=1),
    )

    updated_interview = hiring_workflow_service.record_interview_result(interview, passed=True)

    assert updated_interview.status == InterviewStatus.CLEARED
    app.refresh_from_db()
    assert app.status == ApplicationStatus.SELECTED


@pytest.mark.django_db
def test_failed_interview_failed_and_rejected(test_setup):
    """Verify failing interview marks interview FAILED and application REJECTED."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=timezone.now() + timedelta(days=1),
    )

    updated_interview = hiring_workflow_service.record_interview_result(interview, passed=False)

    assert updated_interview.status == InterviewStatus.FAILED
    app.refresh_from_db()
    assert app.status == ApplicationStatus.REJECTED


@pytest.mark.django_db
def test_cannot_record_result_on_non_scheduled_interview(test_setup):
    """Verify recording result on already resolved interview raises WorkflowError."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=timezone.now() + timedelta(days=1),
    )
    hiring_workflow_service.record_interview_result(interview, passed=True)

    with pytest.raises(WorkflowError) as exc_info:
        hiring_workflow_service.record_interview_result(interview, passed=False)

    assert "Interview result cannot be recorded" in str(exc_info.value)


@pytest.mark.django_db
def test_offer_cannot_be_created_before_interview_clearance(test_setup):
    """Verify offer creation fails if application is not in SELECTED status."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)

    with pytest.raises(WorkflowError) as exc_info:
        hiring_workflow_service.create_offer(
            application=app,
            position="Software Engineer",
            salary="80000.00",
        )

    assert "only be generated for a 'SELECTED' application" in str(exc_info.value)


@pytest.mark.django_db
def test_cleared_interview_offer_creation_success(test_setup):
    """Verify offer can be generated after interview is cleared, moving app to OFFERED."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=timezone.now() + timedelta(days=1),
    )
    hiring_workflow_service.record_interview_result(interview, passed=True)

    offer = hiring_workflow_service.create_offer(
        application=app,
        position="Junior Backend Developer",
        salary=85000.00,
    )

    assert offer.id is not None
    assert offer.position == "Junior Backend Developer"
    assert offer.salary == Decimal("85000.00")
    assert offer.status == OfferStatus.PENDING
    app.refresh_from_db()
    assert app.status == ApplicationStatus.OFFERED


@pytest.mark.django_db
def test_student_accept_offer(test_setup):
    """Verify student accepting offer marks offer ACCEPTED."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=timezone.now() + timedelta(days=1),
    )
    hiring_workflow_service.record_interview_result(interview, passed=True)
    offer = hiring_workflow_service.create_offer(app, position="Dev", salary="90000.00")

    updated_offer = hiring_workflow_service.respond_to_offer(offer, accept=True)
    assert updated_offer.status == OfferStatus.ACCEPTED


@pytest.mark.django_db
def test_student_reject_offer(test_setup):
    """Verify student rejecting offer marks offer REJECTED."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=timezone.now() + timedelta(days=1),
    )
    hiring_workflow_service.record_interview_result(interview, passed=True)
    offer = hiring_workflow_service.create_offer(app, position="Dev", salary="90000.00")

    updated_offer = hiring_workflow_service.respond_to_offer(offer, accept=False)
    assert updated_offer.status == OfferStatus.REJECTED


@pytest.mark.django_db
def test_respond_to_non_pending_offer_rejected(test_setup):
    """Verify responding to an already responded offer raises WorkflowError."""
    app = test_setup["application"]
    hiring_workflow_service.shortlist_application(app)
    interview = hiring_workflow_service.schedule_interview(
        application=app,
        interview_date=timezone.now() + timedelta(days=1),
    )
    hiring_workflow_service.record_interview_result(interview, passed=True)
    offer = hiring_workflow_service.create_offer(app, position="Dev", salary="90000.00")
    hiring_workflow_service.respond_to_offer(offer, accept=True)

    with pytest.raises(WorkflowError) as exc_info:
        hiring_workflow_service.respond_to_offer(offer, accept=False)

    assert "Cannot respond to offer" in str(exc_info.value)


@pytest.mark.django_db
def test_reject_application_success(test_setup):
    """Verify rejecting an application transitions it to REJECTED."""
    app = test_setup["application"]
    rejected_app = hiring_workflow_service.reject_application(app, reason="Did not meet profile requirements")

    assert rejected_app.status == ApplicationStatus.REJECTED
    app.refresh_from_db()
    assert app.status == ApplicationStatus.REJECTED


@pytest.mark.django_db
def test_cannot_reject_offered_or_already_rejected(test_setup):
    """Verify rejecting an application already REJECTED or OFFERED raises WorkflowError."""
    app = test_setup["application"]
    hiring_workflow_service.reject_application(app)  # Now REJECTED

    with pytest.raises(WorkflowError) as exc_info:
        hiring_workflow_service.reject_application(app)

    assert "Cannot reject application currently in 'REJECTED' status" in str(exc_info.value)
