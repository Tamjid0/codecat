# 05_DELIVERABLES — Submission Checklist (4 items, PDF pages 07-08)

## 01 Complete solution code + improvement changelog
- [ ] Full code in `src/codecat/` with agent instructions (`docs/06_AGENT_INSTRUCTIONS.md` + inline prompts)
- [ ] README introduces user + bottleneck + why valuable
- [ ] `docs/07_IMPROVEMENT_CHANGELOG.md` with columns Stage | What tried & why | Evidence | Decision/Learning (Baseline, Iter1 skill, Iter2 verification, Iter3 orchestration, Final)
- [ ] Main failure mode + Hot Take (5pts) at end of changelog

## 02 Reproduction guide
- [ ] Clean-env steps, exact commands for solution, baseline, evaluation (see 03_REPRODUCIBILITY.md)
- [ ] Data required: `datasets/10_repos.json` (public URLs only)
- [ ] Expected output: `report.md` + `evidence/` + `evaluation_results/metrics.md` with values
- [ ] Versions, runtime (~12m/repo, ~2h full eval), cost (~$0.30/repo)

## 03 Solution video ≤5 min (script locked)
1. 0:00-0:45 Problem + baseline demo (baseline scores flask as 90 but misses CVE)
2. 0:45-3:00 One realistic end-to-end run (lying README repo → clone → FAIL → fix → PASS, show report)
3. 3:00-4:00 Final comparison table (Spearman + accuracy delta)
4. 4:00-4:45 Changelog: biggest win (verification) + one removed experiment (tried full UI, removed to save time)
5. 4:45-5:00 Human gate + reproducibility note

## 04 Agent trajectories
- [ ] `trajectories/<repo>/build_agent.json`, `depsec_agent.json`, `static_claim.json`, `aggregator.json`, `fixer.json`, `verifier.json` — each shows instructions → tool responses → feedback → retries/human checkpoint
- [ ] At least one trajectory with retry (fix fails first, succeeds second)

## Extra legal checks
- [ ] No credentials, no private data, sandbox for consequential actions, human reviewer noted
- [ ] `pyproject.toml` licenses respected, `Dockerfile` reproducible

## Submission package
- [ ] GitHub repo `Tamjid0/codecat` public, tagged `v1.0`
- [ ] HackerEarth submission links to repo + video (unlisted YouTube) + `out/` sample + `evaluation_results/`
