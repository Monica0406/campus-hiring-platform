# Internship & Campus Hiring Platform

> A Django-based platform for managing campus hiring activities by connecting students and companies through a centralized system.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Architecture Diagram](#architecture-diagram)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Current Project Status](#current-project-status)
- [License](#license)


---

## Overview

The Internship & Campus Hiring Platform is designed to support campus hiring activities by connecting students and companies through a centralized web application.

The platform provides student and company registration and login, student dashboards, resume management, and the foundation for managing placement drives, applications, interviews, and offers.

The project is currently under active development as a Python/Django capstone project.

---

## Problem Statement

The detailed problem statement for the project is documented in:

`Problem_Statement.md`

The problem statement defines the target users, proposed solution, core entities, user roles, scope, and expected outcomes of the platform.

---

## Architecture Diagram

The system architecture follows a Django-based web application structure.

The current implementation consists of:

```text
                    Internship & Campus Hiring Platform
                                   |
                                   v
                         Django Web Application
                                   |
                    +--------------+--------------+
                    |                             |
                    v                             v
             Django Templates              Django Views
             (Frontend/UI)                 (Application Logic)
                                                  |
                                                  v
                                           Django ORM
                                                  |
                                                  v
                                           Core Models
                                                  |
                    +--------------+--------------+--------------+
                    |              |              |              |
                    v              v              v              v
                Student         Company          Drive       Application
                                                                  |
                                                          +-------+-------+
                                                          |               |
                                                          v               v
                                                      Interview         Offer
                                                                  |
                                                                  v
                                                            SQLite Database
```
## Tech Stack
### Current Implementation

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Django |
| ORM | Django ORM |
| Frontend | HTML, Django Templates |
| Database | SQLite |
| Authentication | Django authentication utilities and session-based login |
| File Uploads | Django Media Files |
| Version Control | Git |
| Repository Hosting | GitHub |

### Planned / Target Technologies

As development progresses according to the capstone requirements, the project is planned to include:

- Django REST Framework / REST API
- React frontend
- PostgreSQL or MySQL database
- Pytest-based automated testing
- Swagger / OpenAPI API documentation
- GitHub Actions CI/CD
- Production deployment

## Features

### Student Module

- Student registration
- Student login
- Student dashboard
- Student profile information
- Password hashing
- Session-based authentication
- Resume upload
- PDF resume validation

### Company Module

- Company registration
- Company login
- Company dashboard
- Password hashing
- Session-based authentication

### Campus Hiring Module

- Placement Drive model
- Application model
- Interview model
- Offer model

## Folder Structure
```text

CAPSPRO/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── docs/
│   └── diagrams/
│
├── hiring/
│   ├── api/
│   │   └── __init__.py
│   │
│   ├── core/
│   │   └── __init__.py
│   │
│   ├── migrations/
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── company.py
│   │   ├── drive.py
│   │   ├── application.py
│   │   ├── interview.py
│   │   └── offer.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   ├── templates/
│   │
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── media/
├── manage.py
├── Problem_Statement.md
├── README.md
└── .gitignore
```

## Current Project Status

The project is currently under active development.

### Completed Areas

- Django project setup
- Student registration and login
- Company registration and login
- Student and company dashboards
- Resume upload and validation
- Core campus hiring models
- Database migrations
- Environment variable configuration

### In Progress

- Architecture documentation
- ER diagram
- Class / Module diagram
- REST API implementation
- Automated testing
- API documentation
- Deployment configuration
- CI/CD

## License

This project is developed as a Python capstone project.