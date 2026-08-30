#!/bin/bash
set -e
git clone https://github.com/request/request repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json