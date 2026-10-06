# Campus Hiring Platform - React Frontend

Modern, student-friendly frontend interface for the Campus & Internship Hiring Platform capstone project. Built with React 18, Vite, Bootstrap 5, and Axios, fully integrated with the Django REST API backend.

---

## 1. Prerequisites & Environment Setup

- **Node.js**: v18.0.0 or later (v24 LTS recommended)
- **npm**: v9.0.0 or later
- **Python**: v3.12+ (for Django backend)
- **MySQL**: 8.0+ running with the project database

### Environment Variables

The frontend reads configuration from `.env` in the `frontend/` directory:

```bash
# frontend/.env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

An example file is provided at `frontend/.env.example`.

---

## 2. Installation & Quick Start

### Install Dependencies

From the `frontend/` directory:

```bash
cd frontend
npm install
```

### Run the Frontend Development Server

```bash
npm run dev
```

The Vite dev server will start at `http://localhost:5173/`.

### Build for Production

To create an optimized production bundle:

```bash
npm run build
```

The build output will be placed in the `frontend/dist/` folder.

---

## 3. Running Backend and Frontend Together

### Terminal 1: Django Backend Server

From the project root (`capspro/`):

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# or: source venv/bin/activate  # Linux/macOS

# Ensure database migrations are applied
python manage.py migrate

# Run Django dev server on port 8000
python manage.py runserver 127.0.0.1:8000
```

The Django REST API will be live at `http://127.0.0.1:8000/api/`.

### Terminal 2: React Frontend Server

From the `frontend/` directory:

```bash
cd frontend
npm run dev
```

Open your browser at `http://localhost:5173/`.

---

## 4. Frontend Architecture & Folder Structure

```
frontend/
├── public/                 # Static public assets
├── src/
│   ├── api/
│   │   └── client.js       # Central Axios client with JWT interceptor & auto-refresh
│   ├── components/
│   │   ├── AlertMessage.jsx    # Dismissible Bootstrap alerts
│   │   ├── LoadingSpinner.jsx  # Reusable loading spinner
│   │   ├── Navbar.jsx          # Dynamic role-based navigation header
│   │   ├── ProtectedRoute.jsx  # Route guard for authentication and roles
│   │   ├── StatCard.jsx        # Metric and KPI counter card
│   │   └── StatusBadge.jsx     # Status badge with semantic color codes
│   ├── context/
│   │   └── AuthContext.jsx # Global auth state (login, logout, refresh, user)
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.jsx           # User authentication
│   │   │   ├── RegisterStudent.jsx # Student registration with academic profile
│   │   │   └── RegisterCompany.jsx # Company registration with company profile
│   │   ├── company/
│   │   │   ├── CompanyDashboard.jsx         # Recruiter overview & metrics
│   │   │   ├── CompanyProfile.jsx           # Manage company info
│   │   │   ├── CompanyDrives.jsx            # List company drives
│   │   │   ├── CreateDrive.jsx              # Create new drive
│   │   │   ├── EditDrive.jsx                # Update drive details
│   │   │   ├── DriveApplicants.jsx          # Review applicants, shortlist/reject
│   │   │   ├── CompanyApplicationDetail.jsx # Candidate view with interview/offer modals
│   │   │   ├── CompanyInterviews.jsx        # Manage interviews, record pass/fail
│   │   │   └── CompanyOffers.jsx            # Track extended offers & student response
│   │   ├── drives/
│   │   │   ├── DriveList.jsx        # Public / browsable list of drives
│   │   │   └── DriveDetail.jsx      # Drive details & Student one-click apply
│   │   ├── student/
│   │   │   ├── StudentDashboard.jsx         # Student stats, next interview, recent apps
│   │   │   ├── StudentProfile.jsx           # View and update academic GPA/branch/skills
│   │   │   ├── StudentApplications.jsx      # List all student submissions
│   │   │   ├── StudentApplicationDetail.jsx # Application timeline and details
│   │   │   ├── StudentInterviews.jsx        # Scheduled interviews with details
│   │   │   └── StudentOffers.jsx            # Received offers with Accept/Reject actions
│   │   ├── Home.jsx        # Landing page with portal highlights
│   │   └── NotFound.jsx    # 404 page
│   ├── routes/
│   │   └── AppRoutes.jsx   # Client-side routing configuration
│   ├── App.jsx             # Main application layout with Nav & Footer
│   ├── index.css           # Custom styles & design tokens
│   └── main.jsx            # App root mounting
├── index.html              # HTML entry point
├── package.json            # Node dependencies and scripts
└── vite.config.js          # Vite configuration
```

---

## 5. Page and Routing Overview

| Route | Access | Description |
| :--- | :--- | :--- |
| `/` | Public | Homepage featuring portal stats, key workflows, and CTAs |
| `/login` | Public | Login for students and company recruiters |
| `/register/student` | Public | Student signup with GPA, department, and skills |
| `/register/company` | Public | Company recruiter signup with company profile |
| `/drives` | Public | Placement drives catalog with branch & title search |
| `/drives/:id` | Public | Drive details with eligibility criteria and apply action |
| `/student/dashboard` | Student | Student dashboard showing KPIs, active apps, upcoming interviews |
| `/student/profile` | Student | Academic profile viewer and GPA/skills editor |
| `/student/applications` | Student | Student's submitted applications with status badges |
| `/student/applications/:id` | Student | Detailed timeline and status of an application |
| `/student/interviews` | Student | Scheduled interview details and timings |
| `/student/offers` | Student | Extended offers with one-click Accept or Reject buttons |
| `/company/dashboard` | Company | Recruiter dashboard with drives, candidates, and hiring KPIs |
| `/company/profile` | Company | Company recruiter profile viewer and editor |
| `/company/drives` | Company | Company's placement drives management |
| `/company/drives/create` | Company | Create a new campus placement drive |
| `/company/drives/:id/edit` | Company | Edit an existing placement drive |
| `/company/drives/:id/applicants` | Company | Review candidates, shortlist or reject applicants |
| `/company/applications/:id` | Company | Detailed candidate view with interview/offer workflow actions |
| `/company/interviews` | Company | Review interviews and record Pass / Fail outcomes |
| `/company/offers` | Company | Track job offers sent and student acceptance status |
| `*` | Public | 404 Not Found page |

---

## 6. Authentication & JWT Interceptor

The frontend handles JWT authentication seamlessly via Axios interceptors in `src/api/client.js`:
- Attaches `Authorization: Bearer <access_token>` to every authenticated request.
- When an API response returns `401 Unauthorized`, the interceptor automatically attempts to refresh the access token using `POST /api/auth/refresh/` with the stored refresh token.
- If refresh succeeds, the failed request is replayed transparently without interrupting the user.
- If refresh fails (or the refresh token expired), stored tokens are cleared and the user is redirected to `/login`.
