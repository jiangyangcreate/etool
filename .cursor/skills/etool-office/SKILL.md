---
name: etool-office
description: Word (.docx) text replace and image extraction, Excel format copying, Markdown to docx/HTML/Excel conversion, and Jupyter notebook merging or Markdown export via the etool CLI. Use when the user works with .docx, .xlsx, .md, or .ipynb files — replacing text, extracting images, converting Markdown, or merging notebooks.
---

# Office documents with etool

Requires the `etool` CLI: `pip install etool` (verify with `etool --json version`).

Always pass `--json`: stdout is exactly one envelope, either
`{"ok": true, "data": {...}}` or `{"ok": false, "error": {"code", "message", "details"}}`.
If `error.code` is `"DEPENDENCY_ERROR"`, run the pip command from `error.details.install` and retry once.

## Word (.docx)

Replace text everywhere in a document (modifies a copy; the result path is in `data.path`):

```bash
etool --json docx replace --path report.docx --old "DRAFT" --new "FINAL"
```

Swap page width/height (portrait ↔ landscape):

```bash
etool --json docx swap-dimensions --input report.docx --output rotated.docx
```

Extract all embedded images:

```bash
etool --json docx extract-images --input report.docx --out-dir extracted_images
```

## Excel (.xlsx)

Copy sheet formatting (column widths, styles) from a template workbook into a new file:

```bash
etool --json excel copy-format --source template.xlsx --output styled.xlsx
```

## Markdown

Convert Markdown to Word / HTML, or extract all Markdown tables into an Excel workbook (one sheet per table):

```bash
etool --json md to-docx notes.md --out notes.docx
etool --json md to-html notes.md --out notes.html
etool --json md tables-to-xlsx notes.md --out tables.xlsx
```

## Jupyter (.ipynb)

Merge every notebook in a directory into one, or convert a notebook to Markdown:

```bash
etool --json ipynb merge-dir ./notebooks
etool --json ipynb to-markdown analysis.ipynb --out-dir ./out
```
