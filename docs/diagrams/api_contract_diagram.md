# REST API Contract & Flow Diagram

This diagram visualizes the sequential API contracts and interactions across the full recruitment lifecycle between the React Frontend, Django REST API, and backend services.

---

## 1. End-to-End Recruitment Workflow Sequence

```mermaid
sequenceDiagram
    autonumber
    actor StudentUser as Student (Browser)
    actor CompanyUser as Company (Browser)
    participant API as Django REST API (/api/)
    participant Auth as SimpleJWT / Auth
    participant DB as MySQL DB

    %% 1. Registration & Auth
    rect rgb(240, 248, 255)
        Note over StudentUser, DB: Authentication & Profile Setup
        StudentUser->>API: POST /api/auth/register/student/ {email, password, name, cgpa, department}
        API->>DB: Create User + Student Profile
        API-->>StudentUser: 201 Created {access, refresh, user}

        CompanyUser->>API: POST /api/auth/login/ {username, password}
        API->>Auth: Validate Credentials
        Auth-->>CompanyUser: 200 OK {access, refresh, role: "company"}
    end

    %% 2. Placement Drive Creation
    rect rgb(245, 255, 245)
        Note over CompanyUser, DB: Placement Drive Creation
        CompanyUser->>API: POST /api/drives/ [Bearer Token] {title, min_cgpa, allowed_departments, drive_date}
        API->>DB: Save Drive Record
        API-->>CompanyUser: 201 Created {id, title, is_active: true}
    end

    %% 3. Application Submission
    rect rgb(255, 250, 240)
        Note over StudentUser, DB: Drive Discovery & Application
        StudentUser->>API: GET /api/drives/ [Bearer Token]
        API-->>StudentUser: 200 OK [List of Active Drives]

        StudentUser->>API: POST /api/applications/ [Bearer Token] {drive_id}
        Note over API: Evaluates CGPA & Department eligibility
        API->>DB: Insert Application (Status: APPLIED)
        API-->>StudentUser: 201 Created {id, status: "APPLIED"}
    end

    %% 4. Shortlisting & Interview
    rect rgb(255, 245, 245)
        Note over CompanyUser, DB: Candidate Evaluation & Interview
        CompanyUser->>API: POST /api/applications/{id}/shortlist/ [Bearer Token]
        API->>DB: Update Application (Status: SHORTLISTED)
        API-->>CompanyUser: 200 OK {status: "SHORTLISTED"}

        CompanyUser->>API: POST /api/interviews/ [Bearer Token] {application_id, interview_date, mode}
        API->>DB: Insert Interview & Update App (Status: INTERVIEW_SCHEDULED)
        API-->>CompanyUser: 201 Created {id, status: "SCHEDULED"}

        CompanyUser->>API: PATCH /api/interviews/{id}/ [Bearer Token] {passed: true}
        API->>DB: Update Interview (Status: CLEARED) & App (Status: SELECTED)
        API-->>CompanyUser: 200 OK {status: "CLEARED"}
    end

    %% 5. Offer & Acceptance
    rect rgb(250, 240, 255)
        Note over CompanyUser, StudentUser: Job Offer Issuance & Decision
        CompanyUser->>API: POST /api/offers/ [Bearer Token] {application_id, position, salary}
        API->>DB: Insert Offer (Status: PENDING) & Update App (Status: OFFERED)
        API-->>CompanyUser: 201 Created {id, status: "PENDING", position, salary}

        StudentUser->>API: GET /api/offers/ [Bearer Token]
        API-->>StudentUser: 200 OK [List of Student Offers]

        StudentUser->>API: POST /api/offers/{id}/respond/ [Bearer Token] {accept: true}
        API->>DB: Update Offer (Status: ACCEPTED)
        API-->>StudentUser: 200 OK {id, status: "ACCEPTED"}
    end
```

---

## 2. API Endpoint Catalog

| Method | Endpoint | Access Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register/student/` | Public | Register new student account and academic profile |
| `POST` | `/api/auth/register/company/` | Public | Register new recruiter account and company profile |
| `POST` | `/api/auth/login/` | Public | Authenticate user credentials and return JWT tokens |
| `POST` | `/api/auth/refresh/` | Public | Refresh expired access token using refresh token |
| `GET` | `/api/auth/me/` | Authenticated | Fetch current user session details and profile |
| `GET` | `/api/students/profile/` | Student | Retrieve student academic profile |
| `PATCH`| `/api/students/profile/` | Student | Update student profile information |
| `GET` | `/api/companies/profile/`| Company | Retrieve company profile |
| `PATCH`| `/api/companies/profile/`| Company | Update company profile information |
| `GET` | `/api/drives/` | Authenticated | List all active placement drives |
| `POST` | `/api/drives/` | Company | Create a new campus placement drive |
| `GET` | `/api/drives/{id}/` | Authenticated | Retrieve details for a specific drive |
| `PATCH`| `/api/drives/{id}/` | Company | Update drive details, deadline, or active status |
| `GET` | `/api/applications/` | Authenticated | List user applications or company drive applicants |
| `POST` | `/api/applications/` | Student | Apply to a placement drive with eligibility validation |
| `GET` | `/api/applications/{id}/` | Participant | Retrieve comprehensive application details |
| `POST` | `/api/applications/{id}/shortlist/` | Company | Transition application status to SHORTLISTED |
| `POST` | `/api/applications/{id}/reject/` | Company | Transition application status to REJECTED |
| `GET` | `/api/interviews/` | Authenticated | List student's or company's scheduled interviews |
| `POST` | `/api/interviews/` | Company | Schedule interview for shortlisted candidate |
| `PATCH`| `/api/interviews/{id}/` | Company | Record interview outcome (passed: true/false) |
| `GET` | `/api/offers/` | Authenticated | List student's received or company's extended offers |
| `POST` | `/api/offers/` | Company | Extend formal job offer to cleared candidate |
| `POST` | `/api/offers/{id}/respond/` | Student | Accept or decline extended job offer |
| `GET` | `/api/health/` | Public | Health check reporting DB engine and API status |
