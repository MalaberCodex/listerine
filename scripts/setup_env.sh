#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${PYTHON_BIN:-}" ]]; then
  PY="${PYTHON_BIN}"
elif python3.14 --version >/dev/null 2>&1; then
  PY="python3.14"
elif [[ -x /root/.pyenv/versions/3.14.0/bin/python ]]; then
  PY="/root/.pyenv/versions/3.14.0/bin/python"
else
  PY="python"
fi

"${PY}" --version
"${PY}" -m pip install --upgrade pip

REQS=$("${PY}" - <<'PY'
import tomllib
from pathlib import Path
p=Path('pyproject.toml')
data=tomllib.loads(p.read_text())
reqs=[]
reqs.extend(data['project'].get('dependencies', []))
reqs.extend(data['project'].get('optional-dependencies', {}).get('dev', []))
print(' '.join(reqs))
PY
)

# Install direct runtime+dev dependencies from pyproject (no editable build backend needed).
"${PY}" -m pip install ${REQS}
