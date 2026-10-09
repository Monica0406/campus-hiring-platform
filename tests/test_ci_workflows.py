"""
Tests for CI workflow specifications and pipeline configuration.
"""

from pathlib import Path
import yaml
from django.conf import settings


BASE_DIR = Path(settings.BASE_DIR)


def test_backend_ci_workflow_exists_and_is_valid_yaml():
    """Verify backend-ci.yml exists and has valid YAML syntax."""
    ci_path = BASE_DIR / ".github" / "workflows" / "backend-ci.yml"
    assert ci_path.is_file(), ".github/workflows/backend-ci.yml must exist"

    with open(ci_path, "r", encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    assert workflow.get("name") == "Backend CI"
    assert "jobs" in workflow
    assert "test" in workflow["jobs"]


def test_backend_ci_uses_pinned_actions_and_runs_checks():
    """Verify backend-ci.yml pins actions and executes system check, deploy check, and pytest."""
    ci_path = BASE_DIR / ".github" / "workflows" / "backend-ci.yml"
    with open(ci_path, "r", encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    steps = workflow["jobs"]["test"]["steps"]
    actions_used = [s["uses"] for s in steps if "uses" in s]

    assert any(a.startswith("actions/checkout@v") for a in actions_used)
    assert any(a.startswith("actions/setup-python@v") for a in actions_used)

    run_commands = [s["run"] for s in steps if "run" in s]
    assert any("python manage.py check" in cmd for cmd in run_commands)
    assert any("check --deploy" in cmd for cmd in run_commands)
    assert any("pytest" in cmd for cmd in run_commands)
