# System Architecture Diagram

This document illustrates the four-tier layered architecture of the **Campus & Internship Hiring Platform**, depicting the interactions between client layers, API gateways, business domain services, persistence engines, external services, and hosting infrastructure.

---

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph ClientLayer ["Client Presentation Tier (Browser)"]
        UI["React 18 Single Page Application<br/>(Vite + Bootstrap 5 + React Router)"]
        AuthContext["Auth Context & State Store"]
        AxiosClient["Axios HTTP Client<br/>(JWT Interceptors & Auto Refresh)"]
        UI --> AuthContext
        UI --> AxiosClient
    end

    subgraph Hosting ["Hosting & Deployment (Infrastructure Placeholder)"]
        WebGateway["Reverse Proxy & Gateway<br/>(Nginx / Cloud Ingress / Docker - TBD)"]
    end

    subgraph APILayer ["API & Routing Tier (Django REST Framework)"]
        URLRouter["Django URL Dispatcher (/api/*)"]
        AuthMiddleware["JWT Authentication Middleware<br/>(SimpleJWT Bearer Token)"]
        Permissions["Role Permission Layer<br/>(IsStudent, IsCompany, IsParticipant)"]
        ViewControllers["API View Layer<br/>(Auth, Drives, Applications, Interviews, Offers)"]
        Serializers["DRF Serializers<br/>(Input Validation & Serialization)"]

        URLRouter --> AuthMiddleware
        AuthMiddleware --> Permissions
        Permissions --> ViewControllers
        ViewControllers <--> Serializers
    end

    subgraph ServiceLayer ["Business Logic & Service Layer (Domain)"]
        AuthService["Django Auth Services"]
        DriveService["Drive Service<br/>(hiring.services.drive_service)"]
        AppService["Application Service<br/>(hiring.services.application_service)"]
        WorkflowService["Workflow Service<br/>(hiring.services.hiring_workflow_service)"]
    end

    subgraph PersistenceLayer ["Persistence Tier (Database)"]
        ORM["Django Object-Relational Mapper (ORM)"]
        MySQL[("MySQL 8.0 Relational Database<br/>(campus_hiring_db)")]
        MediaStorage[("Local / Cloud Media Storage<br/>(Student Resumes)")]
    end

    subgraph ExternalServices ["External / Third-Party Services (Placeholder)"]
        EmailService["Transactional Email Service<br/>(SMTP / SendGrid - TBD)"]
        StorageService["S3 / Cloud Blob Storage<br/>(Future Resume Storage - TBD)"]
    end

    %% Network flows
    AxiosClient -->|"HTTPS / REST (JSON)"| WebGateway
    WebGateway -->|"WSGI / ASGI"| URLRouter

    ViewControllers --> AuthService
    ViewControllers --> DriveService
    ViewControllers --> AppService
    ViewControllers --> WorkflowService

    AuthService --> ORM
    DriveService --> ORM
    AppService --> ORM
    WorkflowService --> ORM

    ORM -->|"TCP / Port 3306"| MySQL
    ORM -->|"File IO"| MediaStorage

    WorkflowService -.->|"Notifications (TBD)"| EmailService
    MediaStorage -.->|"Sync / Offload (TBD)"| StorageService
```

---

## 2. Layer Description

### A. Client Presentation Tier
- **Framework**: React 18 with Vite bundling.
- **Styling**: Bootstrap 5 responsive grid with custom modern design tokens.
- **Client Networking**: Axios configured with request interceptors for Bearer token injection and response interceptors to transparently catch `401 Unauthorized`, refresh expired tokens via `/api/auth/refresh/`, and replay requests.

### B. Hosting & Deployment Tier (Placeholder)
- Serves the static React build (`dist/`) and proxies `/api/` traffic to the Django WSGI application server (Gunicorn/Uvicorn).
- Production deployment configuration is currently pending/TBD.

### C. API & Controller Tier
- **Framework**: Django REST Framework (DRF) running Django 5+.
- **Authentication**: Stateless JSON Web Tokens (`djangorestframework-simplejwt`).
- **Authorization**: Role-based access control checking `user.student_profile` vs. `user.company_profile`.

### D. Service & Business Logic Tier
- Decoupled from Django HTTP views, ensuring business rules can be verified in isolation:
  - `drive_service`: Drive creation, validation, active drive filters.
  - `application_service`: GPA and department eligibility checks, duplicate prevention.
  - `hiring_workflow_service`: Finite-state machine enforcing strict recruitment transitions.

### E. Persistence Tier
- **Database Engine**: MySQL 8.0+ connected via `mysqlclient`.
- **Relational Integrity**: Enforced through foreign keys and unique constraints (`UniqueConstraint(student, drive)`).

### F. External Services (Placeholder)
- External email and file storage APIs for automated notifications and scalable cloud resume storage.
