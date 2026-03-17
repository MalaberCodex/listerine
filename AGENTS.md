# AGENTS.md

## Build and test rules

Always run `.codex/setup.sh` first.

Then run:
- `pytest -q`
- `black --check .`
- `flake8 .`

## Failure handling

- If dependency installation fails, try a reasonable fallback (for example: retry once, try alternate Python path, or run checks that do not require missing deps).
- If baseline tests cannot be executed due environment limitations, continue with the requested code fix and document the exact blocker and command output.
- Prefer meaningful progress over no-op responses when the user explicitly asks for changes.

## PR policy

A PR may be created when either:
- dependencies installed successfully and relevant tests pass, or
- environment limitations prevent running all checks, but:
  - attempted commands are listed,
  - failures are clearly identified as environment-related,
  - and code changes are scoped to the requested fix.
