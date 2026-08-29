# 01_PRD — Locked Product Spec (NO FEATURE CREEP)

> **Rule:** Nothing outside this doc is built in the 48h. If it's not here, it's out of scope. Any change requires updating this doc + PROGRESS.md + git commit.

## 1. Product Name
**CodeCat — Risk2Fix Auditor** (repo: Tamjid0/codecat)

## 2. Problem Statement (judging: Problem & User Value 15pts)
Buyer of unfamiliar repo wastes 3-8h per repo manually verifying quality. Repository claims may not match observed behavior (tests broken, deps vulnerable, Docker fails). Wrong valuation costs $10k-$100k.

## 3. Target User
Primary: Individual buyer of micro-SaaS / private repo (solo founder, eng lead). Secondary: Engineer inheriting legacy repo. We are our own test user (we understand the pain).

## 4. Locked Scope — MVP (48h, Solo, 100% quality, no prototype)
### Input
- Single GitHub public URL (Python or JavaScript/TypeScript repo only, <50k LOC, <5k stars to keep clone fast)
- Optional: branch/tag (default main)

### Output (single self-contained artifact, end-to-end quality 20pts)
1. `report.md` — Human-signable diligence memo:
   - Header: Risk Score 0-100 (before) → 0-100 (after fix if any)
   - Verdict: BUY / HOLD / REJECT + price adjustment note
   - Evidence table (5 areas): Testing, Dependencies, Security, Architecture, Maintainability (+ README claims row)
     - Columns: Area | Score | Severity | Evidence (file:line or log:line) | Cost to fix
   - Before/After proof: `before.log` / `after.log` excerpts + `patch.diff`
2. `evidence/` folder: raw logs (`clone.log`, `install.log`, `test.log`, `audit.json`, `pip-audit.json`, `madge.out`, `git.log`, `claim_check.json`)
3. `reproduction.sh` — exact commands to re-run

### Out of Scope (explicitly NOT built)
- No auto-PR to GitHub (human gate required)
- No Java/Go/Rust analysis
- No fixing more than 1 issue per repo
- No UI dashboard (CLI + markdown only for 48h; viewer is post-hackathon)
- No private repo auth (public only, legal)
- No architecture refactor fixes (only build/test/CVE dep bump)

## 5. User Flow (realistic execution for video)
1. User runs: `python -m codecat audit https://github.com/expressjs/express --out ./out`
2. Agent shows trajectory: clone → install → test FAIL → audit CVE → aggregate → fix lodash → re-run PASS
3. Opens `out/report.md` — readable, evidence-linked
4. Runs `cat out/evidence/test.log` to verify

## 6. How It Looks (final quality bar)
- Report is not AI slop: concise, tables, severity colors (markdown), each claim hyperlinked to evidence file
- Logs are real tool output, not LLM generated
- Patch is `git diff` that applies cleanly
- If report says `Tests 12/12 pass`, `test.log` ends with `12 passed`

## 7. Success Criteria (user would sign name)
- For a healthy repo: Report says 85+ and no fix needed, all logs show PASS
- For a broken repo: Report finds REAL failure (not hallucinated), fix makes tests PASS in CLEAN sandbox
- Expert reviewers would agree with ranking (±1 position)

## 8. Constraints (100% legal)
- Sandbox: Docker for all installs/tests (ground rule 04)
- Human approval: patch not auto-applied outside sandbox
- Data: public repos only, synthetic if needed
- Licenses: respect MIT/Apache, use tools per terms
- No credentials in repo/trajectories

## 9. Non-goals for 48h
- No cloud deployment, no auth, no payment
- No handling of repos >50k LOC or with native binaries that need GPU

## 10. Definition of Done
- `python -m codecat audit <url>` produces report.md + evidence/ + reproduction.sh in <12 min per repo on laptop
- `pytest tests/` passes with 80%+ coverage, `ruff check .` and `mypy .` pass
- 10-repo evaluation reproduces rank correlation delta baseline → advanced
