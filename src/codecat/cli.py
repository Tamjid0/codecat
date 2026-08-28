"""CLI — audit <url> + evaluate. Human gate before patch apply."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from codecat.orchestrator import audit_repo

app = typer.Typer(add_completion=False)
console = Console()




@app.command()
def audit(
    url: str = typer.Argument(..., help="GitHub URL to audit"),
    out: str = typer.Option("./out", "--out", help="Output root"),
    verbose: bool = typer.Option(False, "--verbose"),
) -> None:
    """Audit one repo: clone → build → audit → aggregate → fix → verify → report."""
    out_root = Path(out)
    out_root.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold]Auditing {url}[/bold] -> {out_root}")
    report = audit_repo(url, out_root, verbose=verbose)
    console.print(f"[green]Done. Score {report.overall_before} -> {report.overall_after} Verdict {report.verdict}[/green]")
    console.print(f"Report: {out_root / report.repo_hash / 'report.md'}")
    if report.patch_diff:
        console.print("[yellow]Proposed patch requires human approval. See evidence/patch.diff[/yellow]")
        # Human gate (ground rule 04/05) — non-blocking for CI; show diff quietly
        console.print(report.patch_diff[:3000])


@app.command()
def evaluate(
    dataset: str = typer.Option("datasets/10_repos.json", "--dataset"),
    out: str = typer.Option("evaluation_results", "--out"),
) -> None:
    """Run baseline vs advanced on 10 repos dataset. For 48h MVP, delegates to harness."""
    from codecat.evaluation.harness import run_evaluation

    out_path = Path(out)
    dataset_path = Path(dataset)
    console.print(f"Evaluating {dataset_path} -> {out_path}")
    metrics = run_evaluation(dataset_path, out_path)
    console.print(json.dumps(metrics, indent=2))
    console.print(f"[green]Metrics written to {out_path / 'metrics.md'}[/green]")


if __name__ == "__main__":
    app()
