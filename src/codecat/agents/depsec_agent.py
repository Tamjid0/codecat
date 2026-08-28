"""DepSecAgent — npm/pip audit + git history."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from codecat.tools.audit_tools import count_high_cves, npm_audit, pip_audit
from codecat.tools.git_tools import (
    bus_factor_from_shortlog,
    git_log_stat,
    git_shortlog,
    has_dockerfile,
)
from codecat.tools.sandbox import SandboxResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DepSecResult:
    npm_audit_log: SandboxResult | None
    pip_audit_log: SandboxResult | None
    npm_parsed: dict[str, object] | None
    pip_parsed: object | None
    high_cves: int
    bus_factor: int
    has_docker: bool
    git_log: SandboxResult


def run_depsec_agent(repo_path: Path, out_evidence: Path) -> DepSecResult:
    out_evidence.mkdir(parents=True, exist_ok=True)

    # Audits
    npm_log, npm_parsed = npm_audit(repo_path)
    pip_log, pip_parsed = pip_audit(repo_path)

    # Write evidence
    (out_evidence / "npm_audit.json").write_text(json.dumps(npm_parsed, indent=2) if npm_parsed else "{}", encoding="utf-8")
    (out_evidence / "npm_audit.log").write_text(npm_log.combined, encoding="utf-8")
    (out_evidence / "pip_audit.json").write_text(json.dumps(pip_parsed, indent=2) if pip_parsed else "[]", encoding="utf-8")
    (out_evidence / "pip_audit.log").write_text(pip_log.combined, encoding="utf-8")

    high = count_high_cves(npm_parsed if npm_parsed else {}) + count_high_cves(pip_parsed if pip_parsed else {})  # type: ignore[arg-type]

    # Git
    git_log = git_log_stat(repo_path)
    (out_evidence / "git.log").write_text(git_log.combined, encoding="utf-8")
    short = git_shortlog(repo_path)
    (out_evidence / "git_shortlog.log").write_text(short.combined, encoding="utf-8")
    bus = bus_factor_from_shortlog(short.stdout)

    has_docker = has_dockerfile(repo_path)

    return DepSecResult(
        npm_audit_log=npm_log,
        pip_audit_log=pip_log,
        npm_parsed=npm_parsed,  # type: ignore[assignment]
        pip_parsed=pip_parsed,  # type: ignore[assignment]
        high_cves=high,
        bus_factor=bus,
        has_docker=has_docker,
        git_log=git_log,
    )
