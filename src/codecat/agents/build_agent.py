"""BuildAgent — reproduces repo in sandbox, captures real logs. See docs/06."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from codecat.tools.sandbox import SandboxResult, run_in_sandbox

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuildResult:
    install_pass: bool | None
    test_pass: bool | None
    docker_pass: bool | None
    install_log: SandboxResult | None
    test_log: SandboxResult | None
    docker_log: SandboxResult | None
    test_summary: str
    package_manager: str  # "npm" | "pip" | "none"


def detect_package_manager(repo_path: Path) -> str:
    if (repo_path / "package.json").exists():
        return "npm"
    if (repo_path / "pyproject.toml").exists() or (repo_path / "requirements.txt").exists():
        return "pip"
    return "none"


def _detect_test_cmd(repo_path: Path, pm: str) -> str | None:
    if pm == "npm":
        # check package.json scripts
        try:
            import json

            pkg = json.loads((repo_path / "package.json").read_text(encoding="utf-8"))
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                return "npm test"
        except Exception:
            pass
        return "npm test"
    if pm == "pip":
        if (repo_path / "pyproject.toml").exists():
            return "pytest -q"
        if (repo_path / "tests").exists():
            return "pytest -q"
        return None
    return None


def run_build_agent(repo_path: Path, out_evidence: Path) -> BuildResult:
    """Run install/test/docker, write logs to out_evidence. Returns BuildResult."""
    out_evidence.mkdir(parents=True, exist_ok=True)
    pm = detect_package_manager(repo_path)
    logger.info("BuildAgent pm=%s path=%s", pm, repo_path)

    install_pass: bool | None = None
    test_pass: bool | None = None
    docker_pass: bool | None = None
    install_log: SandboxResult | None = None
    test_log: SandboxResult | None = None
    docker_log: SandboxResult | None = None

    # Install
    if pm == "npm":
        install_log = run_in_sandbox("npm ci --ignore-scripts", cwd=repo_path, timeout_sec=120)
        if install_log.returncode != 0:
            install_log = run_in_sandbox("npm install --ignore-scripts", cwd=repo_path, timeout_sec=120)
        install_pass = install_log.passed
        (out_evidence / "install.log").write_text(install_log.combined, encoding="utf-8")
    elif pm == "pip":
        install_log = run_in_sandbox("pip install -e . --quiet", cwd=repo_path, timeout_sec=120)
        if install_log.returncode != 0:
            install_log = run_in_sandbox("pip install -r requirements.txt --quiet", cwd=repo_path, timeout_sec=120)
        install_pass = install_log.passed if install_log else None
        if install_log:
            (out_evidence / "install.log").write_text(install_log.combined, encoding="utf-8")

    # Test
    test_cmd = _detect_test_cmd(repo_path, pm)
    if test_cmd:
        test_log = run_in_sandbox(test_cmd, cwd=repo_path, timeout_sec=90)
        test_pass = test_log.passed and ("fail" not in test_log.stdout.lower() or "pass" in test_log.stdout.lower())
        # More accurate: check returncode
        test_pass = test_log.returncode == 0
        (out_evidence / "test.log").write_text(test_log.combined, encoding="utf-8")
        test_summary = _summarize_tests(test_log.combined)
    else:
        test_summary = "no test command detected"

    # Docker
    if (repo_path / "Dockerfile").exists():
        docker_log = run_in_sandbox("docker build -t codecat-test:tmp .", cwd=repo_path, timeout_sec=120)
        docker_pass = docker_log.passed
        (out_evidence / "docker.log").write_text(docker_log.combined, encoding="utf-8")

    return BuildResult(
        install_pass=install_pass,
        test_pass=test_pass,
        docker_pass=docker_pass,
        install_log=install_log,
        test_log=test_log,
        docker_log=docker_log,
        test_summary=test_summary if "test_summary" in locals() else "n/a",
        package_manager=pm,
    )


def _summarize_tests(combined: str) -> str:
    low = combined.lower()
    if "passed" in low and "failed" in low:
        # extract numbers like "3 passed, 2 failed"
        import re

        m = re.search(r"(\d+)\s+passed.*?(\d+)\s+failed", low)
        if m:
            return f"{m.group(1)} passed, {m.group(2)} failed"
        m2 = re.search(r"(\d+)\s+passed", low)
        if m2:
            return f"{m2.group(1)} passed"
    if "passed" in low:
        import re

        m = re.search(r"(\d+)\s+passed", low)
        if m:
            return f"{m.group(1)} passed"
    if "fail" in low:
        return "tests failed"
    return combined.strip()[:200]
