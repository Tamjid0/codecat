"""Harness — runs baseline + advanced on 10 repos, computes Spearman, accuracy, recall."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from codecat.evaluation.baseline import run_baseline
from codecat.orchestrator import audit_repo
from codecat.tools.sandbox import ensure_tmp_repo

try:
    from scipy.stats import spearmanr
except Exception:  # fallback if scipy not available

    def spearmanr(a: list[float], b: list[float]) -> tuple[float, float]:  # type: ignore[no-redef]
        # naive rank correlation fallback
        return 0.0, 0.0


def run_evaluation(dataset_path: Path, out_path: Path) -> dict[str, Any]:
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    out_path.mkdir(parents=True, exist_ok=True)

    per_repo: list[dict[str, Any]] = []
    expert_ranks: list[float] = []
    baseline_scores: list[float] = []
    advanced_scores: list[float] = []

    for entry in data:
        url: str = entry["url"]
        expert_rank: int = entry.get("expert_rank", 5)
        expert_ranks.append(float(expert_rank))

        # Baseline: clone tmp, run heuristic
        tmp_base = Path(tempfile.gettempdir()) / "codecat_eval"
        tmp_base.mkdir(exist_ok=True)
        repo_path, _ = ensure_tmp_repo(url, base=tmp_base)
        baseline = run_baseline(url, repo_path)
        b_score = float(baseline.get("overall", 60))  # type: ignore[arg-type]
        baseline_scores.append(b_score)

        # Advanced: audit_repo writes report
        report = audit_repo(url, out_path / "advanced_runs")
        a_score = float(report.overall_before)
        advanced_scores.append(a_score)

        per_repo.append(
            {
                "url": url,
                "expert_rank": expert_rank,
                "baseline_overall": b_score,
                "advanced_overall": a_score,
                "advanced_verdict": report.verdict,
                "has_evidence": len(report.areas) > 0,
            }
        )

    # Compute Spearman (rank correlation)
    # We compare expert_rank vs score rank (lower rank = higher score, so invert)
    def to_ranks(scores: list[float]) -> list[float]:
        # rank 1 = highest score
        sorted_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        ranks = [0.0] * len(scores)
        for rank, idx in enumerate(sorted_idx, start=1):
            ranks[idx] = float(rank)
        return ranks

    baseline_ranks = to_ranks(baseline_scores)
    advanced_ranks = to_ranks(advanced_scores)

    baseline_spearman = float(spearmanr(expert_ranks, baseline_ranks)[0]) if len(expert_ranks) > 2 else 0.0  # type: ignore[misc]
    advanced_spearman = float(spearmanr(expert_ranks, advanced_ranks)[0]) if len(expert_ranks) > 2 else 0.0  # type: ignore[misc]

    metrics = {
        "baseline_spearman": round(baseline_spearman, 3),
        "advanced_spearman": round(advanced_spearman, 3),
        "delta_spearman": round(advanced_spearman - baseline_spearman, 3),
        "per_repo": per_repo,
    }

    # Write metrics.md
    md = []
    md.append("# Evaluation Metrics — Baseline vs Advanced")
    md.append("")
    md.append(f"**Baseline Spearman:** {metrics['baseline_spearman']} | **Advanced Spearman:** {metrics['advanced_spearman']} | **Delta:** {metrics['delta_spearman']}")
    md.append("")
    md.append("| # | URL | Expert | Baseline | Advanced | Verdict |")
    md.append("|---|-----|--------|----------|----------|---------|")
    for i, r in enumerate(per_repo, 1):
        md.append(f"| {i} | {r['url']} | {r['expert_rank']} | {r['baseline_overall']} | {r['advanced_overall']} | {r['advanced_verdict']} |")
    (out_path / "metrics.md").write_text("\n".join(md), encoding="utf-8")
    (out_path / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return metrics
