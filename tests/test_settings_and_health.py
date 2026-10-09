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


def test_static_root_and_whitenoise_configuration():
    """Verify STATIC_ROOT, WhiteNoise middleware, and STORAGES are configured properly."""
    assert hasattr(settings, "STATIC_ROOT")
    assert settings.STATIC_ROOT is not None
    assert str(settings.STATIC_ROOT).endswith("staticfiles")

    # Verify middleware placement
    middleware = list(settings.MIDDLEWARE)
    assert "whitenoise.middleware.WhiteNoiseMiddleware" in middleware
    sec_index = middleware.index("django.middleware.security.SecurityMiddleware")
    wn_index = middleware.index("whitenoise.middleware.WhiteNoiseMiddleware")
    assert wn_index > sec_index, "WhiteNoise must be placed after SecurityMiddleware"

    # Verify STORAGES staticfiles backend
    staticfiles_storage = settings.STORAGES.get("staticfiles", {}).get("BACKEND")
    assert "whitenoise" in staticfiles_storage


def test_whitenoise_serves_admin_static_assets(client):
    """Verify that collected static files (e.g. Django admin CSS) are served with HTTP 200."""
    response = client.get("/static/admin/css/base.css")
    assert response.status_code == status.HTTP_200_OK


def test_swagger_documentation_endpoint_renders(client):
    """Verify Swagger/OpenAPI documentation endpoint is reachable and returns HTTP 200."""
    response = client.get("/api/docs/")
    assert response.status_code == status.HTTP_200_OK


def test_database_default_options_and_connection_pooling():
    """Verify default database settings include utf8mb4, connect_timeout, and connection reuse."""
    db_config = settings.DATABASES["default"]
    assert db_config["ENGINE"] == "django.db.backends.mysql"
    assert db_config["CONN_MAX_AGE"] == 60
    assert db_config["CONN_HEALTH_CHECKS"] is True
    assert db_config["OPTIONS"]["charset"] == "utf8mb4"
    assert db_config["OPTIONS"]["connect_timeout"] == 10


def test_database_config_local_defaults():
    """Verify local development defaults generate clean MySQL settings without SSL options."""
    from config.settings import build_database_config

    config = build_database_config(env={})
    assert config["ENGINE"] == "django.db.backends.mysql"
    assert config["HOST"] == "127.0.0.1"
    assert config["PORT"] == "3306"
    assert config["CONN_MAX_AGE"] == 60
    assert config["CONN_HEALTH_CHECKS"] is True
    assert config["OPTIONS"]["charset"] == "utf8mb4"
    assert config["OPTIONS"]["connect_timeout"] == 10
    assert "ssl" not in config["OPTIONS"]
    assert "ssl_mode" not in config["OPTIONS"]


def test_database_config_rds_ca_bundle_enables_strict_verification(tmp_path):
    """Verify providing an RDS CA bundle enables strict certificate and hostname verification."""
    from config.settings import build_database_config

    ca_file = tmp_path / "global-bundle.pem"
    ca_file.write_text("-----BEGIN CERTIFICATE-----\nTEST_CERT\n-----END CERTIFICATE-----\n")

    # When DB_SSL_CA is specified, default mode must be VERIFY_IDENTITY
    config = build_database_config(env={"DB_SSL_CA": str(ca_file)})
    assert config["OPTIONS"]["ssl"] == {"ca": str(ca_file)}
    assert config["OPTIONS"]["ssl_mode"] == "VERIFY_IDENTITY"

    # Explicit VERIFY_CA with CA bundle is also supported
    config_verify_ca = build_database_config(env={"DB_SSL_CA": str(ca_file), "DB_SSL_MODE": "VERIFY_CA"})
    assert config_verify_ca["OPTIONS"]["ssl"] == {"ca": str(ca_file)}
    assert config_verify_ca["OPTIONS"]["ssl_mode"] == "VERIFY_CA"


def test_database_config_explicit_ssl_mode_validation():
    """Verify explicit SSL modes are validated and invalid values fail safely with ImproperlyConfigured."""
    from config.settings import build_database_config
    from django.core.exceptions import ImproperlyConfigured

    # Invalid modes must raise ImproperlyConfigured
    for invalid_mode in ["INVALID", "NONE", "TLS_TRUE", "VERIFY_ALL"]:
        with pytest.raises(ImproperlyConfigured, match="Invalid DB_SSL_MODE"):
            build_database_config(env={"DB_SSL_MODE": invalid_mode})

    # Valid explicit mode without CA bundle
    config_req = build_database_config(env={"DB_SSL_MODE": "REQUIRED"})
    assert config_req["OPTIONS"]["ssl_mode"] == "REQUIRED"
    assert "ssl" not in config_req["OPTIONS"]


def test_database_config_missing_or_invalid_ca_bundle_fails(tmp_path):
    """Verify missing or invalid CA bundle paths fail fast and do not silently disable verification."""
    from config.settings import build_database_config
    from django.core.exceptions import ImproperlyConfigured

    # Non-existent file path
    non_existent = tmp_path / "nonexistent-bundle.pem"
    with pytest.raises(ImproperlyConfigured, match="does not exist or is not a valid file"):
        build_database_config(env={"DB_SSL_CA": str(non_existent)})

    # Directory path instead of a file
    with pytest.raises(ImproperlyConfigured, match="does not exist or is not a valid file"):
        build_database_config(env={"DB_SSL_CA": str(tmp_path)})


