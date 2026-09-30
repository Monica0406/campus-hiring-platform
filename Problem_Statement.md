# Problem Statement

## 1. Project Title

**Internship & Campus Hiring Platform**

---

## 2. Domain

**HRTech / Campus Recruitment & University Placement Automation**

---

## 3. Target Users

1. **College / University Students**: Undergraduate and postgraduate students seeking internships and full-time campus placement opportunities.
2. **Company Recruiters / Corporate HRs**: Enterprise and startup talent acquisition teams seeking to hire university talent.
3. **Training & Placement Cell (T&P)**: Academic placement officers coordinating recruitment drives, eligibility rules, and interview processes.

---

## 4. Problem

Campus recruitment activities in universities and colleges are frequently managed using disparate, manual tools such as spreadsheets, group emails, chat groups, and shared forms. This fragmented approach causes several critical operational bottlenecks:

- **Information Asymmetry**: Students frequently miss application deadlines, eligibility criteria updates, and interview schedules.
- **Manual Eligibility Verification**: Placement coordinators and recruiters must manually verify students' CGPA, department, and backlog criteria against drive requirements, resulting in errors and delays.
- **Duplicate & Inconsistent Applications**: Without centralized database constraints, students can inadvertently submit multiple applications for the same drive.
- **Fragmented Communication**: Interview invites, feedback, and job offers lack a unified audit trail, leading to confusion and student anxiety.
- **Lack of Real-Time Analytics**: Neither companies nor universities have real-time visibility into application metrics, shortlisting rates, and offer acceptance status.

---

## 5. Proposed Solution

The **Internship & Campus Hiring Platform** solves these challenges by providing a secure, centralized, role-based web application connecting students and recruiters through automated recruitment workflows.

Key capabilities provided:
- **Role-Based Authentication**: Secure JWT-based authentication for Students and Company Recruiters with dedicated permissions.
- **Academic Profile Management**: Students maintain their academic profile (CGPA, department, college, uploaded PDF resume).
- **Placement Drive Management**: Recruiters create and publish placement drives with defined eligibility criteria (minimum CGPA, allowed departments, deadlines).
- **Automated Eligibility Engine**: Business logic automatically validates student CGPA and department against drive criteria before accepting applications.
- **Duplicate Prevention**: Database-level unique constraints and service validation prevent duplicate applications.
- **Recruitment Lifecycle Tracking**: Strict finite-state transitions across recruitment stages:
  $$\text{APPLIED} \longrightarrow \text{SHORTLISTED} \longrightarrow \text{INTERVIEW\_SCHEDULED} \longrightarrow \text{SELECTED} \longrightarrow \text{OFFERED}$$
  with explicit rejection handling at each evaluation stage.
- **Interview Scheduling & Evaluation**: Recruiters schedule interviews (online or in-person) and record evaluation outcomes.
- **Job Offer Management**: Formal employment offers extended to successful candidates with one-click student acceptance or rejection.

---

## 6. Core Database Entities

The relational database model comprises six interconnected domain entities:

| Entity | Table Name | Purpose & Cardinality |
| :--- | :--- | :--- |
| **Student** | `hiring_student` | Student academic credentials, CGPA, department, and resume. 1-to-1 with `auth_user`. |
| **Company** | `hiring_company` | Recruiter profile and organization information. 1-to-1 with `auth_user`. |
| **Drive** | `hiring_drive` | Placement drives with eligibility constraints. Belongs to a Company (N:1). |
| **Application** | `hiring_application` | Connects a Student to a Drive. Enforces `UniqueConstraint(student, drive)` (N:1 to Student, N:1 to Drive). |
| **Interview** | `hiring_interview` | Interview round schedule, mode, and outcome for an Application (N:1 to Application). |
| **Offer** | `hiring_offer` | Formal employment offer detailing position, salary, and decision status (N:1 to Application). |

---

## 7. User Roles & Permissions

### Role 1: Student
- Register new student account with academic credentials (CGPA, department, college, resume).
- Authenticate and manage JWT session.
- View and update academic profile information.
- Browse all active placement drives and inspect eligibility criteria.
- Apply to eligible placement drives (blocked if criteria not met or duplicate application).
- Track submitted applications through real-time status badges.
- View scheduled interview dates, times, and meeting modes.
- Review formal job offers and record decision (Accept or Reject).

### Role 2: Company Recruiter
- Register company profile (company name, recruiter email, location).
- Authenticate and manage JWT session.
- Create, edit, and manage placement drives with eligibility thresholds.
- View applicants for company drives with status filters (Applied, Shortlisted, Interviewed, Offered, Rejected).
- Shortlist qualified candidates or reject with feedback reasons.
- Schedule interviews with date/time and mode (Online or In-Person).
- Record interview outcomes (Pass / Fail).
- Extend formal employment offers with position title and annual compensation.
- Monitor student acceptance decisions in real time.

---

## 8. Success Criteria

1. **Authentication Integrity**: Students and company recruiters securely register, authenticate, and receive verifiable JWT tokens.
2. **Role Isolation**: Strict permission boundaries prevent students from accessing recruiter tools (e.g., creating drives, reviewing other applicants) and recruiters from applying to drives.
3. **Automated Eligibility Enforcement**: Students failing CGPA or department criteria are rejected with informative feedback before application persistence.
4. **Duplicate Prevention**: Re-applying to the same drive is strictly disallowed at both service and database constraint levels.
5. **State Machine Integrity**: Recruitment transitions strictly obey the valid lifecycle order; offers cannot be created without passing an interview, and closed applications cannot transition invalidly.
6. **Data Consistency**: All relational entities remain consistent across MySQL with foreign key cascading and atomic transactions.
7. **Frontend Usability**: Intuitive, responsive React UI enabling students and recruiters to complete their respective workflows smoothly.
8. **Automated Test Quality**: 100% pass rate across the comprehensive Pytest suite covering all services, workflows, and API permissions.

---

## 9. Out of Scope

The current implementation focuses on core recruitment workflow automation. The following capabilities are explicitly out of scope for the current milestone:
- Online payment gateway integration for placement fees.
- Real-time WebRTC live video streaming within the browser (interviews use external links or in-person venues).
- Instant peer-to-peer chat messaging between candidates and recruiters.
- Advanced AI/LLM resume parsing or algorithmic candidate ranking (reserved for future enhancement).
- External third-party job board integrations (e.g., LinkedIn, Indeed).
- Multi-tenant enterprise SSO (SAML / OAuth2 / Google Workspace).

---

## 10. Chosen Python Track

- **Track**: Python — Full-Stack Web Application with Django
- **Backend**: Python 3.12+ / Django 5+ & Django REST Framework (DRF)
- **Authentication**: `djangorestframework-simplejwt` (stateless JWT tokens)
- **Database**: MySQL 8.0+ connected via `mysqlclient`
- **Testing**: `pytest` and `pytest-django`
- **Frontend**: React 18 Single-Page Application (Vite + Bootstrap 5 + Axios + React Router v6)