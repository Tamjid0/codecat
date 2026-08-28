# Risk2Fix Report — file://C:/Temp/codecat_test_vuln

**Technical Risk Score:** 55/100
**Verdict:** HOLD

| Area | Score | Severity | Evidence | Cost | Summary |
|------|-------|----------|----------|------|---------|
| Testing | 35 | critical | evidence/test.log:1 | 4h | Tests fail: > test-vuln@1.0.0 test
> node -e "process.exit(1)" |
| Dependencies | 60 | medium | evidence/npm_audit.json:1 | 4h | 1 CVE(s) with fix available |
| Security | 65 | medium | evidence/pip_audit.json:1 | 4h | Security audit: 1 high |
| Architecture | 75 | low | evidence/madge.log:1 | 0h | No circular deps |
| Maintainability | 55 | medium | evidence/git_shortlog.log:1 | hiring | Bus factor 1 |
| README claims | 40 | medium | test.log:1:1 | 2h docs | ReADME claim FAIL: "npm test passes" |


## Reproduction
```bash
git clone file://C:/Temp/codecat_test_vuln repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json
```

> Every row links to `evidence/<file>:line`. See `evidence/` folder for raw logs.