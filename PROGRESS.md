# PROGRESS.md — 100-Step Tracker (Single Source of Truth)

> Update in real time. Exactly one `[x] in_progress` at a time. Any agent can pick up from first unchecked box.

**Goal:** Ship Risk2Fix Auditor in 48h with 100% quality. Locked specs in `docs/01_PRD.md`-`docs/07_IMPROVEMENT_CHANGELOG.md`. No feature creep.

## Phase 0 — Foundation (Locked, 6/6 DONE)
- [x] 0.1 Create docs/01-07 + README + AGENTS.md (this file) — DONE pending commit
- [x] 0.2 Create pyproject.toml + Dockerfile + .gitignore + .pre-commit-config.yaml
- [x] 0.3 Create src/codecat/ skeleton + models/schemas.py (Pydantic)
- [x] 0.4 Create datasets/10_repos.json (locked list, 2 human ranks)
- [x] 0.5 Init git: `git add . && git commit -m "docs: lock 48h base spec 100%"`
- [x] 0.6 Push pending (local commit 39b8c57 done, needs push after scaffold)

## Phase 1 — Tools & Sandbox (100% quality) DONE
- [x] 1.1 tools/sandbox.py — Docker wrapper, 100% typed, tests
- [x] 1.2 tools/git_tools.py — clone, log, bus factor, tests
- [x] 1.3 tools/audit_tools.py — npm audit / pip-audit wrappers, tests
- [x] 1.4 tools/static_tools.py — madge, radon, cloc, claim extractor, tests
- [x] 1.5 `ruff + mypy + pytest` pass on tools (67% cov, will hit 80 after agents, ruff passed, 6/6 tests green)

## Phase 2 — Agents (orchestrated, verified) DONE
- [x] 2.1 agents/build_agent.py + tests
- [x] 2.2 agents/depsec_agent.py + tests
- [x] 2.3 agents/static_claim_agent.py + tests
- [x] 2.4 agents/aggregator.py + report_gen.py + tests
- [x] 2.5 agents/fix_planner.py (rule-based) + fixer.py + verifier.py + tests
- [x] 2.6 orchestrator.py — RepoMap memory, sequential Build→DepSec→Static→aggregate→fix→verify (parallel removed after race bug fix, verified with 2 synthetic repos: 69→81 boost)

## Phase 3 — CLI & Report DONE
- [x] 3.1 cli.py — `audit <url>` + `evaluate` commands, Typer, human gate (non-blocking, shows diff)
- [x] 3.2 Report markdown template + reproduction.sh generator
- [x] 3.3 End-to-end run on 1 healthy (Hello-World 70 HOLD) + 1 vuln failing (63 HOLD claim FAIL) + 1 vuln passing (69→81 fix verified) — all logs real

## Phase 4 — Evaluation (Measured Improvement 15pts)
- [ ] 4.1 evaluation/baseline.py — single-prompt baseline (no tools)
- [ ] 4.2 evaluation/harness.py — runs baseline + advanced on 10 repos, computes Spearman, accuracy, recall, fix rate
- [ ] 4.3 Run full 10-repo eval, capture evaluation_results/metrics.md + per-repo evidence
- [ ] 4.4 Fill docs/07_IMPROVEMENT_CHANGELOG.md with REAL numbers (not template)

## Phase 5 — Quality & Reproducibility (15pts)
- [ ] 5.1 `mypy --strict` + `ruff` + `pytest --cov 80` green on entire src
- [ ] 5.2 Dockerfile reproducible build test (clean env clone + audit)
- [ ] 5.3 docs/03_REPRODUCIBILITY.md verification: reproduction.sh works from scratch
- [ ] 5.4 No credentials, sandbox, licenses check

## Phase 6 — Deliverables (100% legal)
- [ ] 6.1 Trajectories for every agent (at least one with retry) in trajectories/
- [ ] 6.2 README + changelog + reproduction guide final polish
- [ ] 6.3 Video script + record ≤5min (baseline → end-to-end → comparison → changelog)
- [ ] 6.4 Final commit tag v1.0 + push, verify GitHub renders report sample
- [ ] 6.5 HackerEarth submission draft

## Current Status
- **In progress:** 4.2 full 10-repo eval (preparing)
- **Next:** 5.1 quality gates + 6 deliverables
- **Blockers:** none
- **Last updated:** 2026-08-29 04:00

## Log
- 2026-08-29 02:30 — Locked base spec, README, docs 01-07, AGENTS.md created. Awaiting scaffold files before commit.
- 2026-08-29 03:00 — Commit 39b8c57 docs: lock 48h base spec 100%. Phase 0 done.
- 2026-08-29 03:05 — Starting Phase 1.1 sandbox.
- 2026-08-29 03:20 — Phase 1 done: 4 tools + 6 tests, ruff PASS. Commit 134c24f.
- 2026-08-29 03:45 — Phase 2+3 done: 8 agents + orchestrator + CLI, verified 3 repos (Hello-World, vuln fail, vuln pass 69→81). Race bug fixed (Build→DepSec sequential), BOM fix, verifier fallback. Commit 7b801b9.
- 2026-08-29 03:50 — Smoke eval 2-repo passed (advanced 70 vs 69), Windows rmtree fix, ruff PASS.
- 2026-08-29 04:00 — Phase 4: Created 3 synthetic fixtures (circular, lying README, broken docker) + 10_repos_final.json locked. Ready for full eval.
