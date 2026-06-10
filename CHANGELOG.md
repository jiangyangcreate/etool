# Changelog

Notable changes to etool. Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [2.2.0] — Unreleased

### Added

- `ManagerLlm` (`etool llm chat|summarize|outline`): any OpenAI-compatible endpoint via stdlib HTTP, automatic `<think>` stripping.
- `ManagerWeb` (`etool web fetch-text|rss|mask-ip`): readable-text page fetching, RSS 2.0 / Atom parsing, IP masking.
- `ManagerCheatsheet` (`etool cheatsheet generate`): render command cheat-sheet wallpaper PNGs from JSON data or an LLM keyword.
- Optional extras for heavy binary dependencies: `etool[pdf-images]` (PyMuPDF), `etool[qr-decode]` (OpenCV), `etool[all]`.
- CLI emits a `DEPENDENCY_ERROR` envelope with an install hint when an optional dependency is missing.

### Changed

- **Default install is ~10x lighter**: removed `numpy` and `scikit-image` entirely (image stitching is now pure Pillow); `pymupdf` and `opencv-python-headless` moved to extras.
- Minimum Python lowered from 3.12 to **3.10**; CI now tests 3.10 / 3.12 / 3.14 on Linux plus Windows and macOS.
- `ManagerMd` user-facing messages are now in English.
- Richer PyPI metadata: keywords, classifiers, SPDX license expression, project URLs.

## [2.1.0] — 2026-03-21

- English argparse help texts; `stdlib analyze-json` merged into `stdlib analyze --json-string`.

## [2.0.0] — 2026-03-21

- New AI-friendly result envelope model (`ok` / `err`, stable `ErrorCode`s) and the `--json` CLI contract.
- `src/` layout, defensive manager imports, `etool` / `python -m etool` entry points.
- **Removed** (deliberately, to keep etool fully cross-platform):
  - Windows COM / registry / context-menu integration (`ManagerMenu`)
  - Screen sharing and Flask file sharing (`ManagerShare`)
  - GPU memory / CUDA speed tests
  - `ManagerPdf.pdfconverter` (Office → PDF via local Microsoft Office)

## [1.4.x] and earlier

- Original toolbox releases (PDF / Word / Excel / image / QR code / notebook / email / scheduler utilities, Windows-era features).
