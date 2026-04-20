#!/usr/bin/env bash
# Autoresearch verify: count test failures + errors. Lower = better.
set -e
cd "$(dirname "$0")"
OUT=$(venv/bin/python -m pytest tests/ --tb=no -q 2>&1 | tail -1)
FAILED=$(echo "$OUT" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | head -1)
ERRORS=$(echo "$OUT" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+' | head -1)
FAILED=${FAILED:-0}
ERRORS=${ERRORS:-0}
echo $((FAILED + ERRORS))
