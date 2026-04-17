#!/usr/bin/env bash
# Autoresearch guard: ensure app still imports cleanly.
set -e
cd "$(dirname "$0")"
venv/bin/python -c "from app import create_app; create_app()" >/dev/null 2>&1
echo "GUARD OK: app imports cleanly"
