---
name: etool-pdf
description: Merge, split, encrypt, decrypt, insert, watermark PDF files and rasterize PDF pages to PNG images via the etool CLI. Use when the user wants to manipulate PDF files — merging, splitting, password-protecting, watermarking, or converting PDF pages to images.
---

# PDF operations with etool

Requires the `etool` CLI: `pip install etool` (verify with `etool --json version`).

Always pass `--json`: stdout is exactly one envelope, either
`{"ok": true, "data": {...}}` or `{"ok": false, "error": {"code", "message", "details"}}`.
If `error.code` is `"DEPENDENCY_ERROR"`, run the pip command from `error.details.install` and retry once.

## Commands

Merge multiple PDFs into one:

```bash
etool --json pdf merge a.pdf b.pdf c.pdf --out merged.pdf
```

Split into chunks of N pages each (outputs land next to the source):

```bash
etool --json pdf split-pages input.pdf --pages 5
```

Split into a fixed number of parts:

```bash
etool --json pdf split-num input.pdf --parts 3
```

Encrypt / decrypt (use `--old-password` when re-encrypting an already-encrypted file):

```bash
etool --json pdf encrypt input.pdf --password s3cret --out locked.pdf
etool --json pdf decrypt locked.pdf --password s3cret --out unlocked.pdf
```

Insert one PDF after a 0-based page index of another:

```bash
etool --json pdf insert --pdf1 base.pdf --pdf2 extra.pdf --after-page 0 --out combined.pdf
```

Watermark every page (`--target` accepts a single PDF or a directory of PDFs; the watermark itself must be a PDF):

```bash
etool --json pdf watermark --target input.pdf --watermark stamp.pdf --out-dir watermarks
```

Rasterize pages to PNG files — needs the `pdf-images` extra (`pip install "etool[pdf-images]"`); `--input` accepts a file or a directory:

```bash
etool --json pdf to-images --input input.pdf --out-dir pdf_images --dpi 2
```
