# 03_REPRODUCIBILITY — 100% Legal & Reproducible (Ground Rules 01-10)

## Compliance Matrix (must pass all)

| Rule | Requirement | How CodeCat Satisfies |
|------|-------------|----------------------|
| 01 | Build with known tools | Python, Docker, npm, pip-audit — all pre-existing, disclosed in pyproject.toml |
| 02 | Clear pre-existing vs added | README states: audit tools (npm audit etc) existed before; orchestration, verification, fix loop, report gen added during hackathon |
| 03 | License/terms compliance | All tools MIT/Apache, LLM per terms, no scraping without permission |
| 04 | Sandbox consequential actions | **All** `clone, install, build, test, docker build` inside Docker sandbox (`tools/sandbox.py`), host not mutated. Patch applied only inside sandbox unless human confirms |
| 05 | Qualified human reviewer for high-stakes | **Human gate** before any patch is shown as "recommended": `typer.confirm("Apply patch to host?")` — report says `PROPOSED PATCH — requires reviewer approval`. Valuation decisions require human |
| 06 | Legal/ethical use | Public repos only, no private data, no scraping personal info |
| 07 | Allowed data to share | Public GitHub repos + synthetic fixtures, 10_repos.json lists only public URLs |
| 08 | No credentials | `.gitignore` out/, no tokens in trajectories, use `GITHUB_TOKEN` env if needed but not logged |
| 09 | Claims tied to evidence | Every table row → `evidence/<file>:line`, logs are raw tool output, Verifier drops claims without evidence |
| 10 | Enough access to reproduce | Reproduction guide + `reproduction.sh` per run + exact versions + Docker image tag |

## Reproduction Guide (for judges, clean env)

**Prerequisites:** Docker 29+, Python 3.11+, git

```bash
git clone https://github.com/Tamjid0/codecat.git
cd codecat
docker build -t codecat:1.0 .
# Single repo
python -m codecat audit https://github.com/psf/requests --out ./out/requests --verbose
cat out/requests/report.md
cat out/requests/evidence/test.log

# Full evaluation (10 repos, baseline vs advanced)
python -m codecat evaluate --dataset datasets/10_repos.json --out evaluation_results/
cat evaluation_results/metrics.md
# Expected: Spearman baseline ~0.45 → advanced ~0.82, factual accuracy 58% → 94%, fix verification 0% → 60%
```

**Versions locked:** see `pyproject.toml` (`langgraph==0.2.x`, `typer`, `pydantic`), `Dockerfile` (`python:3.11-slim`), `package-lock` hashes. Runtime per repo ~12min, full eval ~2h, cost ~$0.30 LLM per repo.

## Sandbox Details
- `tools/sandbox.py` wraps `docker run --rm -v <tmp>:/repo -w /repo --network none codecat-sandbox <cmd>` where possible
- Host `out/` is bind-mounted for evidence only
- Fresh container per verification to prove clean-env reproducibility

## Human Checkpoint
- After Fixer produces `patch.diff`, CLI prints diff + `before.log` excerpt and asks `Apply? [y/N]`. Trajectories log the prompt + response.
- Report header states: `This patch is PROPOSED and requires qualified reviewer sign-off before use in valuation/deployment.`

## Trajectories
- Every agent logs `trajectories/<repo_hash>/<agent>.json` with: `instructions → tool calls → tool responses → next step → retries`
- No secrets, no private data

## What to include in submission
- Code + docs + `datasets/10_repos.json` + `evaluation_results/` + `trajectories/` + `reproduction.sh` per sample
