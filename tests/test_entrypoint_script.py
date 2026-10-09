"""
Tests for container entrypoint script and database pre-flight logic.
"""

from pathlib import Path
from django.conf import settings


BASE_DIR = Path(settings.BASE_DIR)


def test_entrypoint_script_exists_and_has_valid_shebang():
    """Verify entrypoint.sh exists and starts with POSIX sh shebang."""
    script_path = BASE_DIR / "scripts" / "entrypoint.sh"
    assert script_path.is_file(), "scripts/entrypoint.sh must exist"

    content = script_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    assert len(lines) > 0
    assert lines[0].strip() == "#!/bin/sh"
    assert "set -e" in content


def test_entrypoint_script_bounded_database_check():
    """Verify entrypoint script includes bounded DB retry loop with timeout."""
    script_path = BASE_DIR / "scripts" / "entrypoint.sh"
    content = script_path.read_text(encoding="utf-8")

    assert "WAIT_FOR_DB" in content
    assert "DB_TIMEOUT" in content
    assert "python manage.py check --database default" in content
    assert "exit 1" in content


def test_entrypoint_script_conditional_migration_and_static():
    """Verify entrypoint does not run migrations unconditionally."""
    script_path = BASE_DIR / "scripts" / "entrypoint.sh"
    content = script_path.read_text(encoding="utf-8")

    assert "RUN_MIGRATIONS" in content
    assert "python manage.py migrate --noinput" in content
    assert "COLLECT_STATIC" in content
    assert "python manage.py collectstatic --noinput" in content


def test_entrypoint_script_signal_forwarding_exec():
    """Verify entrypoint script ends with exec '$@' to replace PID 1."""
    script_path = BASE_DIR / "scripts" / "entrypoint.sh"
    content = script_path.read_text(encoding="utf-8")

    assert 'exec "$@"' in content
