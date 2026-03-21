"""Command-line entrypoint (`etool` / `python -m etool`)."""

from __future__ import annotations

from ._cli_main import main

if __name__ == "__main__":
    raise SystemExit(main())
