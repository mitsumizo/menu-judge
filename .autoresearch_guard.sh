#!/usr/bin/env bash
# Autoresearch guard: ensure nothing broke (app imports + no test regression).
set -e
cd "$(dirname "$0")"
venv/bin/python -c "from app import create_app; create_app()" >/dev/null 2>&1
PASSED=$(venv/bin/python -m pytest tests/ --tb=no -q 2>&1 | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' | head -1)
PASSED=${PASSED:-0}
if [ "$PASSED" -lt 53 ]; then
  echo "GUARD FAIL: passed=$PASSED (baseline=53)"
  exit 1
fi
echo "GUARD OK: passed=$PASSED"
