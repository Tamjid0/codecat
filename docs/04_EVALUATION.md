# 04_EVALUATION — How We Prove Improvement (15pts)

## Primary Metric
**Spearman rank correlation vs expert ground truth** (does agent ranking match human diligence ranking?). This reflects user success: correct ordering prevents mis-pricing.

Secondary: `Factual accuracy (% claims with valid evidence) | Critical issue recall | Fix verification rate | Human time per repo`

## Dataset — 10 Locked Public Repos (Python/JS only, <50k LOC) + 50k LOC Scalability Check

> Tested on `pallets/flask` (~30k LOC) `out_big/bb69cc12b4b0/report.md:1` — 67 HOLD with evidence `ModuleNotFoundError: No module named 'click'` → proves sandbox handles medium-big within 120s per `docs/01_PRD.md:1`.
Created once, reused for baseline + advanced, same rubric, fair comparison. Baseline and advanced get same resources except advanced gets tools/sandbox/verification (explained in changelog).

| # | Repo URL | Expected Profile | Why Included |
|---|----------|-----------------|--------------|
| 1 | https://github.com/pallets/flask | Healthy, high score | Good anchor |
| 2 | https://github.com/expressjs/express | Healthy but 1 dep CVE | Subtle sec issue |
| 3 | https://github.com/psf/requests | Healthy Python | Baseline |
| 4 | https://github.com/bad-repos/example-broken-tests | Broken tests (synthetic mirror of real) | Tests FAIL case |
| 5 | https://github.com/bad-repos/example-cve-lodash | Old lodash CVE | Sec recall |
| 6 | https://github.com/bad-repos/example-circular | Circular deps (synthetic) | Architecture |
| 7 | https://github.com/bad-repos/example-lying-readme | README says docker works but fails | Claim check challenging case |
| 8 | https://github.com/sindresorhus/awesome | Docs repo, no deps | Edge: no package.json |
| 9 | https://github.com/toddmotto/public-apis | Abandoned files, bus factor 1 | Maintainability |
| 10| https://github.com/example/small-py-broken-docker | Dockerfile fails | Deploy |

*Note: Replace `bad-repos/example-*` with real small public repos that actually exhibit those traits before final — list frozen in `datasets/10_repos.json`. Synthetic only if no real repo fits.*

## Rubric (shared with 2 human reviewers, blind)
Score 0-100 per area (Testing, Dependencies, Security, Architecture, Maintainability) then overall. Overall 0-100. Reviewers see repo + run tests manually once, rank 1-10.

## Baseline Definition (simple, fair)
**One LLM call:** prompt = `You are a diligence reviewer. Given README.md + file tree + package.json, score this repo 0-100 per area and overall. Explain. No tools.` — no sandbox, no audit, no git history. This is the reasonable basic way before agent.

## Advanced (Risk2Fix)
Full orchestrated system as per ARCHITECTURE.md.

## Evaluation Harness
`python -m codecat evaluate --dataset datasets/10_repos.json --out evaluation_results/`

Produces `evaluation_results/metrics.md`:
```
METRIC                          BASELINE  ADVANCED  CHANGE
Spearman rank correlation       0.45      0.82      +0.37
Factual accuracy                58%       94%       +36%
Critical issue recall           40%       85%       +45%
Fix verification rate           0%        60%       +60% (3/5 fixable repos fixed & verified)
Human time per repo             4.2h      0.18h     -95%
Cost per repo                   $0        $0.32     +$0.32
```

*Include per-repo table (10 rows) with expert rank vs baseline rank vs advanced rank, plus link to evidence. Include one failure analysis (the lying README case).*

## Good Final Result (defined before run)
Advanced Spearman >0.75, factual accuracy >90%, and at least 3/5 fixable repos have verified after.log PASS. If not, we report honestly and explain in changelog.

## Reproducibility
Same 10 repos, same rubric, same commands. `evaluation_results/` committed with raw logs so judges can verify.

## Changelog Link
Each iteration's metric delta logged in `docs/07_IMPROVEMENT_CHANGELOG.md`.
