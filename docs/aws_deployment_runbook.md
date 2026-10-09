# AWS Production Deployment Runbook

> **Campus & Internship Hiring Platform**  
> Comprehensive operational guide for cloud infrastructure architecture, environment configuration, deployment procedures, and troubleshooting.

---

## 1. Cloud Architecture Overview

The platform is architected for deployment across managed AWS services providing security, scalability, and automated operations:

```text
+-----------------------------------------------------------------------------------+
|                                 Client (Browser)                                  |
+----------------------------------------+------------------------------------------+
                                         |
               +-------------------------+-------------------------+
               | HTTPS (Custom Domain / *.amplifyapp.com)          | HTTPS (*.awsapprunner.com)
               v                                                   v
+-----------------------------+                           +-----------------------------+
|         AWS Amplify         |                           |       AWS App Runner        |
|  - React 18 SPA (Vite)      |                           |  - Django 6.0+ REST API     |
|  - amplify.yml build spec   |                           |  - Gunicorn WSGI (3 workers)|
|  - SPA 200 Rewrite Rule     |                           |  - WhiteNoise static files  |
+-----------------------------+                           +--------------+--------------+
                                                                         |
                                         +-------------------------------+-------------------------------+
                                         | TLS (VERIFY_IDENTITY)                                         | IAM Task Role
                                         v                                                               v
                          +-----------------------------+                                 +-----------------------------+
                          |   Amazon RDS (MySQL 8.0)    |                                 |      Amazon S3 (Private)    |
                          |  - Private VPC Subnet       |                                 |  - Candidate PDF Resumes    |
                          |  - Multi-AZ High Availability|                                |  - Block Public Access (all)|
                          |  - TLS Encryption in transit|                                 |  - Pre-signed Temporary URLs|
                          +-----------------------------+                                 +-----------------------------+
```

| Component | Target Service | Runtime / Specification | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend** | AWS Amplify Hosting | Node.js 22+ / React 18 / Vite | Serves static SPA assets with continuous deployment |
| **Backend API** | AWS App Runner / ECS | Python 3.14-slim / Gunicorn | Containerized stateless Django REST API |
| **Database** | Amazon RDS for MySQL | MySQL 8.0 Community Edition | Managed relational persistence with automated backups |
| **Media Storage** | Amazon S3 | Private Object Storage Bucket | Secure storage of uploaded candidate PDF resumes |
| **Static Assets** | WhiteNoise | Compressed & Manifest-Cached | Serves Django admin and Swagger UI assets |

---

## 2. Environment Variables Specification

> **Security Notice**: Never commit real secret keys, passwords, or AWS credentials to version control. Set these variables directly in AWS Management Console or AWS Secrets Manager.

### Backend Environment Variables (AWS App Runner / ECS)

| Variable | Required | Example / Recommended | Description |
| :--- | :--- | :--- | :--- |
| `DEBUG` | **No** (defaults to `False`) | `False` | Disables debug mode in production |
| `SECRET_KEY` | **Yes** | *(64-char random hex string)* | Cryptographic signing key |
| `ALLOWED_HOSTS` | **Yes** | `your-service.awsapprunner.com` | Comma-separated trusted Host headers |
| `CORS_ALLOWED_ORIGINS` | **Yes** | `https://main.d123.amplifyapp.com` | Comma-separated allowed frontend origins |
| `USE_SECURE_PROXY_SSL_HEADER` | **Yes** | `True` | Trusts `X-Forwarded-Proto: https` from App Runner proxy |
| `SESSION_COOKIE_SECURE` | No (auto `True` in prod) | `True` | Ensures session cookies are transmitted over HTTPS only |
| `CSRF_COOKIE_SECURE` | No (auto `True` in prod) | `True` | Ensures CSRF cookies are transmitted over HTTPS only |
| `SECURE_SSL_REDIRECT` | No | `False` | TLS is already enforced at App Runner edge proxy |
| `DJANGO_LOG_LEVEL` | No | `INFO` | Logging level for Django framework |
| `APP_LOG_LEVEL` | No | `INFO` | Logging level for `hiring` application logic |
| `DB_NAME` | **Yes** | `campus_hiring_db` | MySQL database name |
| `DB_USER` | **Yes** | `dbadmin` | Master database username |
| `DB_PASSWORD` | **Yes** | *(secure master password)* | Master database password |
| `DB_HOST` | **Yes** | `mydb.c123.us-east-1.rds.amazonaws.com` | RDS instance endpoint |
| `DB_PORT` | No | `3306` | RDS port |
| `DB_SSL_CA` | **Yes** | `/app/certs/global-bundle.pem` | Path to AWS RDS CA bundle |
| `DB_SSL_MODE` | No | `VERIFY_IDENTITY` | Strict hostname and certificate validation |
| `AWS_STORAGE_BUCKET_NAME` | **Yes** | `campus-hiring-resumes-prod` | Private S3 bucket for student resumes |
| `AWS_S3_REGION_NAME` | **Yes** | `us-east-1` | AWS region of S3 bucket |
| `AWS_QUERYSTRING_EXPIRE` | No | `3600` | Pre-signed URL expiration in seconds (default 1 hour) |

