# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Development uses [uv](https://docs.astral.sh/uv/) (Python 3.10+ supported; `uv.lock` is committed):

```bash
uv sync                                          # install runtime deps + dev group (pytest + heavy optional deps)
uv run pytest tests/test_etool.py -v             # run the test suite
uv run pytest tests/test_etool.py::test_image_manager -v   # run a single test
uv run etool --json version                      # run the CLI from the clone
```

CI (`.github/workflows/python-app.yml`) uses pip instead: `pip install -e ".[all,dev]"` then `pytest tests/test_etool.py -v --tb=short`, on a matrix of Python 3.10/3.12/3.14 (Linux) plus Windows/macOS. Publishing to PyPI happens automatically when a GitHub release is published.

Tests `os.chdir(tests/)` at import time and operate on fixture files committed in `tests/` (`pic1.webp`, `test.docx`, etc.); generated outputs also land there. Email/scheduler tests are intentionally skipped.

## Architecture

`src/` layout; the public package is `src/etool/`. All functionality is exposed as `Manager*` classes living in private subpackages grouped by domain:

- `_office/` — `ManagerPdf`, `ManagerDocx`, `ManagerExcel`, `ManagerImage`, `ManagerQrcode`, `ManagerIpynb`, `ManagerEmail`, `ManagerCheatsheet`
- `_network/` — `ManagerSpeed`, `ManagerWeb`
- `_ai/` — `ManagerLlm`
- `_other/` — `ManagerPassword`, `ManagerScheduler`, `ManagerInstall`, `ManagerStdlibUsage`
- `_md/` — `ManagerMd`
- `_core/errors.py` — the error/envelope model (see below)

**Defensive imports:** `etool/__init__.py` imports every manager inside `try/except ImportError`, appends successes to `__all__`, and records failures (queryable via `get_import_status()` / `is_available()`), so one missing optional dependency never breaks the whole package. A new manager must follow this same pattern.

**Heavy deps are extras:** the default install is lightweight (pure-Python + Pillow). PyMuPDF (`etool pdf to-images`) and OpenCV (`etool qrcode decode`) live in the `pdf-images` / `qr-decode` / `all` extras and are imported lazily inside the methods that need them, raising `EtoolError(DEPENDENCY_ERROR)` with an install hint when missing. Do not add heavy binary wheels (numpy, scipy, etc.) to the default `dependencies`.

**Result envelopes:** `_core/errors.py` defines the AI-friendly contract used everywhere: `ok(data)` → `{"ok": true, "data": ...}`, `err(EtoolError)` → `{"ok": false, "error": {code, message, details}}`, with `ErrorCode` as a stable `StrEnum` (`VALIDATION_ERROR`, `NOT_FOUND`, `IO_ERROR`, `DEPENDENCY_ERROR`, `RUNTIME_ERROR`).

**CLI:** `etool` entry point (also `python -m etool`) → `cli.py` → `_cli_main.py`, which is one large argparse tree mapping subcommands onto manager methods. A global `--json` flag makes stdout a single pretty-printed (2-space indent) envelope per invocation; without it, output is human-readable (errors go to stderr). Adding a feature means: manager method → argparse subcommand in `_cli_main.py` wrapping the result in `ok`/`err` → README examples.

**Version is hardcoded in three places** that must stay in sync: `pyproject.toml`, `get_version()` in `src/etool/__init__.py`, and the `test_version` assertion.

## Conventions

- `README.md` (English) and `README_CN.md` (Chinese) mirror each other and document every CLI subcommand with input/output examples (inside per-domain `<details>` blocks) — update both when changing the CLI. User-visible release notes go to `CHANGELOG.md`.
- 2.0 deliberately removed all platform-specific features (Windows COM/registry/context menu, screen/file sharing, GPU tests, Office-based PDF conversion). Everything must remain cross-platform (Windows/macOS/Linux).
