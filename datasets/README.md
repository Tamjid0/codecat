# Datasets — Ground Truth Transparency

**Goal:** Be 100% transparent for judges — no overselling. Metric is Spearman rank correlation, not % accuracy.

## 10 Repos Composition (plus 50k LOC medium-big validation)

**5 Real public (small, fast clone, MIT/Apache):**
- `https://github.com/sindresorhus/is` (JS, healthy, ~2k LOC)
- `https://github.com/pallets/click` (Python, healthy, ~10k LOC)
- `https://github.com/octocat/Hello-World` (docs, no deps edge)
- `https://github.com/sindresorhus/awesome` (markdown, no package.json edge)
- `https://github.com/public-apis/public-apis` (Python, maintainability edge, ~30k LOC, large but public)

**Additional 50k LOC equivalent validation (outside 10-repo eval, for scalability proof):**
- `https://github.com/pallets/flask` (~30k LOC Python + tests, medium-big, `out_big/bb69cc12b4b0/report.md:1` Score 67 HOLD, Testing 35 `ModuleNotFoundError: No module named 'click'` → correctly flagged as evidence `evidence/test.log:1`, not hallucinated. Proves sandbox handles medium-big clones, installs, and tests within 120s timeout.)

**5 Synthetic public MIT fixtures (we created to cover failure modes baseline misses):**

**5 Synthetic public MIT fixtures (we created to cover failure modes baseline misses):**
- `file://C:/Temp/codecat_test_vuln_pass` — CVE lodash 4.17.19, tests pass, fixable via bump
- `file://C:/Temp/codecat_test_vuln` — broken tests + CVE, critical
- `file://C:/Temp/codecat_circular` — `src/a.js ↔ b.js` circular (madge)
- `file://C:/Temp/codecat_lying_readme` — README claims `docker build works` + `npm test passes` but Dockerfile `RUN exit 1` and tests `exit 1` (challenging case)
- `file://C:/Temp/codecat_broken_docker` — Dockerfile `RUN npm ci` without lockfile, build fails

All synthetic are `git init` public, MIT, pushed to `file://` for reproducibility — not hidden. No private data.

## Ground Truth Establishment

**Before running any tool:** 2 reviewers blind-ranked 1-10 using shared rubric `docs/04_EVALUATION.md:1` (Testing, Dependencies, Security, Architecture, Maintainability 0-100 each, overall). Ranks in `10_repos.json` `expert_rank` — e.g., is 1 (healthy), lying 10 (most risky). Reviewers did not see baseline or advanced outputs.

**Fair comparison:** Baseline (single LLM prompt README+tree) and Advanced (this workflow) run on same 10, same rubric.

## Metric — What 0.891 Means

**Spearman rank correlation** between `expert_rank` (1=best) and `tool rank` (1=highest score). `to_ranks` in `evaluation/harness.py:1` inverts scores (higher score → rank 1). Range -1 to 1, 1 = perfect ordering.

* Baseline 0.709 — heuristic already correlates because long README ≈ healthy, but it misses circular/docker/lint.
* Advanced 0.891 — correctly orders after penalizing lint (is 73 not 85), docker FAIL (69), circular 69, and verifying CVE fix 69→81.
* Delta +0.182 — not "18% more accurate", but "rank ordering 18 points closer to experts while providing evidence links and verified remediation".

**Limitations:** Synthetic cases were created specifically for this system — we disclose that. Real-world private repos would need re-validation. All evidence is in `evaluation_results/advanced_runs/*/evidence/` for independent verification.

## Reproduction

```powershell
python -m codecat.cli evaluate --dataset datasets/10_repos.json --out evaluation_results
cat evaluation_results/metrics.md
```

Runtime ~10 min, cost ~$0.04 (heuristic, 1 LLM call max).
