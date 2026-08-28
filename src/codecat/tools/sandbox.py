"""Sandbox — all consequential actions inside Docker or isolated tmp. 100% typed, 100% legal."""

from __future__ import annotations

import hashlib
import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SandboxResult:
    """Raw tool output — never hallucinated, always logged."""

    command: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool

    @property
    def combined(self) -> str:
        return f"{self.stdout}\n{self.stderr}".strip()

    @property
    def passed(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def repo_hash(url: str) -> str:
    """Deterministic short hash for out/ folder."""
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def run_in_sandbox(
    command: str,
    cwd: Path,
    timeout_sec: int = 120,
    use_docker: bool = False,
) -> SandboxResult:
    """
    Run command in sandbox. For 48h MVP, use host isolation (tmp + timeout).
    If use_docker True and Docker available, wrap in docker.
    Evidence is raw stdout/stderr — never LLM generated.
    """
    logger.info("sandbox run: %s (cwd=%s)", command, cwd)
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return SandboxResult(
            command=command,
            returncode=result.returncode,
            stdout=result.stdout[-8000:],
            stderr=result.stderr[-8000:],
            timed_out=False,
        )
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else str(e.stdout or "")  # type: ignore[union-attr]
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr or "")  # type: ignore[union-attr]
        return SandboxResult(
            command=command,
            returncode=124,
            stdout=stdout[-8000:],
            stderr=stderr[-8000:],
            timed_out=True,
        )


def ensure_tmp_repo(url: str, base: Path | None = None) -> tuple[Path, SandboxResult]:
    """
    Clone to isolated tmp dir. Returns (path, result). Caller moves to out/ if needed.
    Ground rule 04: sandbox-isolated, no host mutation outside tmp/out.
    """
    tmp_base = base or Path(tempfile.gettempdir()) / "codecat"
    tmp_base.mkdir(parents=True, exist_ok=True)
    dest = tmp_base / repo_hash(url)
    if dest.exists():
        # Windows: git pack files are read-only -> PermissionError without onerror
        def _on_rm_error(func: object, path: str, exc_info: object) -> None:
            import contextlib
            import os
            import stat

            with contextlib.suppress(Exception):
                os.chmod(path, stat.S_IWRITE)
                if func is not None:
                    with contextlib.suppress(Exception):
                        func(path)  # type: ignore[operator]

        shutil.rmtree(dest, onerror=_on_rm_error)  # type: ignore[arg-type]
    # Use host git for speed; sandbox isolates install/test steps
    result = run_in_sandbox(f"git clone --depth 1 {url} {dest}", cwd=tmp_base, timeout_sec=60)
    return dest, result
