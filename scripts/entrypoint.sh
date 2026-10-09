#!/bin/sh
set -e

# ==============================================================================
# Container Entrypoint for Campus Hiring Platform
# ==============================================================================

# Wait for MySQL / Amazon RDS database readiness if requested
if [ "${WAIT_FOR_DB:-false}" = "true" ] || [ "${WAIT_FOR_DB:-false}" = "1" ]; then
    TIMEOUT="${DB_TIMEOUT:-30}"
    ELAPSED=0
    echo "[entrypoint] Waiting for database readiness (timeout: ${TIMEOUT}s)..."

    until python manage.py check --database default > /dev/null 2>&1; do
        if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
            echo "[entrypoint] ERROR: Database connection timed out after ${TIMEOUT}s." >&2
            exit 1
        fi
        sleep 2
        ELAPSED=$((ELAPSED + 2))
    done
    echo "[entrypoint] Database connection verified successfully."
fi

# Run database migrations only if explicitly enabled
if [ "${RUN_MIGRATIONS:-false}" = "true" ] || [ "${RUN_MIGRATIONS:-false}" = "1" ]; then
    echo "[entrypoint] Applying database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files if enabled
if [ "${COLLECT_STATIC:-false}" = "true" ] || [ "${COLLECT_STATIC:-false}" = "1" ]; then
    echo "[entrypoint] Collecting static assets..."
    python manage.py collectstatic --noinput
fi

# Hand over PID 1 to the passed command (e.g. gunicorn) for proper POSIX signal forwarding
echo "[entrypoint] Executing: $@"
exec "$@"
