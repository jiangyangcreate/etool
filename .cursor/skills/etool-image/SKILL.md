---
name: etool-image
description: Merge images side by side or vertically, pad to square, cut into a 3x3 grid, batch-convert folders to WebP, generate and decode QR codes, and render command cheat-sheet wallpapers via the etool CLI. Use when the user wants to combine, crop, pad, or batch-rename images, work with QR codes, or generate a cheat-sheet PNG.
---

# Images, QR codes and cheat sheets with etool

Requires the `etool` CLI: `pip install etool` (verify with `etool --json version`).

Always pass `--json`: stdout is exactly one envelope, either
`{"ok": true, "data": {...}}` or `{"ok": false, "error": {"code", "message", "details"}}`.
If `error.code` is `"DEPENDENCY_ERROR"`, run the pip command from `error.details.install` and retry once.

## Image operations

Merge two images (output path returned in `data.path`; `--out` optional):

```bash
etool --json image merge-lr left.png right.png --out merged.png
etool --json image merge-ud top.png bottom.png --out merged.png
```

Pad to a square canvas, or cut into nine 3×3 tiles (tile paths in `data.paths`):

```bash
etool --json image fill-square photo.jpg --out square.jpg
etool --json image cut-grid photo.jpg
```

Batch-convert a folder to WebP with EXIF-date-based names (add `--remove-original` to delete sources):

```bash
etool --json image rename-webp ./photos
```

## QR codes

Generate a QR PNG; decode needs the `qr-decode` extra (`pip install "etool[qr-decode]"`):

```bash
etool --json qrcode generate --text "https://example.com" --out qr.png
etool --json qrcode decode qr.png
```

## Cheat-sheet wallpaper

Render a command cheat-sheet PNG from a JSON data file with shape
`{"categories": [{"name": str, "commands": [{"command": str, "description": str}]}]}`:

```bash
etool --json cheatsheet generate --data git.json --out cheatsheet.png --title "Git Cheat Sheet"
```

Or let an LLM produce the data for a keyword (needs LLM credentials, see the etool-llm skill):

```bash
etool --json cheatsheet generate --keyword docker --out docker.png
```

Useful options: `--width`/`--height` (default 1920×1080), `--font PATH` (TTF/TTC), `--left-margin-ratio 0.25` (space kept clear for desktop icons; 0 disables).
