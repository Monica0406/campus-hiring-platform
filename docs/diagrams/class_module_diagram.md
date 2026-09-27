# Python Class & Module Diagram

This diagram documents the Object-Oriented module hierarchy and dependencies within the Django backend (`hiring/` application).

---

## 1. Class & Module Architecture

```mermaid
classDiagram
    direction TB

    %% Models
    namespace Models {
        class Student {
            +User user
            +CharField name
            +EmailField email
            +CharField college
            +CharField department
            +DecimalField cgpa
            +FileField resume
            +__str__()
        }
        class Company {
            +User user
            +CharField company_name
            +EmailField email
            +CharField location
            +__str__()
        }
        class Drive {
            +Company company
            +CharField title
            +TextField description
            +DecimalField min_cgpa
            +CharField allowed_departments
            +TextField eligibility
            +DateField drive_date
            +BooleanField is_active
            +__str__()
        }
        class Application {
            +Student student
            +Drive drive
            +DateTimeField applied_date
            +CharField status
            +__str__()
        }
        class Interview {
            +Application application
            +DateTimeField interview_date
            +CharField mode
            +CharField status
            +__str__()
        }
        class Offer {
            +Application application
            +DateField offer_date
            +CharField position
            +DecimalField salary
            +CharField status
            +__str__()
        }
    }

    %% Service Layer
    namespace Services {
        class DriveService {
            <<module>>
            +create_drive(company, title, description, drive_date, min_cgpa, allowed_departments) Drive
            +get_active_drives() QuerySet
            +get_company_drives(company) QuerySet
            +get_drive_by_id(drive_id) Drive
        }
        class ApplicationService {
            <<module>>
            +check_student_eligibility(student, drive) Tuple~bool, str~
            +apply_to_drive(student, drive) Application
            +get_student_applications(student) QuerySet
            +get_drive_applications(drive) QuerySet
        }
        class HiringWorkflowService {
            <<module>>
            +shortlist_application(application) Application
            +reject_application(application, reason) Application
            +schedule_interview(application, interview_date, mode) Interview
            +record_interview_result(interview, passed) Interview
            +create_offer(application, position, salary) Offer
            +respond_to_offer(offer, accept) Offer
        }
    }

    %% API Layer
    namespace APIViews {
        class AuthViews {
            +StudentRegisterView
            +CompanyRegisterView
            +LoginView
            +RefreshTokenView
            +MeView
        }
        class DriveViews {
            +DriveListCreateView
            +DriveDetailView
        }
        class ApplicationViews {
            +ApplicationListCreateView
            +ApplicationDetailView
            +ApplicationShortlistView
            +ApplicationRejectView
        }
        class InterviewViews {
            +InterviewListCreateView
            +InterviewDetailUpdateView
        }
        class OfferViews {
            +OfferListCreateView
            +OfferDetailView
            +OfferRespondView
        }
    }

    %% Relationships
    Company "1" *-- "many" Drive
    Student "1" *-- "many" Application
    Drive "1" *-- "many" Application
    Application "1" *-- "many" Interview
    Application "1" *-- "many" Offer

    DriveService ..> Drive : creates/queries
    ApplicationService ..> Application : evaluates/creates
    ApplicationService ..> Student : inspects
    ApplicationService ..> Drive : inspects
    HiringWorkflowService ..> Application : mutates status
    HiringWorkflowService ..> Interview : schedules/evaluates
    HiringWorkflowService ..> Offer : creates/responds

    DriveViews ..> DriveService : calls
    ApplicationViews ..> ApplicationService : calls
    ApplicationViews ..> HiringWorkflowService : calls
    InterviewViews ..> HiringWorkflowService : calls
    OfferViews ..> HiringWorkflowService : calls
```

---

## 2. Structural Principles

1. **Separation of Concerns**: HTTP parsing, authentication checks, and JSON rendering live in the `hiring.api` views; all core validation and business decisions live in `hiring.services`.
2. **Encapsulated Workflow Transitions**: Status changes are guarded by `WorkflowError` in `hiring_workflow_service.py` to prevent out-of-sequence operations (e.g., offering before interview clearance).
3. **Decoupled Serializers**: Serializers in `hiring.schemas` handle bidirectional transformations between JSON payloads and model instances.
