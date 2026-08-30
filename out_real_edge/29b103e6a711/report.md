# Risk2Fix Report — https://github.com/request/request

**Technical Risk Score:** 67/100
**Verdict:** HOLD

| Area | Score | Severity | Evidence | Cost | Summary |
|------|-------|----------|----------|------|---------|
| Testing | 35 | critical | evidence/test.log:1 | 4h | Tests fail: > request@2.88.1 test
> npm run lint && npm run test-ci && npm run test-browser


> request@2.88.1 lint
> standard


'standard' is not recognized as an internal or external command,
operable program o |
| Dependencies | 85 | low | evidence/npm_audit.json:1 | 0h | No high CVEs |
| Security | 88 | low | evidence/pip_audit.json:1 | 0h | No high security findings |
| Architecture | 75 | low | evidence/madge.log:1 | 0h | No circular deps |
| Maintainability | 55 | medium | evidence/git_shortlog.log:1 | hiring | Bus factor 1 |


## Reproduction
```bash
git clone https://github.com/request/request repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json
```

> Every row links to `evidence/<file>:line`. See `evidence/` folder for raw logs.