# 02_ARCHITECTURE — 100 Steps Ahead

## 1. Tech Stack (locked, Python per Frontier allowed list)
- **Language:** Python 3.11+ (type hints 100%, mypy strict)
- **Orchestration:** LangGraph (graph of agents) — alternative: explicit Python orchestrator if LangGraph overkill, decision logged
- **Server/CLI:** FastAPI (if API needed) + Typer CLI (`python -m codecat`)
- **Sandbox:** Docker 29.x (isolated, reproducible) + `docker run --network none` where possible
- **Tools (called via subprocess, NOT LLM hallucination):**
  - `git clone --depth 1`, `git log --stat --since="18 months ago"`, `git shortlog -sn`
  - `npm ci` / `pip install -r requirements.txt` (captured)
  - `npm test` / `pytest` / `npm audit --json` / `pip-audit --format=json`
  - `npx madge --circular src/` or `import-linter` for JS/TS circular deps
  - `radon` / `complexipy` for complexity (Python)
  - `docker build` if Dockerfile exists
  - `du`, `cloc` for size
- **LLM:** OpenAI GPT-4o-mini / Anthropic where needed for claim parsing & report synthesis (disclosed, trajectories logged)
- **Quality:** `ruff`, `mypy --strict`, `pytest --cov=80`, `pre-commit`

## 2. System Diagram
```
CLI (Typer) ──→ Orchestrator (LangGraph, memory: repoMap)
                │
                ├─→ BuildAgent (tool: clone → install → test → docker build) ──→ logs/
                ├─→ DepSecAgent (npm audit / pip-audit + git history bus factor) ──→ audit.json
                ├─→ StaticClaimAgent (circular deps + complexity + README claim cross-check) ──→ claim_check.json
                │
                └─→ AggregatorAgent (LLM: scores 0-100 per area, severity, evidence links, cost)
                     │
                     └─→ FixPlannerAgent (rule-based: pick TOP 1 fixable)
                          │
                          └─→ FixerAgent (LLM patch) → Verifier (re-clone CLEAN sandbox → apply diff → re-run tests) loop 2x
                               │
                               └─→ HumanGate (typer confirm) → ReportGenerator (markdown)
```

## 3. Agents — Responsibilities & Prompts (see 06_AGENT_INSTRUCTIONS.md)

| Agent | Input | Tools | Output | Memory |
|-------|-------|-------|--------|--------|
| BuildAgent | repo URL | `git clone`, `npm ci`, `pip install`, `npm test`, `pytest`, `docker build` | `install.log`, `test.log`, `docker.log` + PASS/FAIL boolean | repo path, test cmd detected |
| DepSecAgent | repo path | `npm audit`, `pip-audit`, `git log`, `git shortlog` | `audit.json`, `git.log`, bus factor, abandoned files | dep list |
| StaticClaimAgent | repo path + README.md | `madge`, `radon`, `cloc`, LLM claim extractor | `madge.out`, `complexity.json`, `claim_check.json` (README "npm test passes" → actual FAIL) | claim list |
| Aggregator | all logs | LLM synthesis | `scores.json` + evidence table | all evidence |
| FixPlanner | scores.json | rule engine | `fix_target.json` (file, line, CVE, type) | top risk |
| Fixer | fix_target + code snippet | LLM + `apply_patch` tool | `patch.diff` | attempt count |
| Verifier | patch.diff + clean clone | `git apply` + re-run build/tests in NEW sandbox | `after.log` + PASS/FAIL | verification result |
| ReportGen | all | markdown templating | `report.md` + `reproduction.sh` | final |

**Verification is mandatory:** Every score must have at least one evidence file reference. Verifier deletes hallucinated claims (score without evidence dropped).

## 4. Memory
- Orchestrator carries `RepoMap` (file tree, package manager detected, test command, Dockerfile exists, README claims) across agents
- No persistent DB needed for MVP (per-repo folder). Future: SQLite for cross-repo cache

## 5. Data Flow & Evidence
1. `orchestrator.py` creates `out/<repo_hash>/evidence/` and runs agents sequentially but Build/DepSec/Static in parallel where possible
2. Each tool call writes raw log (never LLM generated)
3. Aggregator reads logs, produces `scores.json` (structured), then `report.md` renders it
4. Verifier runs in **FRESH** Docker container to avoid contamination — proves reproducibility

## 6. File Structure (100% quality, typed, tested)
```
codecat/
  README.md, AGENTS.md, PROGRESS.md
  docs/*.md
  pyproject.toml, Dockerfile, .gitignore, .pre-commit-config.yaml
  src/codecat/
    __init__.py
    cli.py              # Typer entry
    orchestrator.py     # LangGraph or manual DAG
    agents/
      build_agent.py
      depsec_agent.py
      static_claim_agent.py
      aggregator.py
      fix_planner.py
      fixer.py
      verifier.py
      report_gen.py
    tools/
      sandbox.py        # docker run wrappers
      git_tools.py
      audit_tools.py
      static_tools.py
    models/
      schemas.py        # Pydantic for scores, evidence
    evaluation/
      dataset.py        # 10_repos.json loader
      baseline.py       # single-prompt baseline
      harness.py        # runs both, computes Spearman
      rubric.py
  datasets/
    10_repos.json       # locked list + expert ranks
  tests/
    test_agents.py
    test_tools.py
    test_evaluation.py
    test_cli.py         # coverage 80%+
  trajectories/
    express_before.json # logged per agent
  out/                  # gitignored, per-run evidence
  evaluation_results/
```

## 7. Failure Modes & Handling (correct, testable)
- Retries: install/test timeouts → retry 1x, log timeout
- Partial writes: patch apply fails → Fixer retries with smaller diff
- Duplicate messages: dedup by repo URL hash
- Concurrent access: file locks on out/ (single repo at a time for MVP)
- Hidden deps: if `package-lock` missing, run `npm install` and capture warning

## 8. Performance
- Per repo: <12 min (clone 1m + install 3m + tests 3m + audit 1m + LLM 2m + verify 2m)
- 10 repos sequential: ~2h total evaluation

## 9. Decisions to Log in Changelog
- LangGraph vs manual DAG (measure overhead)
- Added verification (dropped hallucinated scores)
- Changed orchestration from sequential → parallel Build/DepSec

## 10. Security & Compliance
- No secrets in logs/trajectories (redact if needed)
- Sandbox network disabled where possible, no host file writes outside out/
