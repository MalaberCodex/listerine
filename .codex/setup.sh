#!/usr/bin/env bash
set -euo pipefail

# Codex bootstrap script: install project + dev dependencies deterministically.
./scripts/setup_env.sh

# Optional baseline signal for environment health (do not fail bootstrap).
python -m pytest -q || true
