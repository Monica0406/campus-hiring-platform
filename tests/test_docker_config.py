"""
Tests for Docker container configuration and build context exclusions.
"""

from pathlib import Path
from django.conf import settings


BASE_DIR = Path(settings.BASE_DIR)


def test_dockerfile_exists_and_uses_supported_python_base():
    """Verify Dockerfile exists and uses python:3.14-slim base image."""
    dockerfile_path = BASE_DIR / "Dockerfile"
    assert dockerfile_path.is_file(), "Dockerfile must exist at repository root"

    content = dockerfile_path.read_text(encoding="utf-8")
    assert "FROM python:3.14-slim" in content
    assert "WORKDIR /app" in content


def test_dockerfile_configures_non_root_user_and_permissions():
    """Verify Dockerfile creates and switches to a dedicated non-root user."""
    dockerfile_path = BASE_DIR / "Dockerfile"
    content = dockerfile_path.read_text(encoding="utf-8")

    assert "useradd" in content
    assert "appuser" in content
    assert "USER appuser" in content


def test_dockerfile_healthcheck_and_gunicorn_command():
    """Verify Dockerfile defines a container health check and Gunicorn command."""
    dockerfile_path = BASE_DIR / "Dockerfile"
    content = dockerfile_path.read_text(encoding="utf-8")

    assert "HEALTHCHECK" in content
    assert "/api/health/" in content
    assert "EXPOSE 8000" in content
    assert "gunicorn" in content
    assert "config.wsgi:application" in content


def test_dockerignore_excludes_sensitive_and_ephemeral_files():
    """Verify .dockerignore excludes secrets, virtual environments, and build artifacts."""
    dockerignore_path = BASE_DIR / ".dockerignore"
    assert dockerignore_path.is_file(), ".dockerignore must exist at repository root"

    rules = [line.strip() for line in dockerignore_path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]

    assert ".env" in rules
    assert any("venv" in rule for rule in rules)
    assert ".git" in rules
    assert "media/" in rules
    assert any("node_modules" in rule for rule in rules)
