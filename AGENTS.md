# AGENTS.md

## Build and test rules

Always run `.codex/setup.sh` first.

Then run:
- `pytest -q`
- `black --check .`
- `flake8 .`

## Stop conditions

- If dependency installation fails, stop.
- If baseline tests cannot be executed, stop.
- Do not modify code in an attempt to "fix CI" until the baseline environment is working.
- Do not commit changes.
- Do not create or update a PR.

## PR policy

A PR may only be created if:
- dependencies installed successfully,
- the requested checks were run,
- and the relevant tests pass, or pre-existing failures are clearly documented and unchanged.
