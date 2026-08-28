#!/bin/bash
set -e
git clone file://C:/Temp/codecat_circular repo
cd repo && npm ci || pip install -e .
npm test || pytest -q
npm audit --json; pip-audit --format=json