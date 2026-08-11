# Internship & Campus Hiring Platform

> A Django-based platform for managing campus hiring activities by connecting students and companies through a centralized system.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Architecture Diagram](#architecture-diagram)
- [ER Diagram](#er-diagram)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Current Project Status](#current-project-status)
- [Future Enhancements](#future-enhancements)

---

## Overview

The Internship & Campus Hiring Platform is designed to support campus hiring activities by connecting students and companies through a centralized web application.

The current implementation provides student and company registration and login, password hashing, dashboards, session-based authentication, resume upload, PDF validation, and the core database models required for placement drives, applications, interviews, and offers.

The project is currently under active development as a Python/Django capstone project.

---

## Problem Statement

The detailed problem statement for the project is documented in:

`Problem_Statement.md`

The problem statement defines the target users, proposed solution, user roles, core entities, project scope, and expected outcomes of the platform.

---

## Architecture Diagram

The current implementation follows a Django-based web application architecture.

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
              (Frontend/UI)              (Application Logic)
                                                  |
                                                  v
                                           Django ORM
                                                  |
                                                  v
                                           Core Models
                                                  |
              +---------------+-------------------+----------------+
              |               |                   |                |
              v               v                   v                v
           Student         Company              Drive         Application
                                                                    |
                                                            +-------+-------+
                                                            |               |
                                                            v               v
                                                        Interview         Offer
                                                                    |
                                                                    v
                                                              SQLite Database
   ```

## ER Diagram

The Entity Relationship diagram represents the relationships between the major entities in the campus hiring platform, including students, companies, placement drives, applications, interviews, and offers.

## Tech Stack

## Current Implementation
## Layer	                              Technology
Programming Language	                       Python
Backend Framework	                       Django
ORM	                                     Django ORM
Frontend	                              HTML, CSS, Django Templates
Database	                              SQLite
Authentication	                       Password hashing and session-based login
File Uploads	                              Django Media Files
Configuration	                              .env environment variables
Version Control	                       Git
Repository Hosting	                       GitHub


## Planned / Target Technologies

The following technologies are planned for subsequent development phases:

Django REST Framework / REST API
React frontend
PostgreSQL or MySQL database
Pytest-based automated testing
Swagger / OpenAPI API documentation
GitHub Actions CI/CD
Production deployment

## Features
## Student Module
Student registration
Student login
Password hashing
Session-based authentication
Student dashboard
Student profile information
Resume upload
PDF resume validation
Resume storage using Django media files
## Company Module
Company registration
Company login
Password hashing
Session-based authentication
Company dashboard
## Campus Hiring Data Model
The core database structure has been created for:

Placement Drive
Application
Interview
Offer

These models provide the foundation for the complete campus hiring workflow that will be implemented in the upcoming development phases.     

## Flow Structure

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
│       └── ER_Diagram.png
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
│   │   ├── home.html
│   │   ├── student_register.html
│   │   ├── student_login.html
│   │   ├── student_dashboard.html
│   │   ├── company_register.html
│   │   ├── company_login.html
│   │   └── company_dashboard.html
│   │
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── media/
│   └── resumes/
│
├── manage.py
├── Problem_Statement.md
├── README.md
├── .env
└── .gitignore

## Current Project Status

### Completed

- Django project setup
- Student registration and login
- Company registration and login
- Student and company dashboards
- Password hashing and session-based authentication
- Resume PDF upload and validation
- Core hiring models
- Database migrations
- `.env` configuration
- ER diagram

### In Progress

- Placement drive management
- Student application workflow
- Interview and offer management
- REST API implementation
- React frontend
- Automated testing

## Future Enhancements

- Placement drive management
- Student application workflow
- Interview and offer management
- Django REST APIs
- React frontend
- Automated testing
- API documentation
- Production deployment