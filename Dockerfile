# ==============================================================================
# Production Dockerfile for Campus Hiring Platform (Backend)
# Designed for AWS App Runner, Amazon ECS, or Docker Compose
# ==============================================================================

FROM python:3.14-slim

# Prevent Python from writing .pyc files and enable unbuffered logging for CloudWatch
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies for mysqlclient C extensions and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pinned Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into container
COPY . /app/

# Create non-root system user and prepare runtime directories
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appgroup /app

# Switch to non-root user for production security
USER appuser

EXPOSE 8000

# Container health check against Django health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Default command launches Gunicorn WSGI server
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
