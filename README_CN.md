# [English](README.md) | 中文

跨平台 Python 工具集（**2.0**）。**`etool` 命令行**覆盖主要能力；加 **`--json`** 时 stdout 为缩进排版后的 JSON（`ok` / `err`），仍为合法 JSON，便于阅读与程序解析。

**需要 Python 3.12+。**

## 安装

```bash
pip install -U etool
```

安装后可直接使用 `etool`，也可用 `python -m etool ...`。在克隆目录下用 uv：`uv run etool ...`。

---

## 命令行：`--json` 约定

使用 **`--json`** 时，每次命令在 stdout 输出**一份**缩进后的 JSON（多行，2 空格缩进）：

- 成功：`{"ok": true, "data": { ... }}`
- 失败：`{"ok": false, "error": {"code", "message", "details"}}`

不加 `--json` 时，为便于人类阅读，多为结构化内容的友好输出（常为缩进 JSON）。

下文 **输入** 为示例命令；**输出** 为典型 **`--json`** 的 stdout（路径、密码、速度等数值仅为示例）。

---

### 版本

**输入**

```bash
etool --json version
```

**输出**

```json
{"ok": true, "data": {"version": "2.0.0"}}
```

---

### 密码

**随机密码**

```bash
etool --json password random --length 16
```

```json
{"ok": true, "data": {"password": "xYz9...共16位"}}
```

**任意进制转换**

```bash
etool --json password convert-base --from-base 16 --to-base 2 A1F
```

```json
{"ok": true, "data": {"result": "101000011111"}}
```

---

### 测速（网络 / 磁盘 / 内存）

**网络**（依赖 speedtest-cli，需外网，可能较慢）

```bash
etool --json speed network
```

```json
{"ok": true, "data": {"report": "\n network test result:\ndownload speed: ... Mbps\n..."}}
```

**磁盘**

```bash
etool --json speed disk --file-size-mb 10
```

```json
{"ok": true, "data": {"report": "\n disk test result:\nread speed: ... MB/s\nwrite speed: ... MB/s\n"}}
```

**内存**（标准库缓冲粗略测速）

```bash
etool --json speed memory --size-mb 32
```

```json
{"ok": true, "data": {"report": "\n memory test result:\nread speed: ... MB/s\nwrite speed: ... MB/s"}}
```

---

### PDF（`ManagerPdf`）

**合并**

```bash
etool --json pdf merge --out merged.pdf a.pdf b.pdf
```

```json
{"ok": true, "data": {"merged": "merged.pdf", "log": "merged: a.pdf\nmerged: b.pdf\nmerged file saved as: merged.pdf"}}
```

**按每份页数拆分**

```bash
etool --json pdf split-pages --pages 3 document.pdf
```

```json
{"ok": true, "data": {"source": "document.pdf", "log": "generated: document_part_by_page1.pdf\n..."}}
```

**按份数拆分**

```bash
etool --json pdf split-num --parts 2 document.pdf
```

```json
{"ok": true, "data": {"source": "document.pdf", "log": "..."}}
```

**加密 / 解密**

```bash
etool --json pdf encrypt --password 密钥 doc.pdf --out doc_encrypted.pdf
etool --json pdf decrypt --password 密钥 doc_encrypted.pdf --out doc_clear.pdf
```

```json
{"ok": true, "data": {"log": "encrypted file saved as: doc_encrypted.pdf"}}
```

**在指定页后插入另一 PDF**

```bash
etool --json pdf insert --pdf1 a.pdf --pdf2 b.pdf --after-page 0 --out out.pdf
```

```json
{"ok": true, "data": {"output": "out.pdf", "log": "inserted file saved as: out.pdf"}}
```

**水印**

```bash
etool --json pdf watermark --target 某文件或目录 --watermark wm.pdf --out-dir watermarked
```

```json
{"ok": true, "data": {"log": "..."}}
```

**PDF 转 PNG**

```bash
etool --json pdf to-images --input doc.pdf --out-dir png_out --dpi 2
```

```json
{"ok": true, "data": {"log": "found 1 PDF file(s)\n..."}}
```

---

### Word（`ManagerDocx`）

**替换文字**

```bash
etool --json docx replace --path report.docx --old foo --new bar
```

```json
{"ok": true, "data": {"path": "report.docx"}}
```

**交换页面宽高**

```bash
etool --json docx swap-dimensions --input in.docx --output out.docx
```

```json
{"ok": true, "data": {"path": "out.docx"}}
```

**导出内嵌图片**

```bash
etool --json docx extract-images --input in.docx --out-dir ./img_out
```

