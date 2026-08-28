"""StaticClaimAgent — circular deps + complexity + README claim cross-check."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from codecat.agents.build_agent import BuildResult
from codecat.tools.sandbox import SandboxResult
from codecat.tools.static_tools import (
    claim_verdict,
    cloc_summary,
    complexity_scan,
    detect_circular_deps,
    extract_readme_claims,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClaimCheck:
    text: str
    verdict: str  # PASS|FAIL|UNKNOWN
    evidence_ref: str


@dataclass(frozen=True)
class StaticClaimResult:
    circular_log: SandboxResult
    complexity_log: SandboxResult
    cloc_log: SandboxResult
    claims: list[ClaimCheck]
    has_circular: bool


def run_static_claim_agent(repo_path: Path, out_evidence: Path, build: BuildResult) -> StaticClaimResult:
    out_evidence.mkdir(parents=True, exist_ok=True)

    circular = detect_circular_deps(repo_path)
    (out_evidence / "madge.log").write_text(circular.combined, encoding="utf-8")

    complexity = complexity_scan(repo_path)
    (out_evidence / "complexity.log").write_text(complexity.combined, encoding="utf-8")

    cloc = cloc_summary(repo_path)
    (out_evidence / "cloc.log").write_text(cloc.combined, encoding="utf-8")

    has_circular = "circular" in circular.combined.lower() and "found" in circular.combined.lower()
    # Also check if madge output contains "->"
    if "->" in circular.combined:
        has_circular = True

    raw_claims = extract_readme_claims(repo_path)
    claim_checks: list[ClaimCheck] = []
    for c in raw_claims:
        verdict, ref = claim_verdict(c, build.test_pass, build.docker_pass, build.install_pass)
        claim_checks.append(ClaimCheck(text=c, verdict=verdict, evidence_ref=ref))

    (out_evidence / "claim_check.json").write_text(
        json.dumps([{"text": ch.text, "verdict": ch.verdict, "evidence": ch.evidence_ref} for ch in claim_checks], indent=2),
        encoding="utf-8",
    )

    return StaticClaimResult(
        circular_log=circular,
        complexity_log=complexity,
        cloc_log=cloc,
        claims=claim_checks,
        has_circular=has_circular,
    )
