# [中文](README_CN.md) | English

Cross-platform Python utilities (**2.0**): same code on Windows, macOS, and Linux. The **`etool`** command exposes major features from the shell; use **`--json`** for a pretty-printed JSON envelope (2-space indent, valid JSON) suitable for AI agents and scripts (`ok` / `err`).

**Requires Python 3.12+.**

## Install

```bash
pip install -U etool
```

After install, the `etool` entry point is on your `PATH`. You can also run `python -m etool ...`. With uv from a clone: `uv run etool ...`.

---

## CLI: `--json` envelope

With **`--json`**, stdout is one JSON document per invocation (pretty-printed with 2-space indent):

- Success: `{"ok": true, "data": { ... }}`
- Failure: `{"ok": false, "error": {"code", "message", "details"}}`

Without `--json`, output is a human-readable form (often pretty-printed JSON for structured `data`).

Below, **Input** is the command; **Output** shows typical **`--json`** stdout (values such as paths, passwords, and timings are illustrative).

---

### Version

**Input**

```bash
etool --json version
```

**Output**

```json
{"ok": true, "data": {"version": "2.1.0"}}
```

---

### Password

**Random password**

```bash
etool --json password random --length 16
```

```json
{"ok": true, "data": {"password": "xYz9...16chars"}}
```

**Base conversion**

```bash
etool --json password convert-base --from-base 16 --to-base 2 A1F
```

```json
{"ok": true, "data": {"result": "101000011111"}}
```

---

### Speed (network / disk / memory)

**Network** (uses speedtest-cli; needs internet, can be slow)

```bash
etool --json speed network
```

```json
{"ok": true, "data": {"report": "\n network test result:\ndownload speed: ... Mbps\n..."}}
```

**Disk**

```bash
etool --json speed disk --file-size-mb 10
```

```json
{"ok": true, "data": {"report": "\n disk test result:\nread speed: ... MB/s\nwrite speed: ... MB/s\n"}}
```

**Memory** (stdlib buffer test)

```bash
etool --json speed memory --size-mb 32
```

```json
{"ok": true, "data": {"report": "\n memory test result:\nread speed: ... MB/s\nwrite speed: ... MB/s"}}
```

---

### PDF (`ManagerPdf`)

**Merge**

```bash
etool --json pdf merge --out merged.pdf part1.pdf part2.pdf
```

```json
{"ok": true, "data": {"merged": "merged.pdf", "log": "merged: part1.pdf\nmerged: part2.pdf\nmerged file saved as: merged.pdf"}}
```

**Split by page chunk size**

```bash
etool --json pdf split-pages --pages 3 document.pdf
```

```json
{"ok": true, "data": {"source": "document.pdf", "log": "generated: document_part_by_page1.pdf\n..."}}
```

**Split into N parts**

```bash
etool --json pdf split-num --parts 2 document.pdf
```

```json
{"ok": true, "data": {"source": "document.pdf", "log": "..."}}
```

**Encrypt / decrypt**

```bash
etool --json pdf encrypt --password secret doc.pdf --out doc_encrypted.pdf
etool --json pdf decrypt --password secret doc_encrypted.pdf --out doc_clear.pdf
```

```json
{"ok": true, "data": {"log": "encrypted file saved as: doc_encrypted.pdf"}}
```

**Insert another PDF after a page index**

```bash
etool --json pdf insert --pdf1 a.pdf --pdf2 b.pdf --after-page 0 --out out.pdf
```

```json
{"ok": true, "data": {"output": "out.pdf", "log": "inserted file saved as: out.pdf"}}
```

**Watermark**

```bash
etool --json pdf watermark --target folder_or_file.pdf --watermark wm.pdf --out-dir watermarked
```

```json
{"ok": true, "data": {"log": "..."}}
```

**PDF → PNG images**

```bash
etool --json pdf to-images --input doc.pdf --out-dir png_out --dpi 2
```

```json
{"ok": true, "data": {"log": "found 1 PDF file(s)\n..."}}
```

---

### Word (`ManagerDocx`)

**Replace text**

```bash
etool --json docx replace --path report.docx --old foo --new bar
```

```json
{"ok": true, "data": {"path": "report.docx"}}
```

**Swap page dimensions (landscape ↔ portrait style)**

```bash
etool --json docx swap-dimensions --input in.docx --output out.docx
```

```json
{"ok": true, "data": {"path": "out.docx"}}
```

**Extract embedded images**

```bash
etool --json docx extract-images --input in.docx --out-dir ./img_out
```

```json
{"ok": true, "data": {"path": "./img_out"}}
```

---

### Excel (`ManagerExcel`)

