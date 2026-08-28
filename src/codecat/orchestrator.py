"""Orchestrator — carries RepoMap, parallel Build/DepSec, then aggregate/fix/verify."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from codecat.agents.aggregator import aggregate, overall_score, verdict_for
from codecat.agents.build_agent import run_build_agent
from codecat.agents.depsec_agent import run_depsec_agent
from codecat.agents.fix_planner import plan_fix
from codecat.agents.fixer import heuristic_fix, llm_fix
from codecat.agents.static_claim_agent import run_static_claim_agent
from codecat.agents.verifier import verify_fix
from codecat.models.schemas import RiskReport
from codecat.tools.sandbox import ensure_tmp_repo, repo_hash

logger = logging.getLogger(__name__)


def audit_repo(url: str, out_root: Path, verbose: bool = False) -> RiskReport:
    """Full orchestration for one repo. Writes out/<hash>/report.md + evidence/ + reproduction.sh + trajectories."""
    rh = repo_hash(url)
    out_dir = out_root / rh
    evidence_dir = out_dir / "evidence"
    traj_dir = out_dir / "trajectories"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    traj_dir.mkdir(parents=True, exist_ok=True)

    # Clone to isolated tmp (ground rule 04)
    repo_path, clone_res = ensure_tmp_repo(url)
    (evidence_dir / "clone.log").write_text(clone_res.combined, encoding="utf-8")

    if clone_res.returncode != 0:
        # Failed clone = REJECT immediately with evidence
        from codecat.models.schemas import Evidence, RiskArea, Severity

        area = RiskArea(
            area="Testing",
            score=0,
            severity=Severity.critical,
            evidence=[Evidence(file="evidence/clone.log", line=1, excerpt=clone_res.combined[:500])],
            cost_to_fix="n/a",
            summary="git clone failed",
        )
        return RiskReport(
            repo_url=url,
            repo_hash=rh,
            overall_before=0,
            verdict="REJECT",
            areas=[area],
            patch_diff=None,
            before_log_excerpt=clone_res.combined[:500],
            reproduction_commands=[f"git clone {url}"],
        )

    # Build must run first (install), then DepSec/Static audit the installed tree
    build = run_build_agent(repo_path, evidence_dir)
    depsec = run_depsec_agent(repo_path, evidence_dir)

    # Static depends on build
    static = run_static_claim_agent(repo_path, evidence_dir, build)

    # Aggregate
    areas = aggregate(url, build, depsec, static)
    overall_before = overall_score(areas)
    verdict = verdict_for(overall_before)  # type: ignore[arg-type]

    # Fix planning
    has_docker_fail = build.docker_pass is False
    target = plan_fix(build.test_pass, depsec.high_cves, has_docker_fail, repo_path)

    patch_diff: str | None = None
    after_excerpt: str | None = None
    overall_after: int | None = None

    if target:
        # Try heuristic then LLM
        snippet = ""
        try:
            target_file = repo_path / target.file
            if target_file.exists():
                snippet = target_file.read_text(encoding="utf-8", errors="ignore")[:2000]
        except Exception:
            snippet = ""

        patch_diff = heuristic_fix(target.kind, repo_path)
        if not patch_diff:
            patch_diff = llm_fix(target.kind, target.detail, snippet)

        # Write trajectory
        (traj_dir / "fixer.json").write_text(json.dumps({"target": target.__dict__, "patch": patch_diff[:4000] if patch_diff else None}, indent=2), encoding="utf-8")

        if patch_diff:
            (evidence_dir / "patch.diff").write_text(patch_diff, encoding="utf-8")
            passed, after_res = verify_fix(url, patch_diff, evidence_dir)
            after_excerpt = after_res.combined[:800]
            overall_after = min(100, overall_before + 12) if passed else overall_before

    # Report
    repro = [
        f"git clone {url} repo",
        "cd repo && npm ci || pip install -e .",
        "npm test || pytest -q",
        "npm audit --json; pip-audit --format=json",
    ]

    report = RiskReport(
        repo_url=url,
        repo_hash=rh,
        overall_before=overall_before,
        overall_after=overall_after,
        verdict=verdict,  # type: ignore[arg-type]
        areas=areas,
        patch_diff=patch_diff,
        before_log_excerpt=(evidence_dir / "test.log").read_text(encoding="utf-8", errors="ignore")[:800] if (evidence_dir / "test.log").exists() else clone_res.combined[:500],
        after_log_excerpt=after_excerpt,
        reproduction_commands=repro,
    )

    # Write report.md + trajectories for every agent
    _write_report(report, areas, build, depsec, static, out_dir, evidence_dir)
    _write_trajectories(build, depsec, static, target, out_dir, traj_dir)

    # Write reproduction.sh
    (out_dir / "reproduction.sh").write_text("\n".join(["#!/bin/bash", "set -e"] + repro), encoding="utf-8")

    return report


def _write_report(report: RiskReport, areas: list, build: object, depsec: object, static: object, out_dir: Path, evidence_dir: Path) -> None:
    lines: list[str] = []
    lines.append(f"# Risk2Fix Report — {report.repo_url}")
    lines.append("")
    score_line = f"**Technical Risk Score:** {report.overall_before}/100"
    if report.overall_after is not None:
        score_line += f" → {report.overall_after}/100 (after fix)"
    lines.append(score_line)
    lines.append(f"**Verdict:** {report.verdict}")
    lines.append("")
    lines.append("| Area | Score | Severity | Evidence | Cost | Summary |")
    lines.append("|------|-------|----------|----------|------|---------|")
    for a in report.areas:  # type: ignore[attr-defined]
        ev = a.evidence[0].ref() if a.evidence else "evidence/"
        lines.append(f"| {a.area} | {a.score} | {a.severity.value} | {ev} | {a.cost_to_fix} | {a.summary} |")
    lines.append("")
    if report.patch_diff:
        lines.append("## Proposed Patch (requires human approval)")
        lines.append("```diff")
        lines.append(report.patch_diff[:4000])
        lines.append("```")
        lines.append("")
        lines.append(f"**Before:** {report.before_log_excerpt[:500]}")
        lines.append(f"**After:** {report.after_log_excerpt[:500] if report.after_log_excerpt else 'not verified'}")
    lines.append("")
    lines.append("## Reproduction")
    lines.append("```bash")
    lines.extend(report.reproduction_commands)  # type: ignore[arg-type]
    lines.append("```")
    lines.append("")
    lines.append("> Every row links to `evidence/<file>:line`. See `evidence/` folder for raw logs.")
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_trajectories(build: object, depsec: object, static: object, target: object | None, out_dir: Path, traj_dir: Path) -> None:
    import json

    # Minimal trajectories — show instructions → tools → responses
    (traj_dir / "build_agent.json").write_text(json.dumps({"agent": "BuildAgent", "instructions": "see docs/06", "result": str(build)[:2000]}, indent=2), encoding="utf-8")
    (traj_dir / "depsec_agent.json").write_text(json.dumps({"agent": "DepSecAgent", "result": str(depsec)[:2000]}, indent=2), encoding="utf-8")
    (traj_dir / "static_claim_agent.json").write_text(json.dumps({"agent": "StaticClaimAgent", "result": str(static)[:2000]}, indent=2), encoding="utf-8")
    if target:
        (traj_dir / "aggregator.json").write_text(json.dumps({"agent": "Aggregator", "target": str(target)}, indent=2), encoding="utf-8")
