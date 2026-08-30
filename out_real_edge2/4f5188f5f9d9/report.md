# Risk2Fix Report — https://github.com/moment/moment

**Technical Risk Score:** 69/100
**Verdict:** HOLD

| Area | Score | Severity | Evidence | Cost | Summary |
|------|-------|----------|----------|------|---------|
| Testing | 90 | low | evidence/test.log:1 | 0h | Tests pass: tests failed |
| Dependencies | 85 | low | evidence/npm_audit.json:1 | 0h | No high CVEs |
| Security | 88 | low | evidence/pip_audit.json:1 | 0h | No high security findings |
| Architecture | 30 | critical | evidence/madge.log:1 | 1w | Circular dependency detected — tight coupling |
| Maintainability | 55 | medium | evidence/git_shortlog.log:1 | hiring | Bus factor 1 |


## Reproduction
```bash
git clone https://github.com/moment/moment repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json
```

> Every row links to `evidence/<file>:line`. See `evidence/` folder for raw logs.