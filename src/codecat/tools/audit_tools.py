"""Audit tools — npm audit / pip-audit wrappers. 100% typed, evidence-first."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from codecat.tools.sandbox import SandboxResult, run_in_sandbox

logger = logging.getLogger(__name__)


def npm_audit(repo_path: Path) -> tuple[SandboxResult, dict[str, Any]]:
    """Run npm audit --json if package.json exists. Returns (result, parsed)."""
    if not (repo_path / "package.json").exists():
        return (
            SandboxResult(command="npm audit --json", returncode=0, stdout="{}", stderr="no package.json", timed_out=False),
            {},
        )
    result = run_in_sandbox("npm audit --json", cwd=repo_path, timeout_sec=60)
    try:
        parsed: dict[str, Any] = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        parsed = {"raw": result.stdout[:2000]}
    return result, parsed


def pip_audit(repo_path: Path) -> tuple[SandboxResult, dict[str, Any] | list[Any]]:
    """Run pip-audit --format=json if requirements exist. Returns (result, parsed)."""
    has_reqs = (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists()
    if not has_reqs:
        return (
            SandboxResult(command="pip-audit --format=json", returncode=0, stdout="[]", stderr="no requirements", timed_out=False),
            [],
        )
    result = run_in_sandbox("pip-audit --format=json", cwd=repo_path, timeout_sec=60)
    try:
        parsed: dict[str, Any] | list[Any] = json.loads(result.stdout) if result.stdout.strip() else []  # type: ignore[assignment]
    except json.JSONDecodeError:
        parsed = {"raw": result.stdout[:2000]}  # type: ignore[assignment]
    return result, parsed


def count_high_cves(audit_parsed: dict[str, Any] | list[Any]) -> int:
    """Count highs/criticals from npm audit or pip-audit."""
    if isinstance(audit_parsed, list):
        # pip-audit list of vulns
        return len(audit_parsed)
    # npm audit: vulnerabilities dict or metadata
    vulns = audit_parsed.get("vulnerabilities", {})
    if isinstance(vulns, dict):
        return sum(1 for v in vulns.values() if isinstance(v, dict) and v.get("severity") in ("high", "critical"))
    advisories = audit_parsed.get("advisories", {})
    if isinstance(advisories, dict):
        return len(advisories)
    return 0
