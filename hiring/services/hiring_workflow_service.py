"""
Hiring workflow service: manages the end-to-end recruitment lifecycle and state transitions.

Lifecycle:
APPLIED -> SHORTLISTED -> INTERVIEW_SCHEDULED -> SELECTED -> OFFERED
(REJECTED permitted from any pre-offer stage)
"""

import logging
from decimal import Decimal
from hiring.models import (
    Application,
    ApplicationStatus,
    Interview,
    InterviewStatus,
    Offer,
    OfferStatus,
)
from .exceptions import WorkflowError

logger = logging.getLogger("hiring")


def shortlist_application(application: Application) -> Application:
    """
    Moves an application from APPLIED to SHORTLISTED.
    """
    if application.status != ApplicationStatus.APPLIED:
        raise WorkflowError(
            f"Cannot shortlist application. Expected status '{ApplicationStatus.APPLIED}', got '{application.status}'."
        )

    application.status = ApplicationStatus.SHORTLISTED
    application.save(update_fields=["status"])
    logger.info("Application shortlisted: app_id=%s, student=%s", application.id, application.student.name)
    return application


def reject_application(application: Application, reason: str = "") -> Application:
    """
    Rejects an application from APPLIED, SHORTLISTED, INTERVIEW_SCHEDULED, or SELECTED stage.
    Cannot reject already rejected or offered applications.
    """
    non_rejectable = [ApplicationStatus.REJECTED, ApplicationStatus.OFFERED]
    if application.status in non_rejectable:
        raise WorkflowError(
            f"Cannot reject application currently in '{application.status}' status."
        )

    old_status = application.status
    application.status = ApplicationStatus.REJECTED
    application.save(update_fields=["status"])
    logger.info(
        "Application rejected: app_id=%s, from_status=%s, reason='%s'",
        application.id,
        old_status,
        reason,
    )
    return application


def schedule_interview(
    application: Application,
    interview_date,
    mode: str = "Online"
) -> Interview:
    """
    Schedules an interview for an application.
    Rule: Interview can only be scheduled for a SHORTLISTED application.
    """
    if application.status != ApplicationStatus.SHORTLISTED:
        raise WorkflowError(
            f"An interview can only be scheduled for a '{ApplicationStatus.SHORTLISTED}' application. "
            f"Current status is '{application.status}'."
        )

    interview = Interview.objects.create(
        application=application,
        interview_date=interview_date,
        mode=mode.strip() or "Online",
        status=InterviewStatus.SCHEDULED,
    )

    application.status = ApplicationStatus.INTERVIEW_SCHEDULED
    application.save(update_fields=["status"])

    logger.info(
        "Interview scheduled: interview_id=%s, app_id=%s, date=%s, mode=%s",
        interview.id,
        application.id,
        interview_date,
        mode,
    )
    return interview


def record_interview_result(interview: Interview, passed: bool) -> Interview:
    """
    Records whether an interview was passed (cleared) or failed.
    - If passed: interview becomes CLEARED, application becomes SELECTED.
    - If failed: interview becomes FAILED, application becomes REJECTED.
    """
    if interview.status != InterviewStatus.SCHEDULED:
        raise WorkflowError(
            f"Interview result cannot be recorded. Expected status '{InterviewStatus.SCHEDULED}', got '{interview.status}'."
        )

    application = interview.application

    if passed:
        interview.status = InterviewStatus.CLEARED
        application.status = ApplicationStatus.SELECTED
        logger.info(
            "Interview cleared: interview_id=%s, student=%s -> Application SELECTED",
            interview.id,
            application.student.name,
        )
    else:
        interview.status = InterviewStatus.FAILED
        application.status = ApplicationStatus.REJECTED
        logger.info(
            "Interview failed: interview_id=%s, student=%s -> Application REJECTED",
            interview.id,
            application.student.name,
        )

    interview.save(update_fields=["status"])
    application.save(update_fields=["status"])
    return interview


def create_offer(
    application: Application,
    position: str,
    salary,
) -> Offer:
    """
    Generates a job offer for an applicant.
    Rule: An offer can only be created after the interview is passed/cleared.
    """
    if application.status != ApplicationStatus.SELECTED:
        raise WorkflowError(
            f"An offer can only be generated for a '{ApplicationStatus.SELECTED}' application. "
            f"Current status is '{application.status}'."
        )

    has_cleared_interview = application.interviews.filter(status=InterviewStatus.CLEARED).exists()
    if not has_cleared_interview:
        raise WorkflowError(
            "Cannot create offer: No cleared interview record found for this application."
        )

    if isinstance(salary, (int, float, str)):
        salary = Decimal(str(salary))

    offer = Offer.objects.create(
        application=application,
        position=position.strip(),
        salary=salary,
        status=OfferStatus.PENDING,
    )

    application.status = ApplicationStatus.OFFERED
    application.save(update_fields=["status"])

    logger.info(
        "Offer generated: offer_id=%s, app_id=%s, position='%s', salary=%s",
        offer.id,
        application.id,
        offer.position,
        offer.salary,
    )
    return offer


def respond_to_offer(offer: Offer, accept: bool) -> Offer:
    """
    Records a student's acceptance or rejection of a job offer.
    """
    if offer.status != OfferStatus.PENDING:
        raise WorkflowError(
            f"Cannot respond to offer. Expected status '{OfferStatus.PENDING}', got '{offer.status}'."
        )

    if accept:
        offer.status = OfferStatus.ACCEPTED
        logger.info("Offer accepted: offer_id=%s, student=%s", offer.id, offer.application.student.name)
    else:
        offer.status = OfferStatus.REJECTED
        logger.info("Offer rejected: offer_id=%s, student=%s", offer.id, offer.application.student.name)

    offer.save(update_fields=["status"])
    return offer
