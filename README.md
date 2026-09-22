# Campus & Internship Hiring Platform

> A full-stack web application connecting university students and corporate recruiters through automated placement drives, eligibility validation, interview scheduling, and offer management.

---

## 1. Title / Tagline

**Campus & Internship Hiring Platform**  
*Streamlining university campus recruitment with automated workflows, eligibility checks, and real-time application tracking.*

---

## 2. Live / Video Links

- **Live Production URL**: *Pending / TBD (Local development and evaluation environment active; cloud deployment planned for subsequent milestone)*
- **Demo Video Walkthrough**: *Pending / TBD (To be recorded and linked upon cloud deployment)*
- **Local Frontend**: `http://localhost:5173/`
- **Local Backend**: `http://127.0.0.1:8000/`
- **API Health Check**: `http://127.0.0.1:8000/api/health/`
- **Interactive API Documentation (Swagger UI)**: `http://127.0.0.1:8000/api/docs/`
- **Raw OpenAPI Schema**: `http://127.0.0.1:8000/api/schema/`

---

## 3. Overview

The **Campus & Internship Hiring Platform** is an enterprise-grade recruitment management system designed for university Training & Placement (T&P) cells, corporate recruiters, and students.

Traditional campus recruitment suffers from fragmented communication, reliance on manual spreadsheets, untracked email threads, and error-prone eligibility evaluations. This platform replaces disjointed tools with a centralized, role-based single-page application (React 18) and a robust RESTful backend (Django REST Framework) powered by a relational database (MySQL 8.0).

### Key Value Propositions
- **Centralized Opportunities**: Students discover, inspect, and apply to verified campus placement drives.
- **Automated Eligibility Engine**: Automatically validates student CGPA and department criteria against company drive thresholds prior to application persistence, eliminating manual filtering errors.
- **Duplicate Application Prevention**: Multi-level database constraints guarantee that students cannot re-apply to the same drive.
- **Strict Lifecycle Pipeline**: A finite-state machine controls application transitions:
  $$\text{APPLIED} \longrightarrow \text{SHORTLISTED} \longrightarrow \text{INTERVIEW\_SCHEDULED} \longrightarrow \text{SELECTED} \longrightarrow \text{OFFERED} \longrightarrow \text{ACCEPTED}$$
- **Role Isolation & Security**: Strict permission boundaries ensure that students only access their own records and recruiters only manage their respective drives, applicants, interviews, and offers.
- **bcrypt Password Compliance**: Passwords are securely hashed with bcrypt (`BCryptSHA256PasswordHasher` / `BCryptPasswordHasher`), preventing plaintext exposure.
- **Clean Resume Storage**: Student resumes are stored on disk under `media/resumes/` while the database holds clean relative file references (`resumes/<filename>.pdf`), kept strictly ignored by Git.

---

## 4. Architecture Image & Diagrams

The platform follows a clean four-tier architecture separating the React single-page frontend, stateless REST API gateway, domain business logic services, and MySQL relational database.

Detailed architectural documentation and diagrams are located in [`docs/diagrams/`](docs/diagrams/):
- **[System Architecture Diagram](docs/diagrams/system_architecture.md)**: 4-tier overview showing React, Django REST API, Service Layer, and MySQL DB.
- **[Entity-Relationship (ER) Diagram](docs/diagrams/er_diagram.md)**: Data model covering all six core entities and Django User authentication.
- **[Python Class & Module Diagram](docs/diagrams/class_module_diagram.md)**: Object-oriented hierarchy of models, services, and API controllers.
- **[API Contract & Flow Diagram](docs/diagrams/api_contract_diagram.md)**: Sequential request/response workflows for recruitment lifecycle operations.

### High-Level Architecture Flow

