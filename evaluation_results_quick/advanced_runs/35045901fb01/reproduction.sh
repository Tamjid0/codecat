#!/bin/bash
set -e
git clone https://github.com/octocat/Hello-World repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json