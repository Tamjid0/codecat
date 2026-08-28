# Risk2Fix Report — file://C:/Temp/codecat_lying_readme

**Technical Risk Score:** 63/100
**Verdict:** HOLD

| Area | Score | Severity | Evidence | Cost | Summary |
|------|-------|----------|----------|------|---------|
| Testing | 35 | critical | evidence/test.log:1 | 4h | Tests fail: > lying@1.0.0 test
> node -e "process.exit(1)" |
| Dependencies | 85 | low | evidence/npm_audit.json:1 | 0h | No high CVEs |
| Security | 88 | low | evidence/pip_audit.json:1 | 0h | No high security findings |
| Architecture | 75 | low | evidence/madge.log:1 | 0h | No circular deps |
| Maintainability | 55 | medium | evidence/git_shortlog.log:1 | hiring | Bus factor 1 |
| README claims | 40 | medium | docker.log:1:1 | 2h docs | ReADME claim FAIL: "docker build works" |


## Reproduction
```bash
git clone file://C:/Temp/codecat_lying_readme repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json
```

> Every row links to `evidence/<file>:line`. See `evidence/` folder for raw logs.