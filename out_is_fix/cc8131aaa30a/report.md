# Risk2Fix Report — https://github.com/sindresorhus/is

**Technical Risk Score:** 73/100
**Verdict:** HOLD

| Area | Score | Severity | Evidence | Cost | Summary |
|------|-------|----------|----------|------|---------|
| Testing | 65 | medium | evidence/test.log:1 | 2h lint | Lint warnings (not unit fail): > @sindresorhus/is@8.1.0 test
> tsc --noEmit && tsc --project test/tsconfig.json --noEmit && xo && node --experimental-t |
| Dependencies | 85 | low | evidence/npm_audit.json:1 | 0h | No high CVEs |
| Security | 88 | low | evidence/pip_audit.json:1 | 0h | No high security findings |
| Architecture | 75 | low | evidence/madge.log:1 | 0h | No circular deps |
| Maintainability | 55 | medium | evidence/git_shortlog.log:1 | hiring | Bus factor 1 |


## Reproduction
```bash
git clone https://github.com/sindresorhus/is repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json
```

> Every row links to `evidence/<file>:line`. See `evidence/` folder for raw logs.