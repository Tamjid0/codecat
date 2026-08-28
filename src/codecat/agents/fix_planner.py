"""FixPlanner — rule-based, picks TOP 1 fixable."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FixTarget:
    kind: str  # "tests" | "dep_bump" | "docker"
    file: str
    detail: str


def plan_fix(
    build_pass: bool | None,
    high_cves: int,
    has_docker_fail: bool | None,
    repo_path: Path,
) -> FixTarget | None:
    """
    Rule priority:
    1. If tests FAIL → fix tests (most demonstrable)
    2. Else if CVE with fix available → bump dep
    3. Else if docker FAIL → fix Dockerfile
    4. Else None
    """
    if build_pass is False:
        return FixTarget(kind="tests", file="evidence/test.log", detail="tests fail - missing dep or import")
    if high_cves > 0 and (repo_path / "package.json").exists():
        return FixTarget(kind="dep_bump", file="package.json", detail=f"{high_cves} high CVE bump")
    if has_docker_fail is True:
        return FixTarget(kind="docker", file="Dockerfile", detail="docker build fails")
    return None
