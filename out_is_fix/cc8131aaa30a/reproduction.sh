#!/bin/bash
set -e
git clone https://github.com/sindresorhus/is repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json