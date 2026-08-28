"""Git tools — clone, history, bus factor. 100% typed."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from codecat.tools.sandbox import SandboxResult, run_in_sandbox

logger = logging.getLogger(__name__)


def git_log_stat(repo_path: Path, since: str = "18 months ago") -> SandboxResult:
    return run_in_sandbox(f'git log --stat --since="{since}" --oneline -n 100', cwd=repo_path, timeout_sec=30)


def git_shortlog(repo_path: Path) -> SandboxResult:
    return run_in_sandbox("git shortlog -sn --all --no-merges", cwd=repo_path, timeout_sec=30)


def bus_factor_from_shortlog(shortlog_stdout: str) -> int:
    """Count contributors; bus factor ~ contributors with >10% commits. Simplified for MVP."""
    lines = [line.strip() for line in shortlog_stdout.strip().splitlines() if line.strip()]
    if not lines:
        return 0
    # shortlog format: "   123\tAuthor"
    counts: list[int] = []
    for line in lines:
        m = re.match(r"\s*(\d+)\s+.*", line)
        if m:
            counts.append(int(m.group(1)))
    total = sum(counts)
    if total == 0:
        return 0
    # count authors with >10% of commits
    major = sum(1 for c in counts if c / total > 0.10)
    return max(1, major) if counts else 1


def abandoned_files_from_log(log_stdout: str) -> list[str]:
    """Naive: files not touched in log window are considered abandoned — caller supplies full log."""
    # For MVP, parse --stat lines like " file.py | 10 +-"
    files: set[str] = set()
    for line in log_stdout.splitlines():
        if "|" in line and "." in line:
            # e.g. " src/foo.py |  20 +++++"
            part = line.split("|")[0].strip()
            if part and "/" in part or "." in part:
                files.add(part)
    return sorted(files)[:20]


def has_dockerfile(repo_path: Path) -> bool:
    return (repo_path / "Dockerfile").exists() or (repo_path / "docker-compose.yml").exists()