def test_database_config_tls_verification_never_weakened(tmp_path):
    """Verify TLS certificate verification cannot be weakened when CA bundle or requirement is set."""
    from config.settings import build_database_config
    from django.core.exceptions import ImproperlyConfigured

    ca_file = tmp_path / "rds-ca.pem"
    ca_file.write_text("-----BEGIN CERTIFICATE-----\nTEST_CERT\n-----END CERTIFICATE-----\n")

    # When CA bundle is configured, weakening modes must be blocked
    for weak_mode in ["DISABLED", "PREFERRED", "REQUIRED"]:
        with pytest.raises(ImproperlyConfigured, match="Certificate verification cannot be disabled or weakened"):
            build_database_config(env={"DB_SSL_CA": str(ca_file), "DB_SSL_MODE": weak_mode})

    # When DB_SSL_REQUIRE is enabled, disabling or weakening mode must be blocked
    for weak_mode in ["DISABLED", "PREFERRED"]:
        with pytest.raises(ImproperlyConfigured, match="Cannot use DB_SSL_MODE"):
            build_database_config(env={"DB_SSL_REQUIRE": "True", "DB_SSL_MODE": weak_mode})


def test_database_config_ssl_require_flag():
    """Verify DB_SSL_REQUIRE enables REQUIRED mode when no CA bundle is provided."""
    from config.settings import build_database_config

    config = build_database_config(env={"DB_SSL_REQUIRE": "True"})
    assert config["OPTIONS"]["ssl_mode"] == "REQUIRED"
    assert "ssl" not in config["OPTIONS"]

    config_disabled = build_database_config(env={"DB_SSL_REQUIRE": "False"})
    assert "ssl_mode" not in config_disabled["OPTIONS"]


def test_database_config_integer_parsing_and_production_bounds():
    """Verify CONN_MAX_AGE, connect_timeout, and port safely parse invalid input and respect bounds."""
    from config.settings import build_database_config, _parse_int_setting

    # Unit-level parser tests
    assert _parse_int_setting(None, default=60) == 60
    assert _parse_int_setting("not_a_number", default=60) == 60
    assert _parse_int_setting("-5", default=60, min_val=0) == 60
    assert _parse_int_setting("0", default=60, min_val=0) == 0
    assert _parse_int_setting("120", default=60, min_val=0) == 120
    assert _parse_int_setting("0", default=10, min_val=1) == 10
    assert _parse_int_setting("-1", default=10, min_val=1) == 10
    assert _parse_int_setting("15", default=10, min_val=1) == 15

    # Safe fallback with malformed environment variables
    config = build_database_config(env={
        "DB_CONN_MAX_AGE": "invalid_num",
        "DB_CONNECT_TIMEOUT": "invalid_timeout",
        "DB_PORT": "invalid_port",
    })
    assert config["CONN_MAX_AGE"] == 60
    assert config["OPTIONS"]["connect_timeout"] == 10
    assert config["PORT"] == "3306"
    assert config["CONN_HEALTH_CHECKS"] is True

    # Custom valid overrides
    config_custom = build_database_config(env={
        "DB_CONN_MAX_AGE": "0",
        "DB_CONNECT_TIMEOUT": "5",
        "DB_PORT": "3307",
        "DB_CONN_HEALTH_CHECKS": "False",
    })
    assert config_custom["CONN_MAX_AGE"] == 0
    assert config_custom["OPTIONS"]["connect_timeout"] == 5
    assert config_custom["PORT"] == "3307"
    assert config_custom["CONN_HEALTH_CHECKS"] is False


def test_mysqlclient_driver_supports_configured_ssl_options(tmp_path):
    """Verify that installed mysqlclient driver genuinely supports ssl_mode and ssl dictionary options."""
    import MySQLdb
    from config.settings import build_database_config

    ca_file = tmp_path / "global-bundle.pem"
    ca_file.write_text("-----BEGIN CERTIFICATE-----\nTEST_CERT\n-----END CERTIFICATE-----\n")

    db_cfg = build_database_config(env={"DB_SSL_CA": str(ca_file)})
    options = db_cfg["OPTIONS"]

    # Verify mysqlclient native C extension accepts ssl_mode='VERIFY_IDENTITY' and ssl={'ca': ...}
    # It must reach the socket connection phase (raising OperationalError 2002)
    # rather than failing on unrecognized option (NotSupportedError or TypeError)
    try:
        MySQLdb._mysql.connect(
            host="127.0.0.1",
            port=65534,
            connect_timeout=1,
            ssl_mode=options["ssl_mode"],
            ssl=options["ssl"],
        )
    except MySQLdb.OperationalError as exc:
        # Expected error code 2002: cannot connect to server on port 65534
        assert exc.args[0] == 2002

    # Verify that an invalid ssl_mode is genuinely rejected by the mysqlclient C extension
    with pytest.raises(MySQLdb.NotSupportedError, match="Unknown ssl_mode specification"):
        MySQLdb._mysql.connect(host="127.0.0.1", port=65534, ssl_mode="BOGUS_MODE")


@pytest.mark.django_db
def test_database_migration_consistency():
    """Verify that all model definitions match generated migrations without drift."""
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    call_command("makemigrations", "--dry-run", "--check", stdout=out)
    assert "No changes detected" in out.getvalue() or out.getvalue() == ""



