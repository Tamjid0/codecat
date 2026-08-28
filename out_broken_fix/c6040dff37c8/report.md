# Risk2Fix Report — file://C:/Temp/codecat_broken_docker

**Technical Risk Score:** 69/100
**Verdict:** HOLD

| Area | Score | Severity | Evidence | Cost | Summary |
|------|-------|----------|----------|------|---------|
| Testing | 90 | low | evidence/test.log:1 | 0h | Tests pass: > broken-docker@1.0.0 test
> node -e "process.exit(0)" |
| Dependencies | 85 | low | evidence/npm_audit.json:1 | 0h | No high CVEs |
| Security | 88 | low | evidence/pip_audit.json:1 | 0h | No high security findings |
| Architecture | 30 | critical | evidence/docker.log:1 | 1d | Docker build fails — deployment blocked |
| Maintainability | 55 | medium | evidence/git_shortlog.log:1 | hiring | Bus factor 1 |


## Reproduction
```bash
git clone file://C:/Temp/codecat_broken_docker repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json
```

> Every row links to `evidence/<file>:line`. See `evidence/` folder for raw logs.