### Frontend Environment Variables (AWS Amplify Console)

| Variable | Required | Example | Description |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | **Yes** | `https://your-service.awsapprunner.com/api` | Full URL prefix to the deployed Django API |

---

## 3. Pre-Deployment Verification Checklist

Before triggering a cloud deployment, execute the local verification suite:

```powershell
# 1. Full backend automated test suite
.\venv\Scripts\python.exe -m pytest

# 2. Django system check
.\venv\Scripts\python.exe manage.py check

# 3. Django production security check
.\venv\Scripts\python.exe manage.py check --deploy

# 4. Frontend unit tests
cd frontend
npm test

# 5. Frontend production build
npm run build
cd ..

# 6. Verify Git working tree cleanliness and no secrets staged
git status -u
```

---

## 4. Step-by-Step Deployment Procedures

### Phase 1: Database Setup (Amazon RDS for MySQL)
1. Create a MySQL 8.0 RDS instance within a private VPC subnet.
2. In the DB parameter group, ensure `require_secure_transport=ON`.
3. Download the Amazon RDS global CA bundle:
   ```bash
   curl -o global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
   ```
4. Configure database credentials in AWS App Runner environment configuration.

### Phase 2: Resume Storage (Amazon S3)
1. Create an Amazon S3 bucket named e.g. `campus-hiring-resumes-<env>`.
2. Enable **Block *all* public access**.
3. Enable default encryption with AWS KMS or Amazon S3 managed keys (SSE-S3).
4. Attach an IAM role to App Runner with permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:DeleteObject"
         ],
         "Resource": "arn:aws:s3:::campus-hiring-resumes-*/*"
       }
     ]
   }
   ```

### Phase 3: Backend Deployment (AWS App Runner)
1. Build the Docker container using the repository `Dockerfile`.
2. Push the image to Amazon Elastic Container Registry (ECR).
3. Create an App Runner service pointing to the ECR image URI.
4. Set port to `8000`.
5. Configure health check path to `/api/health/`.
6. Set environment variables as detailed in Section 2.

### Phase 4: Frontend Deployment (AWS Amplify)
1. In AWS Amplify Console, click **New app > Host web app**.
2. Connect your GitHub repository (`Monica0406/campus-hiring-platform`) and branch `main`.
3. Verify Amplify detects `amplify.yml` at repository root:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: frontend/dist
       files:
         - '**/*'
     cache:
       paths:
         - frontend/node_modules/**/*
   ```
4. In **App settings > Environment variables**, configure `VITE_API_BASE_URL`.
5. In **App settings > Rewrites and redirects**, configure the SPA rewrite rule:
   - **Source address**: `</^[^.]+$|\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json)$)([^.]+$)/>`
   - **Target address**: `/index.html`
   - **Type**: `200 (Rewrite)`
6. Deploy the application.

---

## 5. Post-Deployment Verification & Health Monitoring

1. **Verify Health Endpoint**:
   ```bash
   curl -i https://your-service.awsapprunner.com/api/health/
   ```
   Expected response:
   ```json
   {
     "success": true,
     "message": "Service is operational.",
     "data": {
       "status": "healthy",
       "database": "connected"
     }
   }
   ```
2. **Verify Frontend Single Page Routing**:
   - Access `https://<amplify-id>.amplifyapp.com/`
   - Navigate to `/drives` and hit browser refresh (verifies 200 SPA rewrite).
3. **Verify Candidate Resume Upload**:
   - Upload a sample PDF resume in student profile.
   - Confirm upload succeeds and resume download URL uses pre-signed AWS S3 URL.

---

## 6. Operational Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **HTTP 503 on `/api/health/`** | Database unreachable or RDS security group blocking port 3306 | Verify RDS VPC security group allows ingress on port 3306 from App Runner VPC connector. |
| **SSL Connection Error to RDS** | Missing or invalid CA bundle path | Ensure `DB_SSL_CA` points to a valid `global-bundle.pem` and `DB_SSL_MODE=VERIFY_IDENTITY`. |
| **CORS Error in Browser** | `CORS_ALLOWED_ORIGINS` does not match Amplify URL | Add the exact Amplify domain (including `https://`, no trailing slash) to `CORS_ALLOWED_ORIGINS`. |
| **Infinite Redirect Loop** | Proxy SSL header mismatch | Ensure `USE_SECURE_PROXY_SSL_HEADER=True` so Django recognizes HTTPS from the reverse proxy. |
| **HTTP 404 on Page Refresh** | Missing SPA rewrite rule in Amplify | Add the 200 rewrite rule targeting `/index.html` in Amplify Console > Rewrites and redirects. |
