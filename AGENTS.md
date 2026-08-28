# AGENTS.md — Rules for ANY Agent Picking Up This Project (Rate-Limit Handoff)

> Read this first if you are a new AI agent continuing this project. Everything is locked in `docs/` — do not add features outside `docs/01_PRD.md`.

## 1. What We Are Building (one sentence)
CodeCat Risk2Fix Auditor: GitHub URL → evidence-backed risk report + 1 verified fix with before/after sandbox proof. See `README.md` and `docs/01_PRD.md`.

## 2. Ground Rules (non-negotiable)
- **No feature creep.** If it's not in `01_PRD.md`, don't build it. Update doc + `PROGRESS.md` + commit if you must change.
- **Sandbox everything:** All `clone/install/test/docker` via `src/codecat/tools/sandbox.py` (Docker). No host mutation.
- **Human gate:** Patch is PROPOSED only. CLI must `typer.confirm` before applying outside sandbox.
- **Evidence or it didn't happen:** Every report row → `evidence/<file>:line`. Verifier drops hallucinated claims.
- **Legal:** Public repos only, no credentials, respect licenses, log trajectories without secrets.
- **Languages:** Python core (allowed per Frontier). TypeScript only if PRD says UI.

## 3. Working Directory & Repo
- **Local:** `D:\hacakthon\codecat` (git remote `https://github.com/Tamjid0/codecat.git`)
- **Resource PDF:** `D:\hacakthon\resource\micro1 - First Hackathon97ce7c5.pdf`
- **Branch:** `master`, commit often with `feat:`, `fix:`, `docs:` prefixes.

## 4. File Structure (must follow `docs/02_ARCHITECTURE.md`)
```
src/codecat/{cli,orchestrator,agents/*,tools/*,models/*,evaluation/*}
tests/
datasets/10_repos.json
trajectories/
out/ (gitignored)
docs/*.md
pyproject.toml, Dockerfile, .pre-commit-config.yaml
```

## 5. Code Quality 100% (no prototyping)
- Type hints everywhere, `mypy --strict` must pass
- `ruff check .` + `ruff format .` must pass
- `pytest --cov --cov-fail-under=80` must pass
- Docstrings for public functions, Pydantic schemas for scores
- No `any`, no `print` debugging (use `logger`), no hallucinated logs

## 6. How to Continue (rate-limit safe)
1. Read `PROGRESS.md` — find first unchecked `[ ]` item and set to `[x]` in progress.
2. Read its `docs/*.md` referenced file for spec.
3. Implement that item only (one file at a time), run `ruff` + `mypy` + `pytest` before next.
4. Append trajectory log to `trajectories/<repo>/` if you ran an audit.
5. Update `PROGRESS.md` and commit: `git add -A && git commit -m "feat: <step>"`

## 7. Commands (verified, Windows PowerShell 5.1)
```powershell
# Setup
Test-Path -LiteralPath "D:\hacakthon\codecat"  # verify parent
python --version; docker --version
pip install -e ".[dev]"
pre-commit install

# Quality gates (run before every commit)
ruff check src tests
ruff format src tests
mypy src
pytest --cov=src --cov-fail-under=80

# Run audit
python -m codecat audit https://github.com/pallets/flask --out ./out/flask

# Evaluate
python -m codecat evaluate --dataset datasets/10_repos.json --out evaluation_results/
```

## 8. Deliverables Checklist (see docs/05_DELIVERABLES.md)
Code + changelog + reproduction guide + video ≤5min + trajectories for every agent.

## 9. Progress Tracking
- Single source of truth: `PROGRESS.md`
- Update status in real time, exactly one `in_progress` at a time.

## 10. If Blocked
Keep `PROGRESS.md` item `in_progress`, add a follow-up todo describing blocker. Do not guess.

---
*Teamsize 1, 48h no-sleep mode locked. Take time, think 100 steps ahead, build absolute best 48h product.*