**Copy formatting from a template workbook**

```bash
etool --json excel copy-format --source template.xlsx --output out.xlsx
```

```json
{"ok": true, "data": {"path": "out.xlsx"}}
```

---

### Images (`ManagerImage`)

**Merge left–right / top–bottom**

```bash
etool --json image merge-lr left.png right.png --out lr.png
etool --json image merge-ud top.png bottom.png --out ud.png
```

```json
{"ok": true, "data": {"path": "lr.png"}}
```

**Pad to square / 3×3 grid crop / batch rename to WebP**

```bash
etool --json image fill-square photo.jpg --out square.jpg
etool --json image cut-grid photo.jpg
etool --json image rename-webp ./shots --remove-original
```

```json
{"ok": true, "data": {"paths": ["photo_cut00.jpg", "..."]}}
```

---

### QR code (`ManagerQrcode`)

**Generate**

```bash
etool --json qrcode generate --text "https://example.com" --out qr.png
```

```json
{"ok": true, "data": {"path": "qr.png"}}
```

**Decode (local OpenCV)**

```bash
etool --json qrcode decode qr.png
```

```json
{"ok": true, "data": {"text": "https://example.com"}}
```

---

### Jupyter (`ManagerIpynb`)

**Merge all `.ipynb` in a directory**

```bash
etool --json ipynb merge-dir ./notebooks/
```

```json
{"ok": true, "data": {"path": "./notebooks.ipynb"}}
```

**Notebook → Markdown file**

```bash
etool --json ipynb to-markdown analysis.ipynb --out-dir ./md_out
```

```json
{"ok": true, "data": {"path": "analysis.md"}}
```

---

### Markdown (`ManagerMd`)

```bash
etool --json md to-docx notes.md --out notes.docx
etool --json md to-html notes.md --out notes.html
etool --json md tables-to-xlsx tables.md --out tables.xlsx
```

```json
{"ok": true, "data": {"message": "已将Markdown文件转换为Word文档并保存至: notes.docx"}}
```

---

### Standard-library usage analysis

One subcommand: `stdlib analyze DIR`. By default the envelope puts the nested counts under `data.result` (JSON object). With `--json-string`, the same analysis is returned as a single formatted JSON **text** under `data.json` (useful when you want one string field instead of nested JSON).

```bash
etool --json stdlib analyze ./src
etool --json stdlib analyze ./src --json-string
```

```json
{"ok": true, "data": {"result": {"os": {"path.join": 12, "listdir": 3}}}}
```

```json
{"ok": true, "data": {"json": "{\n  \"os\": {\n    \"path.join\": 12\n  }\n}"}}
```

---

### Install requirements (`ManagerInstall`)

Uses `python -m pip install` internally.

```bash
etool --json install-reqs --file requirements.txt --failed-file failed.txt --retry 2
```

```json
{"ok": true, "data": {"success": true}}
```

On failure:

```json
{"ok": false, "error": {"code": "RUNTIME_ERROR", "message": "some packages failed to install", "details": {}}}
```

---

### Scheduler (`ManagerScheduler.parse_schedule_time` — debug printout)

```bash
etool --json scheduler parse 120
etool --json scheduler parse '"08:00"'
```

```json
{"ok": true, "data": {"log": "Execute every 120 seconds"}}
```

---

### Email (`ManagerEmail.send_email`)

Do not paste real passwords into shell history; prefer environment-specific secrets in automation.

```bash
etool --json email send \
  --sender you@example.com \
  --password "$SMTP_PASSWORD" \
  --recipient other@example.com \
  --message "Hello" \
  --subject "Test"
```

```json
{"ok": true, "data": {"result": "send success"}}
```

---

## Python API and AI envelopes

Library usage matches the managers above. For structured envelopes in code:

```python
from etool import ok, err, EtoolError, ErrorCode

payload = ok({"path": "/tmp/out.pdf"})
failure = err(EtoolError(ErrorCode.VALIDATION_ERROR, "bad input", {"field": "x"}))
```

---

## Removed in 2.0

- Windows COM / registry / context menu (`ManagerMenu`)
- Screen sharing and Flask file share (`ManagerShare`)
- GPU memory / CUDA speed test
- `ManagerPdf.pdfconverter` (Office → PDF via local Microsoft Office)

---

## Development

With [uv](https://docs.astral.sh/uv/): `uv sync` installs runtime deps plus the `dev` group (pytest). Commit `uv.lock` with the repo.

```bash
uv sync
uv run pytest tests/test_etool.py -v
```

With pip:

```bash
pip install -e ".[dev]"
pytest tests/test_etool.py -v
```
