# Entity-Relationship (ER) Diagram

This diagram represents the relational data model for the **Campus & Internship Hiring Platform**, matching the actual MySQL database schema and Django ORM models.

---

## 1. Relational Schema & Entity Diagram

```mermaid
erDiagram
    AUTH_USER ||--o| STUDENT : "has one profile (1:1)"
    AUTH_USER ||--o| COMPANY : "has one profile (1:1)"
    
    COMPANY ||--o{ DRIVE : "hosts (1:N)"
    
    STUDENT ||--o{ APPLICATION : "submits (1:N)"
    DRIVE ||--o{ APPLICATION : "receives (1:N)"
    
    APPLICATION ||--o{ INTERVIEW : "schedules (1:N)"
    APPLICATION ||--o{ OFFER : "results in (1:N)"

    AUTH_USER {
        int id PK
        string username
        string email
        string password
        boolean is_active
        datetime date_joined
    }

    STUDENT {
        int id PK
        int user_id FK "Unique (1:1 to auth_user)"
        string name
        string email "Unique"
        string college
        string department
        decimal cgpa "max_digits 3, decimal_places 2"
        string resume "FileField (resumes/)"
    }

    COMPANY {
        int id PK
        int user_id FK "Unique (1:1 to auth_user)"
        string company_name
        string email "Unique"
        string location
    }

    DRIVE {
        int id PK
        int company_id FK "References COMPANY(id)"
        string title
        text description
        decimal min_cgpa "max_digits 3, decimal_places 2"
        string allowed_departments "Comma-separated or 'All'"
        text eligibility
        date drive_date
        boolean is_active "Default True"
    }

    APPLICATION {
        int id PK
        int student_id FK "References STUDENT(id)"
        int drive_id FK "References DRIVE(id)"
        datetime applied_date "auto_now_add"
        string status "APPLIED | SHORTLISTED | INTERVIEW_SCHEDULED | SELECTED | OFFERED | REJECTED"
    }

    INTERVIEW {
        int id PK
        int application_id FK "References APPLICATION(id)"
        datetime interview_date
        string mode "Online | In-Person"
        string status "SCHEDULED | CLEARED | FAILED | CANCELLED"
    }

    OFFER {
        int id PK
        int application_id FK "References APPLICATION(id)"
        date offer_date "auto_now_add"
        string position
        decimal salary "max_digits 10, decimal_places 2"
        string status "PENDING | ACCEPTED | REJECTED"
    }
```

---

## 2. Entity Descriptions & Constraints

### 1. `auth_user` (Django Auth)
- Built-in authentication table handling user credentials, password hashes (PBKDF2/argon2), and active state.

### 2. `Student` (`hiring_student`)
- Stores student identity, academic credentials, and uploaded resume document.
- Linked one-to-one with `auth_user`.
- Enforces unique email constraint.

### 3. `Company` (`hiring_company`)
- Stores enterprise profile and recruitment point-of-contact details.
- Linked one-to-one with `auth_user`.
- Enforces unique email constraint.

### 4. `Drive` (`hiring_drive`)
- Campus recruitment drives posted by companies.
- Defines criteria: `min_cgpa` and `allowed_departments` checked during application submission.
- Foreign key: `company_id` (`ON DELETE CASCADE`).

### 5. `Application` (`hiring_application`)
- Relates a student to a drive they have applied for.
- **Unique Constraint**: `UniqueConstraint(student, drive)` strictly prevents duplicate submissions.
- Managed by finite-state transitions in `hiring_workflow_service`.

### 6. `Interview` (`hiring_interview`)
- Scheduled interviews associated with an application.
- Foreign key: `application_id` (`ON DELETE CASCADE`).
- Tracks date/time, mode (`Online` / `In-Person`), and outcome (`SCHEDULED`, `CLEARED`, `FAILED`, `CANCELLED`).

### 7. `Offer` (`hiring_offer`)
- Employment offer extended to candidates who successfully clear interviews.
- Tracks CTC/salary, job role title, and student decision (`PENDING`, `ACCEPTED`, `REJECTED`).