```text
+-------------------------------------------------------------------------+
|                  Client Presentation Tier (Browser)                     |
|         React 18 Single Page Application (Vite + Bootstrap 5)           |
|      - Global AuthContext (Stateless JWT session & role tracking)       |
|      - Central Axios Client (Bearer injection, 401 refresh interceptor) |
+------------------------------------+------------------------------------+
                                     |  HTTPS / JSON
                                     v
+------------------------------------+------------------------------------+
|               API & Security Tier (Django REST Framework)               |
|      - Role-Based Permissions (IsStudent, IsCompany, IsDriveOwner)      |
|      - SimpleJWT Token Authentication (/api/auth/*)                     |
|      - Password Hashing: bcrypt (BCryptSHA256PasswordHasher)            |
|      - OpenAPI Documentation: drf-spectacular (/api/docs/)              |
+------------------------------------+------------------------------------+
                                     |  Method Calls
                                     v
+------------------------------------+------------------------------------+
|                Business Logic & Service Layer (Python)                  |
|      - drive_service.py: Drive creation, validation, active querying    |
|      - application_service.py: CGPA & department eligibility rules      |
|      - hiring_workflow_service.py: Finite-state lifecycle enforcement   |
+------------------------------------+------------------------------------+
                                     |  Django ORM
                                     v
+------------------------------------+------------------------------------+
|                     Persistence Tier (Database)                         |
|         MySQL 8.0 Relational Database (campus_hiring_db)                |
|      - 6 Core Entities: Student, Company, Drive, Application,           |
|                         Interview, Offer                                |
|      - Unique constraint: (student_id, drive_id)                        |
|      - File reference storage: Student.resume -> media/resumes/         |
+-------------------------------------------------------------------------+
```

---

## 5. Tech Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | Django | 6.0+ | Core web framework, ORM, and admin |
| **API Framework** | Django REST Framework | 3.18+ | RESTful API controllers and serializers |
| **Authentication** | SimpleJWT | 5.5+ | Stateless JWT access and refresh tokens |
| **Password Hashing** | bcrypt | 5.0+ | Secure bcrypt password hashing (`BCryptSHA256PasswordHasher`) |
| **API Documentation** | drf-spectacular | 0.30+ | OpenAPI 3.0 schema and Swagger UI (`/api/docs/`) |
| **Database** | MySQL | 8.0+ | Relational data persistence |
| **DB Driver** | mysqlclient | 2.2+ | Native Python C-extension MySQL client |
| **Testing** | Pytest & pytest-django | 9.1+ / 4.14+ | Automated unit and integration test suite (61 tests) |
| **Frontend UI** | React | 18.3+ | Single-page client presentation application |
| **Build Tool** | Vite | 6.4+ | Fast development server and production bundler |
| **Styling** | Bootstrap 5 & Bootstrap Icons | 5.3+ / 1.11+ | Responsive grid, typography, and UI widgets |
| **HTTP Client** | Axios | 1.7+ | HTTP client with automatic token interceptors |
| **Routing** | React Router DOM | 6.28+ | Client-side routing and protected route guards |

---

## 6. Features

### Verified Student Portal Workflows
- **Account Registration & Login**: Sign up with legal name, institutional email, college, department, and CGPA. Newly created passwords are automatically hashed with bcrypt. Login issues stateless JWT access and refresh tokens.
- **Academic Profile & Resume Management**: View and modify academic details. Upload candidate resume in PDF format; the file is securely stored under `media/resumes/` while the database holds only the relative path reference (`resumes/<filename>.pdf`).
- **Drive Discovery**: Browse available campus placement drives with department filters, minimum CGPA thresholds, and search capabilities.
- **Automated Eligibility Verification**: When viewing drive details, the system verifies candidate eligibility (minimum CGPA and allowed departments) before enabling application submission.
- **One-Click Application**: Submit applications to eligible drives. Duplicate applications to the same drive are rejected by both service logic and database constraints.
- **Application History Tracking**: Track application progress across lifecycle stages (`APPLIED`, `SHORTLISTED`, `INTERVIEW_SCHEDULED`, `SELECTED`, `OFFERED`, `REJECTED`).
- **Interview Tracking**: View scheduled interview rounds, interview dates/times, and format (Online with meeting links vs. In-Person).
- **Formal Offer Decisions**: Inspect formal employment offers detailing position designation and annual compensation (CTC), with one-click **Accept** or **Reject** decision handling.

### Verified Company Recruiter Workflows
- **Recruiter Registration & Login**: Register corporate accounts with company name, recruiter email, password (hashed with bcrypt), and location.
- **Recruiter Dashboard**: High-level KPI metrics showing active placement drives, total applicant count, pending evaluations, and accepted offers.
- **Drive Lifecycle Management**: Post placement drives with role titles, descriptions, minimum CGPA thresholds, allowed departments, eligibility notes, and drive dates. Update or edit active drive details.
- **Applicant Review & Filtering**: Inspect applicant pools per drive with status filters, candidate CGPA, department, and application date.
- **Candidate Shortlisting & Rejection**: Transition qualified candidates to `SHORTLISTED` status or record structured rejection feedback.
- **Interview Scheduling**: Schedule interview rounds for shortlisted applicants specifying datetime, round name, and mode (Online with URL or In-Person venue), advancing application to `INTERVIEW_SCHEDULED`.
- **Interview Outcome Evaluation**: Record evaluation outcomes (**Pass** or **Fail**); passing candidates automatically advance to `SELECTED`.
- **Formal Offer Issuance**: Extend formal job offers specifying job designation and annual compensation package, advancing candidate to `OFFERED`.
- **Real-Time Offer Tracking**: Monitor candidate acceptance decisions (`PENDING`, `ACCEPTED`, `REJECTED`) in real time.

