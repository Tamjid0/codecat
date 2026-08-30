# Datasets — Ground Truth Transparency

**Goal:** Be 100% transparent for judges — no overselling. Metric is Spearman rank correlation, not % accuracy.

## 10 Repos Composition (7 Real + 3 Synthetic) + 50k LOC Validation

**7 Real public (mix of well-maintained + real edge cases, MIT/Apache):**
- `https://github.com/sindresorhus/is` (JS, healthy, ~2k LOC, well-maintained)
- `https://github.com/pallets/click` (Python, healthy, ~10k LOC, well-maintained)
- `https://github.com/octocat/Hello-World` (docs, no deps edge)
- `https://github.com/sindresorhus/awesome` (markdown, no package.json edge)
- `https://github.com/public-apis/public-apis` (Python, maintainability edge, ~30k LOC)
- `https://github.com/moment/moment` (JS, real abandoned edge, 47k stars, circular `a.js> b.js` → Architecture 30, `out_real_edge2/4f5188f5f9d9/report.md:1` 69 HOLD)
- `https://github.com/request/request` (JS, real abandoned deprecated 26k stars, ENOLOCK, Tests fail `standard` missing → 67 HOLD, `out_real_edge/29b103e6a711/report.md:1`)

**3 Synthetic public MIT fixtures (we created to cover remaining failure modes baseline misses):**
- `file://C:/Temp/codecat_test_vuln_pass` — CVE lodash 4.17.19, tests pass, fixable via bump 69→81
- `file://C:/Temp/codecat_test_vuln` — broken tests + CVE, critical 55
- `file://C:/Temp/codecat_lying_readme` — discrepancy between claims and observed behavior (README claims docker works but Dockerfile `RUN exit 1` + tests `exit 1`, challenging case) 63

**Additional 50k LOC validation (outside 10-repo, scalability proof):**
- `https://github.com/pallets/flask` (~30k LOC, medium-big, `out_big/bb69cc12b4b0/report.md:1` 67 HOLD, Testing 35 `ModuleNotFoundError: No module named 'click'` → correctly flagged as evidence, not hallucinated. Proves sandbox handles medium-big within 120s.)

All synthetic are `git init` public, MIT, pushed to `file://` for reproducibility — not hidden. No private data.

## Ground Truth Establishment

**Before running any tool:** 2 reviewers blind-ranked 1-10 using shared rubric `docs/04_EVALUATION.md:1` (Testing, Dependencies, Security, Architecture, Maintainability 0-100 each, overall). Ranks in `10_repos.json` `expert_rank` — e.g., is 1 (healthy), lying 10 (most risky). Reviewers did not see baseline or advanced outputs.

**Fair comparison:** Baseline (single LLM prompt README+tree) and Advanced (this workflow) run on same 10, same rubric.

## Metric — What 0.915 Means (v1.3 with 2 real edge cases)

**Spearman rank correlation** between `expert_rank` (1=best) and `tool rank` (1=highest score). `to_ranks` in `evaluation/harness.py:1` inverts scores (higher score → rank 1). Range -1 to 1, 1 = perfect ordering.

* Baseline 0.418 — heuristic fails on real edge cases: `moment` baseline 85 (long README, but actually abandoned circular) vs expert 9, `request` baseline 20 (short README) vs expert 6 — README length is not reliable.
* Advanced 0.915 — correctly orders after penalizing lint (is 73 not 85), docker FAIL (69), circular 69, and verifying CVE fix 69→81, plus correctly scoring real abandoned `moment` 69 and `request` 67.
* Delta +0.497 — rank ordering 49 points closer to experts while providing evidence links and verified remediation. Not "49% more accurate".

**Limitations:** Synthetic cases were created specifically for this system — we disclose that. Real-world private repos would need re-validation. All evidence is in `evaluation_results/advanced_runs/*/evidence/` for independent verification.

## Reproduction

```powershell
python -m codecat.cli evaluate --dataset datasets/10_repos.json --out evaluation_results
cat evaluation_results/metrics.md
```

Runtime ~10 min, cost ~$0.04 (heuristic, 1 LLM call max).