```json
{"ok": true, "data": {"path": "./img_out"}}
```

---

### Excel（`ManagerExcel`）

**按模板复制样式到新文件**

```bash
etool --json excel copy-format --source template.xlsx --output out.xlsx
```

```json
{"ok": true, "data": {"path": "out.xlsx"}}
```

---

### 图片（`ManagerImage`）

**左右 / 上下拼接**

```bash
etool --json image merge-lr left.png right.png --out lr.png
etool --json image merge-ud top.png bottom.png --out ud.png
```

```json
{"ok": true, "data": {"path": "lr.png"}}
```

**填成正方形 / 九宫格裁剪 / 批量转 webp 重命名**

```bash
etool --json image fill-square photo.jpg --out square.jpg
etool --json image cut-grid photo.jpg
etool --json image rename-webp ./shots --remove-original
```

```json
{"ok": true, "data": {"paths": ["photo_cut00.jpg", "..."]}}
```

---

### 二维码（`ManagerQrcode`）

**生成**

```bash
etool --json qrcode generate --text "https://example.com" --out qr.png
```

```json
{"ok": true, "data": {"path": "qr.png"}}
```

**识别（本机 OpenCV）**

```bash
etool --json qrcode decode qr.png
```

```json
{"ok": true, "data": {"text": "https://example.com"}}
```

---

### Jupyter（`ManagerIpynb`）

**合并目录下所有 ipynb**

```bash
etool --json ipynb merge-dir ./notebooks/
```

```json
{"ok": true, "data": {"path": "./notebooks.ipynb"}}
```

**ipynb → Markdown**

```bash
etool --json ipynb to-markdown analysis.ipynb --out-dir ./md_out
```

```json
{"ok": true, "data": {"path": "analysis.md"}}
```

---

### Markdown（`ManagerMd`）

```bash
etool --json md to-docx notes.md --out notes.docx
etool --json md to-html notes.md --out notes.html
etool --json md tables-to-xlsx tables.md --out tables.xlsx
```

```json
{"ok": true, "data": {"message": "已将Markdown文件转换为Word文档并保存至: notes.docx"}}
```

---

### 标准库调用分析

```bash
etool --json stdlib analyze ./src
etool --json stdlib analyze-json ./src
```

```json
{"ok": true, "data": {"result": {"os": {"path.join": 12, "listdir": 3}}}}
```

```json
{"ok": true, "data": {"json": "{\n  \"os\": {\n    \"path.join\": 12\n  }\n}"}}
```

---

### 按 requirements 安装（`ManagerInstall`）

内部使用 `python -m pip install`。

```bash
etool --json install-reqs --file requirements.txt --failed-file failed.txt --retry 2
```

```json
{"ok": true, "data": {"success": true}}
```

失败时示例：

```json
{"ok": false, "error": {"code": "RUNTIME_ERROR", "message": "some packages failed to install", "details": {}}}
```

---

### 定时任务解析调试（`ManagerScheduler.parse_schedule_time`）

```bash
etool --json scheduler parse 120
etool --json scheduler parse '"08:00"'
```

```json
{"ok": true, "data": {"log": "Execute every 120 seconds"}}
```

---

### 发邮件（`ManagerEmail.send_email`）

勿在命令行历史中暴露真实密码；自动化请用环境变量等注入。

```bash
etool --json email send \
  --sender you@example.com \
  --password "$SMTP_PASSWORD" \
  --recipient other@example.com \
  --message "你好" \
  --subject "测试"
```

```json
{"ok": true, "data": {"result": "send success"}}
```

---

## Python API 与 AI 结构体

```python
from etool import ok, err, EtoolError, ErrorCode

payload = ok({"path": "/tmp/out.pdf"})
failure = err(EtoolError(ErrorCode.VALIDATION_ERROR, "参数错误", {"field": "x"}))
```

---

## 2.0 已删除的能力

- Windows 注册表 / 右键菜单（`ManagerMenu`）
- 屏幕分享与文件分享（`ManagerShare`）
- GPU 相关测速
- `ManagerPdf.pdfconverter`（依赖本机 Office 的批量转 PDF）

---

## 开发

推荐使用 [uv](https://docs.astral.sh/uv/)：`uv sync` 会安装运行依赖与 `dev` 组（含 pytest）。请将 `uv.lock` 一并纳入版本控制。

```bash
uv sync
uv run pytest tests/test_etool.py -v
```

使用 pip：

```bash
pip install -e ".[dev]"
pytest tests/test_etool.py -v
```
