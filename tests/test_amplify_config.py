"""
Tests for AWS Amplify build configuration, package scripts, and SPA distribution consistency.
"""

from pathlib import Path
import json
import yaml
from django.conf import settings


BASE_DIR = Path(settings.BASE_DIR)


def test_amplify_yml_exists_and_is_valid_yaml():
    """Verify amplify.yml exists at repository root and is valid YAML."""
    amplify_path = BASE_DIR / "amplify.yml"
    assert amplify_path.is_file(), "amplify.yml must exist at repository root"

    with open(amplify_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert isinstance(data, dict)
    assert data.get("version") == 1
    assert "frontend" in data


def test_amplify_yml_phases_and_artifacts_configuration():
    """Verify amplify.yml defines correct preBuild, build, and artifact paths for frontend/dist."""
    amplify_path = BASE_DIR / "amplify.yml"
    with open(amplify_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    frontend = data.get("frontend", {})
    phases = frontend.get("phases", {})

    pre_build = phases.get("preBuild", {}).get("commands", [])
    assert any("cd frontend" in cmd for cmd in pre_build), "preBuild must navigate to frontend"
    assert any("npm ci" in cmd or "npm install" in cmd for cmd in pre_build)

    build = phases.get("build", {}).get("commands", [])
    assert any("npm run build" in cmd for cmd in build), "build must run npm run build"

    artifacts = frontend.get("artifacts", {})
    assert artifacts.get("baseDirectory") == "frontend/dist", "baseDirectory must point to frontend/dist"
    assert "**/*" in artifacts.get("files", [])


def test_frontend_package_json_scripts():
    """Verify frontend/package.json defines required build and test scripts."""
    pkg_path = BASE_DIR / "frontend" / "package.json"
    assert pkg_path.is_file()

    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    scripts = pkg.get("scripts", {})
    assert "build" in scripts
    assert "vite build" in scripts["build"]
    assert "test" in scripts


def test_frontend_build_dist_structure():
    """Verify frontend build outputs valid index.html with SPA root container."""
    dist_dir = BASE_DIR / "frontend" / "dist"
    index_html = dist_dir / "index.html"

    assert dist_dir.is_dir(), "frontend/dist must exist after npm run build"
    assert index_html.is_file(), "frontend/dist/index.html must exist"

    content = index_html.read_text(encoding="utf-8")
    assert '<div id="root">' in content or 'id="root"' in content
    assert "<html" in content
    assert "assets/" in content
