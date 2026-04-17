#!/usr/bin/env bash
# Autoresearch verify: count security findings. Lower = better.
set -e
cd "$(dirname "$0")"
RUFF_COUNT=$(venv/bin/ruff check app/ --select "S,B,BLE,TRY004,TRY400,TRY301,PLE" --output-format json 2>/dev/null | venv/bin/python -c "import sys,json; print(len(json.load(sys.stdin)))")
PIP_AUDIT_COUNT=$(venv/bin/pip-audit -r requirements.txt --format json 2>/dev/null | venv/bin/python -c "import sys,json; d=json.load(sys.stdin); print(sum(len(x.get('vulns',[])) for x in d.get('dependencies',[])))")
echo $((RUFF_COUNT + PIP_AUDIT_COUNT))
