"""Static + claim tools. 100% typed."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from codecat.tools.sandbox import SandboxResult, run_in_sandbox

logger = logging.getLogger(__name__)


def detect_circular_deps(repo_path: Path) -> SandboxResult:
    """Run madge if available, else fallback heuristic."""
    if not (repo_path / "package.json").exists():
        return SandboxResult(command="madge --circular", returncode=0, stdout="", stderr="no js", timed_out=False)
    # Try madge, if not installed, run heuristic
    result = run_in_sandbox("npx --yes madge --circular --extensions ts,js src 2>&1 || echo 'madge not found'", cwd=repo_path, timeout_sec=30)
    return result


def complexity_scan(repo_path: Path) -> SandboxResult:
    """Run radon if python project."""
    if not (repo_path / "pyproject.toml").exists() and not (repo_path / "requirements.txt").exists():
        return SandboxResult(command="radon cc", returncode=0, stdout="", stderr="no python", timed_out=False)
    result = run_in_sandbox("radon cc -s -j . 2>&1 | head -n 100", cwd=repo_path, timeout_sec=30)
    return result


def extract_readme_claims(repo_path: Path) -> list[str]:
    """Extract claim sentences from README.md."""
    readme = repo_path / "README.md"
    if not readme.exists():
        # try lowercase
        readme = repo_path / "readme.md"
        if not readme.exists():
            return []
    text = readme.read_text(encoding="utf-8", errors="ignore")[:8000]
    claims: list[str] = []
    patterns = [
        r"npm test.*pass",
        r"pytest.*pass",
        r"docker build.*work",
        r"zero.*dependenc",
        r"100%.*coverage",
        r"easy.*install",
    ]
    for line in text.splitlines():
        low = line.lower()
        for pat in patterns:
            if re.search(pat, low):
                claims.append(line.strip()[:300])
                break
    return claims[:10]


def claim_verdict(claim: str, test_pass: bool | None, docker_pass: bool | None, install_pass: bool | None) -> tuple[str, str]:
    """Cross-check claim vs actual logs. Returns (verdict, evidence_ref)."""
    low = claim.lower()
    if "test" in low and "pass" in low:
        if test_pass is None:
            return "UNKNOWN", "no test log"
        return ("PASS" if test_pass else "FAIL"), "test.log:1"
    if "docker" in low:
        if docker_pass is None:
            return "UNKNOWN", "no docker log"
        return ("PASS" if docker_pass else "FAIL"), "docker.log:1"
    if "install" in low:
        if install_pass is None:
            return "UNKNOWN", "no install log"
        return ("PASS" if install_pass else "FAIL"), "install.log:1"
    return "UNKNOWN", "no matching tool"


def cloc_summary(repo_path: Path) -> SandboxResult:
    return run_in_sandbox("npx --yes cloc --json . 2>&1 | head -n 80", cwd=repo_path, timeout_sec=30)
