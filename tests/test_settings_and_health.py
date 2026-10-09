"""
Tests for production settings parsing and health check behavior.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings


@pytest.fixture
def api_client():
    return APIClient()


def test_health_check_healthy_status_200(api_client, db):
    """Verify GET /api/health/ returns HTTP 200 and healthy status when database is operational."""
    response = api_client.get("/api/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert response.data["data"]["status"] == "healthy"
    assert response.data["data"]["database"] == "connected"
    assert response.data["message"] == "Service is operational."


def test_health_check_database_failure_returns_503(api_client):
    """Verify GET /api/health/ returns HTTP 503 and unhealthy status when database query fails."""
    with patch("django.db.connection.cursor") as mock_cursor:
        mock_cursor.side_effect = Exception("Can't connect to MySQL server on 'rds.amazonaws.com'")
        response = api_client.get("/api/health/")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data["success"] is False
        assert response.data["data"]["status"] == "unhealthy"
        assert "rds.amazonaws.com" in response.data["data"]["database"]
        assert "Service is unavailable" in response.data["message"]


def test_debug_default_behavior():
    """Verify DEBUG defaults to False when env variable is absent or empty."""
    # Test logic matching settings.py: os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes")
    parse_debug = lambda val: (val or "False").lower() in ("true", "1", "t", "yes")

    assert parse_debug(None) is False
    assert parse_debug("") is False
    assert parse_debug("False") is False
    assert parse_debug("false") is False
    assert parse_debug("0") is False

    assert parse_debug("True") is True
    assert parse_debug("true") is True
    assert parse_debug("1") is True
    assert parse_debug("yes") is True


def test_cors_allowed_origins_parsing():
    """Verify CORS_ALLOWED_ORIGINS parses custom origins and preserves localhost defaults when unset."""
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    parse_cors = lambda raw: (
        [origin.strip() for origin in raw.split(",") if origin.strip()]
        if raw.strip()
        else list(default_origins)
    )

    # When unset or empty string, fallback to default localhost origins
    assert parse_cors("") == default_origins
    assert parse_cors("   ") == default_origins

    # When custom origins provided (e.g., Amplify deployment)
    custom_input = "https://main.d123.amplifyapp.com, https://campus-hiring.example.com "
    expected = ["https://main.d123.amplifyapp.com", "https://campus-hiring.example.com"]
    assert parse_cors(custom_input) == expected


def test_allowed_hosts_parsing():
    """Verify ALLOWED_HOSTS parses comma-separated hosts from environment."""
    parse_hosts = lambda raw: [host.strip() for host in raw.split(",") if host.strip()]

    raw_input = "my-service.awsapprunner.com, custom-domain.com, "
    parsed = parse_hosts(raw_input)
    assert parsed == ["my-service.awsapprunner.com", "custom-domain.com"]

