# CodeCat — Risk2Fix Auditor
### Micro1 Frontier Engineering Challenge 2026 (Agentic Workflows Hackathon)

**One-liner:** Paste a GitHub URL → Get an evidence-backed risk report (72/100) + 1 verified fix with before/after sandbox proof.

**Working directory:** `D:\hacakthon\codecat` | **Language:** Python (core) + TypeScript (optional viewer) | **Solo, Teamsize 1, No feature creep after lock**

---

## Who has this problem?
**Buyer/acquirer of an unfamiliar repository** (indie hacker, micro-SaaS buyer, eng lead inheriting code). They did not build it and must decide price / whether to acquire / how much refactoring will cost — under time pressure.

## What bottleneck makes it worth solving?
A README and demo can look excellent while hiding: broken tests, dead deps, CVEs, circular deps, bus factor 1, undocumented deployment. Buyer must manually clone, install, run tests, audit deps, read git history, verify README claims. Judgment is inconsistent and takes 3-8 hours per repo. Without reproducible evidence, valuation is guesswork.

## Does the agent solve it well?
Yes — **Risk2Fix** does not just score. It *reproduces*:

```
GitHub URL
  → Clone in isolated sandbox (no host side effects)
  → Build Agent tries docker build / npm ci / pip install / tests — captures REAL logs
  → Dependency/Security Agent: npm audit / pip-audit + git log --stat (abandoned files, bus factor)
  → Static/Claim Agent: complexity, duplication, circular deps + README claim cross-check ("npm test passes" → actually FAIL)
  → Risk Aggregator: 0-100 score per area, EVERY row → file:line or log:line evidence
  → Fix Planner: picks TOP 1 fixable (broken build OR 1 critical CVE dep update)
  → Fixer+Verifier Loop: patches in sandbox, re-runs build/tests in CLEAN sandbox, must PASS (2 retries max)
  → Human gate approves patch (ground rule 04/05)
  → Final memo: Before/After score + evidence table + before.log/after.log + patch.diff + reproduction commands
```

**Output example:**
```
Technical Risk Score: 72 → 84 (after fix)

Area           Score  Evidence
Testing        41     3/12 tests fail — logs/run_test.log:42
Dependencies   83     lodash 4.17.19 CVE-2020-8203 — audit.json:8
Architecture   67     circular dep src/a.ts -> b.ts -> a.ts — madge.out:3
Security       52     pip-audit 2 highs — pip-audit.json:5
Maintainability 71    bus factor 1, 4 files untouched 18mo — git.log:88
README claims  FAIL  claims "docker build works" — docker.log:19 FAIL

Fix applied: bump lodash 4.17.19 → 4.17.21, tests now 12/12 pass — see after.log
```

## Can another person reproduce the result?
Yes. Every score links to a file/log. Reproduction guide gives exact `docker run` + `python -m codecat audit <url>` + `pytest` commands, versions, runtime, cost. Trajectories show agent instructions → tool responses → retries.

## Baseline vs Advanced (locked)
- **Simple Baseline:** One LLM prompt with README + file tree → score + generic suggestion (no tools, no sandbox, no evidence links). This is the fair basic way.
- **Agent Solution (Risk2Fix):** Orchestrated 5-agent system with sandbox execution + verification + memory. Same 10 repos, same rubric, same logs.

## How judges verify improvement
10 locked public repos (Python/JS only). 2 human reviewers rank independently with shared rubric. Metrics: `Spearman rank correlation vs experts | Factual accuracy % claims with valid evidence | Critical issue recall | Fix verification rate (before FAIL → after PASS in clean sandbox) | Human time saved`. One challenging case where README lies.

## Ground rules compliance
Sandbox for all consequential actions, human approval before patch PR, synthetic/public data only, no credentials, licenses respected, every claim tied to evidence (see docs/03_REPRODUCIBILITY.md).

## Quick start (after build)
```bash
docker build -t codecat .
docker run --rm -v $(pwd)/out:/out codecat audit https://github.com/example/repo --out /out/report.md
python -m codecat evaluate --dataset datasets/10_repos.json --baseline --advanced
```

## Docs
- `docs/01_PRD.md` — locked product spec, no feature creep
- `docs/02_ARCHITECTURE.md` — agents, tools, data flow
- `docs/03_REPRODUCIBILITY.md` — legal & sandbox & human gate
- `docs/04_EVALUATION.md` — 10 repos, rubric, metrics
- `docs/05_DELIVERABLES.md` — submission checklist
- `docs/06_AGENT_INSTRUCTIONS.md` — prompts for each agent
- `PROGRESS.md` — 100-step tracker
- `AGENTS.md` — rules for any agent picking up this project
