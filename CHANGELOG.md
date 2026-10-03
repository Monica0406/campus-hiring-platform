# Changelog

All notable changes to the **Campus & Internship Hiring Platform** project are documented in this file in chronological order following semantic principles.

---

## [0.5.0] - Step 5: Root Files, Architecture Diagrams & Documentation Compliance

### Added
- Standard mandatory root files: `LICENSE` (MIT), `.env.example`, `.gitignore`, and `CHANGELOG.md`.
- Comprehensive architecture diagrams under `docs/diagrams/`:
  - `system_architecture.md`: 4-tier architecture (React Frontend → Django REST API → Service Layer → MySQL DB) with placeholders for external services and deployment.
  - `er_diagram.md`: Full entity-relationship schema covering all six core entities (`Student`, `Company`, `Drive`, `Application`, `Interview`, `Offer`) and Django `User` authentication linkage.
  - `class_module_diagram.md`: Object-oriented Python structure showing model relationships, service functions, DRF serializers, and API views.
  - `api_contract_diagram.md`: Sequential recruitment workflow diagrams detailing request/response flows.
  - `docs/diagrams/README.md`: Central catalog for all architectural diagrams.
- PEP-257 docstrings across all core Django model classes (`hiring/models/`).
- Updated `Problem_Statement.md` aligning scope, domain, entities, roles, and constraints with current implementation.
- Rewrote root `README.md` to conform to the 16-section structure required by the Capstone Rules PDF.

---

## [0.4.0] - Step 4: React 18 Frontend Implementation

### Added
- Created modern React 18 frontend powered by Vite in `frontend/`.
- Configured Bootstrap 5, Bootstrap Icons, and custom CSS design system.
- Central Axios HTTP client (`frontend/src/api/client.js`) featuring:
  - Automatic `Authorization: Bearer <access_token>` injection.
  - Transparent 401 token refresh mechanism via `/api/auth/refresh/` with retry of failed requests.
  - Standardized error message extraction.
- React Router v6 navigation with `ProtectedRoute` enforcing role-based permissions (`student` vs. `company`).
- Global authentication context (`AuthContext.jsx`) managing login, registration, logout, and user session state.
- **Pages Implemented**:
  - Public: Landing page (`Home.jsx`), Dual-role Login (`Login.jsx`), Student Registration (`RegisterStudent.jsx`), Company Registration (`RegisterCompany.jsx`), Drive Catalog (`DriveList.jsx`), Drive Details (`DriveDetail.jsx`), 404 (`NotFound.jsx`).
  - Student: Dashboard (`StudentDashboard.jsx`), Profile Editor (`StudentProfile.jsx`), Applications Tracker (`StudentApplications.jsx`), Application Timeline (`StudentApplicationDetail.jsx`), Interviews (`StudentInterviews.jsx`), Offer Decision (`StudentOffers.jsx`).
  - Company: Recruiter Dashboard (`CompanyDashboard.jsx`), Profile Editor (`CompanyProfile.jsx`), Drive Management (`CompanyDrives.jsx`, `CreateDrive.jsx`, `EditDrive.jsx`), Drive Applicants review (`DriveApplicants.jsx`), Candidate Application View (`CompanyApplicationDetail.jsx`), Interview Evaluator (`CompanyInterviews.jsx`), Extended Offers Tracker (`CompanyOffers.jsx`).
- Full frontend production build verified (`npm run build` exits 0).

---

## [0.3.1] - Database Integration & Verification

### Added
- Verified local MySQL database connection for Django via `mysqlclient`.
- Applied migrations across all core models in the `campus_hiring_db` schema.
- Confirmed database engine health using `python manage.py check` and `python manage.py showmigrations`.

---

## [0.3.0] - Step 3: Automated Pytest Unit & Integration Test Suite

### Added
- Established automated test suite using `pytest` and `pytest-django`.
- Created configured `pytest.ini` with Django settings integration.
- Service-layer focused test modules:
  - `tests/test_auth.py`: Registration, login validation, JWT tokens, duplicate email checks.
  - `tests/test_drive_service.py`: Placement drive creation, defaults, filtering, and retrieval.
  - `tests/test_application_service.py`: Eligibility evaluation (CGPA, allowed departments), duplicate application rejections, submission history.
  - `tests/test_workflow_service.py`: State transition rules across shortlisting, interview scheduling, interview pass/fail evaluation, offer extension, and acceptance/rejection.
  - `tests/test_api_permissions.py`: Role boundary enforcement, unauthenticated protection, and cross-user data isolation.
- Maintained 56 passing tests (100% pass rate) with zero regressions.

---

## [0.2.0] - Step 2: Django REST API & JWT Authentication

### Added
- Implemented stateless REST API endpoints using Django REST Framework (DRF) and `djangorestframework-simplejwt`.
- Endpoints:
  - `/api/auth/register/student/`, `/api/auth/register/company/`, `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/me/`.
  - `/api/students/profile/`, `/api/companies/profile/`.
  - `/api/drives/`, `/api/drives/<id>/`.
  - `/api/applications/`, `/api/applications/<id>/`, `/api/applications/<id>/shortlist/`, `/api/applications/<id>/reject/`.
  - `/api/interviews/`, `/api/interviews/<id>/`.
  - `/api/offers/`, `/api/offers/<id>/`, `/api/offers/<id>/respond/`.
  - `/api/health/`.
- Custom DRF permission classes enforcing student and company role boundaries (`IsStudent`, `IsCompany`, `IsApplicationParticipant`).
- Comprehensive DRF serializers with input validation and OpenAPI schema annotations (`drf-spectacular`).

---

## [0.1.0] - Step 1: Core Domain Entities & Business Rules

### Added
- Designed and migrated six core domain models in `hiring/models/`:
  - `Student`: Academic profile (CGPA, department, roll number, resume).
  - `Company`: Recruiter and enterprise organization details.
  - `Drive`: Placement drives with criteria (min CGPA, allowed departments, deadlines).
  - `Application`: Student-drive application mapping with `UniqueConstraint` preventing duplicates.
  - `Interview`: Interview scheduling with status lifecycle (`SCHEDULED`, `CLEARED`, `FAILED`, `CANCELLED`).
  - `Offer`: Formal employment offer with salary, position, and decision states (`PENDING`, `ACCEPTED`, `REJECTED`).
- Implemented decoupled service layer in `hiring/services/`:
  - `drive_service.py`: Business logic for drive operations.
  - `application_service.py`: Strict eligibility checks and duplicate submission prevention.
  - `hiring_workflow_service.py`: Strict finite-state transition enforcement across recruitment stages.
  - `exceptions.py`: Custom domain exceptions (`EligibilityError`, `DuplicateApplicationError`, `WorkflowError`).
