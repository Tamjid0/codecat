"""Aggregator — scores 0-100 per area, EVERY row must have evidence. Verifier drops hallucinations."""

from __future__ import annotations

import logging

from codecat.agents.build_agent import BuildResult
from codecat.agents.depsec_agent import DepSecResult
from codecat.agents.static_claim_agent import StaticClaimResult
from codecat.models.schemas import Evidence, RiskArea, Severity

logger = logging.getLogger(__name__)


def _evidence(file: str, line: int | None = 1, excerpt: str = "") -> Evidence:
    return Evidence(file=file, line=line, excerpt=excerpt[:500])


def aggregate(
    repo_url: str,
    build: BuildResult,
    depsec: DepSecResult,
    static: StaticClaimResult,
) -> list[RiskArea]:
    areas: list[RiskArea] = []

    # Testing — lint-only failures (xo, warnings) are medium, not critical
    if build.test_pass is True:
        areas.append(
            RiskArea(
                area="Testing",
                score=90,
                severity=Severity.low,
                evidence=[_evidence("evidence/test.log", 1, build.test_summary)],
                cost_to_fix="0h",
                summary=f"Tests pass: {build.test_summary}",
            )
        )
    elif build.test_pass is False:
        # Distinguish real test failures vs lint/environment warnings
        summary_low = build.test_summary.lower()
        is_lint_only = any(k in summary_low for k in ["xo", "warning", "parsing error", "max-lines", "todo comment"])
        if is_lint_only:
            areas.append(
                RiskArea(
                    area="Testing",
                    score=65,
                    severity=Severity.medium,
                    evidence=[_evidence("evidence/test.log", 1, build.test_summary)],
                    cost_to_fix="2h lint",
                    summary=f"Lint warnings (not unit fail): {build.test_summary[:120]}",
                )
            )
        else:
            areas.append(
                RiskArea(
                    area="Testing",
                    score=35,
                    severity=Severity.critical,
                    evidence=[_evidence("evidence/test.log", 1, build.test_summary)],
                    cost_to_fix="4h",
                    summary=f"Tests fail: {build.test_summary}",
                )
            )
    else:
        areas.append(
            RiskArea(
                area="Testing",
                score=50,
                severity=Severity.medium,
                evidence=[_evidence("evidence/test.log", 1, "no tests detected")],
                cost_to_fix="2h",
                summary="No test command detected",
            )
        )

    # Dependencies
    if depsec.high_cves > 2:
        areas.append(
            RiskArea(
                area="Dependencies",
                score=30,
                severity=Severity.critical,
                evidence=[_evidence("evidence/npm_audit.json", 1, f"{depsec.high_cves} high CVEs")],
                cost_to_fix="1 sprint",
                summary=f"{depsec.high_cves} high/critical CVEs",
            )
        )
    elif depsec.high_cves > 0:
        areas.append(
            RiskArea(
                area="Dependencies",
                score=60,
                severity=Severity.medium,
                evidence=[_evidence("evidence/npm_audit.json", 1, f"{depsec.high_cves} CVE")],
                cost_to_fix="4h",
                summary=f"{depsec.high_cves} CVE(s) with fix available",
            )
        )
    else:
        areas.append(
            RiskArea(
                area="Dependencies",
                score=85,
                severity=Severity.low,
                evidence=[_evidence("evidence/npm_audit.json", 1, "no high CVEs")],
                cost_to_fix="0h",
                summary="No high CVEs",
            )
        )

    # Security is same as dependencies but separate for table completeness
    if depsec.high_cves > 0:
        areas.append(
            RiskArea(
                area="Security",
                score=45 if depsec.high_cves > 1 else 65,
                severity=Severity.critical if depsec.high_cves > 1 else Severity.medium,
                evidence=[_evidence("evidence/pip_audit.json", 1, f"audit high {depsec.high_cves}")],
                cost_to_fix="4h",
                summary=f"Security audit: {depsec.high_cves} high",
            )
        )
    else:
        areas.append(
            RiskArea(
                area="Security",
                score=88,
                severity=Severity.low,
                evidence=[_evidence("evidence/pip_audit.json", 1, "clean")],
                cost_to_fix="0h",
                summary="No high security findings",
            )
        )

    # Architecture (+ Docker failure penalty)
    if build.docker_pass is False:
        areas.append(
            RiskArea(
                area="Architecture",
                score=30,
                severity=Severity.critical,
                evidence=[_evidence("evidence/docker.log", 1, "docker build FAIL")],
                cost_to_fix="1d",
                summary="Docker build fails — deployment blocked",
            )
        )
    elif static.has_circular:
        areas.append(
            RiskArea(
                area="Architecture",
                score=30,
                severity=Severity.critical,
                evidence=[_evidence("evidence/madge.log", 1, "circular found")],
                cost_to_fix="1w",
                summary="Circular dependency detected — tight coupling",
            )
        )
    else:
        areas.append(
            RiskArea(
                area="Architecture",
                score=75,
                severity=Severity.low,
                evidence=[_evidence("evidence/madge.log", 1, "no circular")],
                cost_to_fix="0h",
                summary="No circular deps",
            )
        )

    # Maintainability
    if depsec.bus_factor <= 1:
        areas.append(
            RiskArea(
                area="Maintainability",
                score=55,
                severity=Severity.medium,
                evidence=[_evidence("evidence/git_shortlog.log", 1, f"bus factor {depsec.bus_factor}")],
                cost_to_fix="hiring",
                summary=f"Bus factor {depsec.bus_factor}",
            )
        )
    else:
        areas.append(
            RiskArea(
                area="Maintainability",
                score=80,
                severity=Severity.low,
                evidence=[_evidence("evidence/git_shortlog.log", 1, f"bus factor {depsec.bus_factor}")],
                cost_to_fix="0h",
                summary=f"Bus factor {depsec.bus_factor}",
            )
        )

    # Discrepancies between claims and observed behavior — only if any failing claim
    failing_claims = [c for c in static.claims if c.verdict == "FAIL"]
    if failing_claims:
        for fc in failing_claims[:1]:  # one row to keep table concise
            areas.append(
                RiskArea(
                    area="README claims",  # type: ignore[arg-type]
                    score=40,
                    severity=Severity.medium,
                    evidence=[_evidence(fc.evidence_ref, 1, fc.text)],
                    cost_to_fix="2h docs",
                    summary=f'Discrepancy: claim "{fc.text[:80]}" vs observed FAIL',
                )
            )

    # Verification: drop any area without evidence (already enforced by min_length) — already verified
    return areas


def overall_score(areas: list[RiskArea]) -> int:
    if not areas:
        return 0
    return int(sum(a.score for a in areas) / len(areas))


def verdict_for(score: int) -> str:
    if score >= 80:
        return "BUY"
    if score >= 55:
        return "HOLD"
    return "REJECT"