### Authentication & Role-Based Permissions
- **bcrypt Password Security**: Passwords are never stored in plaintext and are never exposed in API responses or logs. Primary hasher is `BCryptSHA256PasswordHasher` (with SHA-256 pre-hashing to guard against bcrypt's 72-character truncation limitation), with `BCryptPasswordHasher` and PBKDF2 fallbacks.
- **Role Isolation**: Strict permission guards (`IsStudent`, `IsCompany`, `IsDriveOwner`) prevent cross-role operations:
  - Students cannot create/edit placement drives or schedule interviews (HTTP 403 Forbidden).
  - Companies cannot submit student applications (HTTP 403 Forbidden).
  - Unauthenticated requests to protected endpoints are rejected (HTTP 401 Unauthorized).
- **Client-Side Route Guards**: `ProtectedRoute` validates authentication and normalizes role tokens, redirecting unauthorized users to their respective dashboards.

---

## 7. Screenshots

*(Screenshots can be captured during local runtime and placed in `docs/screenshots/`)*

| View | Description | Status |
| :--- | :--- | :--- |
| **Landing Page** | Public home screen with platform statistics, hero, and role selection | *Placeholder (`docs/screenshots/home.png`)* |
| **Student Dashboard** | KPI overview of active applications, next interview, and quick actions | *Placeholder (`docs/screenshots/student_dashboard.png`)* |
| **Drive Catalog** | Placement drive listings with branch filtering and eligibility highlights | *Placeholder (`docs/screenshots/drives_list.png`)* |
| **Company Recruiter Dashboard** | Recruiter metrics, drive manager, and applicant pipeline | *Placeholder (`docs/screenshots/company_dashboard.png`)* |
| **Drive Applicants View** | Candidate review table with Shortlist and Reject actions | *Placeholder (`docs/screenshots/applicants.png`)* |
| **Interview Evaluation Modal** | Interface to record candidate evaluation outcomes (Pass/Fail) | *Placeholder (`docs/screenshots/interview_eval.png`)* |
| **Offer Acceptance Screen** | Student view with formal compensation details and decision buttons | *Placeholder (`docs/screenshots/student_offers.png`)* |

---

## 8. Getting Started

### Prerequisites
- **Python**: Version 3.12 or later
- **Node.js & npm**: Node.js v18.0.0+ (v24 LTS recommended) and npm v9+
- **MySQL Server**: Version 8.0+ running locally on port 3306
- **Git**: Version control system

---

### Step 1: Database Setup (MySQL)
Ensure your MySQL server is running on `127.0.0.1:3306`, then create the database schema:

```sql
CREATE DATABASE campus_hiring_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### Step 2: Django Backend Setup

1. **Clone repository and navigate to root**:
   ```bash
   git clone <repository_url>
   cd capspro
   ```

2. **Create and activate a Python virtual environment**:
   ```powershell
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Copy `.env.example` to `.env` and configure your local MySQL credentials:
   ```powershell
   # Windows
   copy .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```
   *(Update `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in `.env` to match your local MySQL configuration).*

5. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Verify system health**:
   ```bash
   python manage.py check
   ```

7. **Start the Django development server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
   The backend API will be running at `http://127.0.0.1:8000/`.

---

### Step 3: React Frontend Setup

1. **Open a new terminal and navigate to `frontend/`**:
   ```bash
   cd frontend
   ```

2. **Install frontend packages**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   Verify `frontend/.env` points to your backend API:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000/api
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```
   Open your browser at `http://localhost:5173/`.

5. **Build for production** (verified clean build):
   ```bash
   npm run build
   ```

---

### Step 4: Resume File Storage
- **Runtime Upload Directory**: Uploaded PDF resumes are stored under `media/resumes/`.
- **Database Storage**: The database stores only the relative path reference (e.g., `resumes/<filename>.pdf`), never raw PDF binary content.
- **Git Exclusion**: The `media/` directory and `media/resumes/` are explicitly listed in `.gitignore` and excluded from version control.

---

## 9. Environment Variables Table

### Backend (`.env` in repository root)

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `DB_NAME` | Yes | `campus_hiring_db` | Name of the MySQL database schema |
| `DB_USER` | Yes | `root` | MySQL database username |
| `DB_PASSWORD` | Yes | *(empty)* | Password for the MySQL database user |
| `DB_HOST` | Yes | `127.0.0.1` | Host address of the MySQL server |
| `DB_PORT` | Yes | `3306` | Port number of the MySQL server |
| `DEBUG` | No | `True` | Django debug mode (`True` for local dev, `False` for prod) |
| `SECRET_KEY` | Yes | *(dummy key)* | Cryptographic signing key for Django |
| `ALLOWED_HOSTS` | No | `127.0.0.1,localhost` | Comma-separated list of valid host headers |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Yes | `http://127.0.0.1:8000/api` | Base URL prefix for Django REST API endpoints |

---

## 10. API Documentation

Interactive OpenAPI 3.0 documentation is automatically generated by `drf-spectacular` and served by the Django backend:

- **Swagger UI**: [`http://127.0.0.1:8000/api/docs/`](http://127.0.0.1:8000/api/docs/)
- **Raw OpenAPI Schema**: [`http://127.0.0.1:8000/api/schema/`](http://127.0.0.1:8000/api/schema/)
- **Health Check Endpoint**: [`http://127.0.0.1:8000/api/health/`](http://127.0.0.1:8000/api/health/)

### Core REST API Endpoints

```text
Authentication:
  POST  /api/auth/register/student/    Register new student with bcrypt password hashing
  POST  /api/auth/register/company/    Register new recruiter with bcrypt password hashing
  POST  /api/auth/login/               Authenticate credentials and issue JWT tokens
  POST  /api/auth/refresh/             Generate new access token using refresh token
  GET   /api/auth/me/                  Fetch authenticated user profile and role

Profiles:
  GET   /api/students/profile/         Retrieve student academic credentials
  PATCH /api/students/profile/         Update student profile fields & upload PDF resume
  GET   /api/companies/profile/        Retrieve company organization profile
  PATCH /api/companies/profile/        Update company profile fields

Placement Drives:
  GET   /api/drives/                   List active placement drives (filter: ?mine=true)
  POST  /api/drives/                   Create new placement drive (Company only)
  GET   /api/drives/<id>/              Retrieve detailed drive information
  PATCH /api/drives/<id>/              Update drive criteria or active state (Company only)

Applications:
  GET   /api/applications/             List applications (filter: ?drive=<id>)
  POST  /api/applications/             Submit drive application with eligibility validation
  GET   /api/applications/<id>/        Retrieve comprehensive application details
  POST  /api/applications/<id>/shortlist/ Shortlist candidate (Company only)
  POST  /api/applications/<id>/reject/    Reject candidate with feedback reason (Company only)

Interviews:
  GET   /api/interviews/               List scheduled interviews for user/company
  POST  /api/interviews/               Schedule an interview round (Company only)
  PATCH /api/interviews/<id>/          Record interview outcome (passed: true/false)

Offers:
  GET   /api/offers/                   List received or extended job offers
  POST  /api/offers/                   Extend formal job offer (Company only)
  POST  /api/offers/<id>/respond/      Accept or reject job offer (Student only)

System:
  GET   /api/health/                   System health check and database status
```

---

## 11. Tests

The backend is validated by a comprehensive test suite implemented in **Pytest** with **pytest-django**, covering bcrypt password hashing, service layer business rules, automated eligibility verification, recruitment lifecycle state transitions, and API permission boundaries.

### Run the Test Suite
From the repository root with virtual environment activated:

```powershell
# Run all 61 tests
.\venv\Scripts\python.exe -m pytest

# Run with verbose output
.\venv\Scripts\python.exe -m pytest -v

# Run a specific test module
.\venv\Scripts\python.exe -m pytest tests/test_workflow_service.py
```

### Test Suite Structure & Coverage (61 Tests Passing)

```text
tests/
├── test_auth.py                 (9 tests: bcrypt hashing compliance, plaintext non-storage, API non-exposure, login, JWT refresh, PBKDF2 compatibility)
├── test_drive_service.py        (6 tests: creation, defaults, active queries, ID lookup)
├── test_application_service.py  (8 tests: CGPA eligibility, department rules, duplicates, history)
├── test_workflow_service.py     (14 tests: shortlisting, interviews, pass/fail, offers, rejections)
├── test_api_permissions.py      (7 tests: role boundaries, cross-user isolation, auth guards)
├── test_resume_storage.py       (3 tests: PDF upload via API, template view upload, DB path reference, media isolation)
└── hiring/tests.py              (14 tests: end-to-end integration and API test cases with bcrypt assertions)

Result: 61 passed in ~70s (100% pass rate, 0 failures)
```

---

## 12. Deployment

*Status: **Pending / TBD***  
*(Production cloud deployment will be configured in a subsequent milestone. Below is the planned architecture).*

### Planned Deployment Architecture
- **Web Server / Ingress**: Nginx reverse proxy serving static React build files (`frontend/dist/`) and forwarding `/api/` traffic.
- **Application Server**: Gunicorn WSGI running multiple worker processes for Django backend.
- **Database**: Managed MySQL 8.0 instance with automated backups and connection pooling.
- **Containerization**: Multi-stage `Dockerfile` and `docker-compose.yml` orchestrating frontend, backend, and MySQL services.

---

## 13. Folder Structure

```
capspro/
├── .env.example                       # Root environment configuration template
├── .gitignore                         # Git exclusion rules for secrets, venv, media, and builds
├── CHANGELOG.md                       # Semantic chronological history of project milestones
├── LICENSE                            # Standard MIT open-source license
├── Problem_Statement.md               # Formal capstone problem definition and scope
├── README.md                          # Comprehensive project documentation
├── manage.py                          # Django management script
├── pytest.ini                         # Pytest configuration file
├── requirements.txt                   # Backend Python package dependencies (including bcrypt)
├── config/                            # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                    # Database, JWT, CORS, PASSWORD_HASHERS config
│   ├── urls.py                        # Root URL dispatcher routing to /api/ and Swagger docs
│   └── wsgi.py
├── docs/                              # Project design and diagrams
│   └── diagrams/
│       ├── README.md                  # Diagram catalog and guidelines
│       ├── system_architecture.md     # 4-tier system architecture diagram
│       ├── er_diagram.md              # Entity-Relationship diagram and schema
│       ├── class_module_diagram.md    # Object-oriented class and module hierarchy
│       └── api_contract_diagram.md    # Sequential API workflow diagrams
├── frontend/                          # React 18 frontend single-page application
│   ├── .env.example                   # Frontend environment template
│   ├── index.html                     # HTML entry point
│   ├── package.json                   # Node package dependencies and scripts
│   ├── vite.config.js                 # Vite bundler configuration
│   ├── README.md                      # Frontend-specific quickstart and routing guide
│   └── src/
│       ├── api/                       # Central Axios client with JWT interceptor & URL normalization
│       ├── components/                # Reusable UI widgets (Navbar, StatCard, ProtectedRoute)
│       ├── context/                   # Global AuthContext & state store
│       ├── pages/                     # Routed pages (auth, student, company, drives)
│       ├── routes/                    # AppRoutes with role-based route guards
│       ├── App.jsx                    # Root application component
│       ├── index.css                  # Custom styling enhancements
│       └── main.jsx                   # Application entry point
├── hiring/                            # Core Django application
│   ├── api/                           # DRF REST API views and permission classes
│   ├── core/                          # API response formatters and exception handlers
│   ├── models/                        # Domain entities: Student, Company, Drive, App, etc.
│   ├── schemas/                       # DRF ModelSerializers and input serializers
│   └── services/                      # Decoupled business logic (drive, app, workflow)
├── media/                             # Runtime user uploads (Git-ignored)
│   └── resumes/                       # Student uploaded PDF resume files
└── tests/                             # Pytest automated test suite (61 tests)
```

---

## 14. Future Enhancements

The following capabilities are roadmap candidates for future milestones:
- **AI-Powered Resume Matcher**: Automated semantic scoring comparing candidate resumes with drive requirements.
- **Real-Time WebSockets**: Live candidate notifications for shortlist alerts and interview updates.
- **Automated Email Notifications**: Transactional emails dispatched upon application submission, interview scheduling, and offer letters.
- **Calendar Synchronization**: Google Calendar / Outlook integration for one-click interview scheduling.
- **Cloud Object Storage**: AWS S3 or Google Cloud Storage offloading for student PDF resume storage.
- **Advanced Placement Analytics**: University-wide placement statistics, average package visualizers, and department placement trends.

---

## 15. License

This project is open-source software licensed under the **[MIT License](LICENSE)**.  
See the `LICENSE` file for the full license text.

---

## 16. Author / Contact

- **Project**: Campus & Internship Hiring Platform
- **Track**: Python — Full-Stack Django & React Capstone
- **Institution / Cell**: College Placement & Training Cell
- **Year**: 2026
- **Repository**: [GitHub Repository](https://github.com/Monica0406/campus-hiring-platform)
