<div align="center">

# 🧰 etool

**一次安装,几十个日常自动化命令。为人类与 AI Agent 共同设计。**

[![PyPI](https://img.shields.io/pypi/v/etool)](https://pypi.org/project/etool/)
[![Python](https://img.shields.io/pypi/pyversions/etool)](https://pypi.org/project/etool/)
[![Downloads](https://img.shields.io/pypi/dm/etool)](https://pypi.org/project/etool/)
[![CI](https://github.com/jiangyangcreate/etool/actions/workflows/python-app.yml/badge.svg)](https://github.com/jiangyangcreate/etool/actions/workflows/python-app.yml)
[![License](https://img.shields.io/pypi/l/etool)](https://github.com/jiangyangcreate/etool/blob/main/LICENSE)

[English](https://github.com/jiangyangcreate/etool/blob/main/README.md) | 中文

</div>

`etool` 把日常办公与开发中的琐事变成一行命令(或一次 Python 调用):合并 / 拆分 / 加密 PDF、从 Word 提取图片、Markdown 转 Word / HTML / Excel、照片批量转 WebP、生成与识别二维码、合并 Jupyter Notebook、网络 / 磁盘测速、调用任意 OpenAI 兼容大模型、生成命令速查壁纸……

任何命令加上 `--json`,stdout 都只输出**一份机器可读的 JSON 结构**——这让 `etool` 可以直接作为 AI Agent、脚本与 CI 流水线的工具层。

## 为什么选 etool?

- 🧩 **多合一** —— PDF、Word、Excel、图片、二维码、Markdown、Jupyter、网页、大模型、网络工具,全部收纳在一个 `etool` 命令下;每个功能同时提供 Python API。
- 🤖 **AI Agent 友好** —— 加 `--json` 后,每条命令输出一份结构化结果:`{"ok": true, "data": ...}` 或 `{"ok": false, "error": {code, message, details}}`,错误码稳定、机器可读,适合函数调用与自动化流程。
- 🪶 **默认轻量** —— 默认安装仅约 15 MB;重型二进制依赖(PyMuPDF、OpenCV)按需选装:`etool[all]`。
- 🖥️ **跨平台** —— 同一套代码运行于 Windows / macOS / Linux,三平台 CI 全量测试。支持 Python 3.10+。

## 安装

```bash
pip install -U etool          # 轻量核心(约 15 MB),覆盖绝大部分功能
pip install -U "etool[all]"   # 额外启用 PDF 转图片与二维码识别
```

国内网络可使用镜像加速:

```bash
pip install -i https://mirrors.aliyun.com/pypi/simple/ -U etool
```

| 可选项 | 启用的功能 | 额外安装 |
|---|---|---|
| `etool[pdf-images]` | `etool pdf to-images`(PDF → PNG) | PyMuPDF |
| `etool[qr-decode]` | `etool qrcode decode`(本地二维码识别) | OpenCV(headless) |
| `etool[all]` | 以上全部 | 两者 |

也可以用 [uv](https://docs.astral.sh/uv/) 免安装直接运行,或用 pipx 安装为独立命令行工具:

```bash
uvx etool qrcode generate --text "https://example.com" --out qr.png
pipx install etool
```

安装后 `etool` 命令即可直接使用,也可用 `python -m etool ...`。

## 60 秒上手

```bash
# 合并两个 PDF
etool pdf merge --out merged.pdf part1.pdf part2.pdf

# 把 Markdown 笔记转成 Word 文档
etool md to-docx notes.md --out notes.docx

# 批量把照片无损转为 WebP
etool image rename-webp ./photos

# 生成二维码
etool qrcode generate --text "https://example.com" --out qr.png

# 抓取网页为干净的正文文本
etool web fetch-text https://example.com

# 调用任意 OpenAI 兼容模型(纯标准库 HTTP,无需 SDK)
etool llm chat "天空为什么是蓝色的?" --system "用一句话回答。"
```

脚本或 Agent 需要结构化输出?加 `--json`:

```bash
$ etool --json web mask-ip 8.8.4.4
{
  "ok": true,
  "data": {
    "masked": "8.8.x.4",
    "is_public": true
  }
}
```

`etool` 还能为任意工具生成命令速查壁纸——下图就是用 `etool cheatsheet generate` 生成的:

![etool 生成的 Git 速查壁纸](https://raw.githubusercontent.com/jiangyangcreate/etool/main/docs/cheatsheet-git.png)

## 功能总览

| 领域 | 命令 | 能力 |
|---|---|---|
| PDF | `etool pdf` | 合并、拆分、加密 / 解密、水印、插入、PDF → PNG |
| Word | `etool docx` | 替换文字、横竖版互换、导出内嵌图片 |
| Excel | `etool excel` | 按模板复制工作簿格式 |
| 图片 | `etool image` | 左右 / 上下拼接、填充为正方形、九宫格裁剪、批量转 WebP |
| 二维码 | `etool qrcode` | 生成、本地识别 |
| Markdown | `etool md` | 转 Word、转 HTML、表格转 Excel |
| Jupyter | `etool ipynb` | 合并 Notebook、Notebook → Markdown |
| 网页 | `etool web` | 网页 → 正文文本、RSS / Atom 解析、IP 脱敏 |
| 大模型 | `etool llm` | 对话、摘要、大纲(任意 OpenAI 兼容接口) |
| 速查壁纸 | `etool cheatsheet` | 生成命令速查表 PNG 壁纸 |
| 测速 | `etool speed` | 网络 / 磁盘 / 内存测速 |
| 密码 | `etool password` | 随机密码、任意进制转换 |
| 其他 | `etool stdlib` / `install-reqs` / `scheduler` / `email` | 标准库调用分析、批量 pip 安装、定时表达式解析、SMTP 发邮件 |

## 命令参考

使用 **`--json`** 时,每次命令在 stdout 输出**一份**缩进排版的 JSON(2 空格缩进,合法 JSON):

- 成功:`{"ok": true, "data": { ... }}`
- 失败:`{"ok": false, "error": {"code", "message", "details"}}`

不加 `--json` 时输出对人类友好(错误进 stderr)。下文 **输入** 为示例命令;**输出** 为典型 **`--json`** 的 stdout(路径、密码、速度等数值仅为示例)。

<details>
<summary><b>版本</b> —— <code>etool version</code></summary>

**输入**

```bash
etool --json version
```

**输出**

```json
{"ok": true, "data": {"version": "2.2.0"}}
```

</details>

<details>
<summary><b>PDF</b> —— 合并 · 拆分 · 加密 · 水印 · 转图片 —— <code>etool pdf</code></summary>

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

**PDF 转 PNG**(需要 `etool[pdf-images]`)

```bash
etool --json pdf to-images --input doc.pdf --out-dir png_out --dpi 2
```

```json
{"ok": true, "data": {"log": "found 1 PDF file(s)\n..."}}
```

</details>

<details>
<summary><b>Word</b> —— 替换文字 · 横竖版互换 · 导出图片 —— <code>etool docx</code></summary>

**替换文字**

```bash
etool --json docx replace --path report.docx --old foo --new bar
```

```json
{"ok": true, "data": {"path": "report.docx"}}
```

**交换页面宽高(横竖版互换)**

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

</details>

<details>
<summary><b>Excel</b> —— 按模板复制样式 —— <code>etool excel</code></summary>

**按模板复制样式到新文件**

```bash
etool --json excel copy-format --source template.xlsx --output out.xlsx
```

```json
{"ok": true, "data": {"path": "out.xlsx"}}
```

</details>

<details>
<summary><b>图片</b> —— 拼接 · 填充 · 裁剪 · WebP —— <code>etool image</code></summary>

**左右 / 上下拼接**

```bash
etool --json image merge-lr left.png right.png --out lr.png
etool --json image merge-ud top.png bottom.png --out ud.png
```

```json
{"ok": true, "data": {"path": "lr.png"}}
```

**填成正方形 / 九宫格裁剪 / 批量转 WebP 重命名**

```bash
etool --json image fill-square photo.jpg --out square.jpg
etool --json image cut-grid photo.jpg
etool --json image rename-webp ./shots --remove-original
```

```json
{"ok": true, "data": {"paths": ["photo_cut00.jpg", "..."]}}
```

</details>

<details>
<summary><b>二维码</b> —— 生成 · 识别 —— <code>etool qrcode</code></summary>

**生成**

```bash
etool --json qrcode generate --text "https://example.com" --out qr.png
```

```json
{"ok": true, "data": {"path": "qr.png"}}
```

**识别(本机 OpenCV;需要 `etool[qr-decode]`)**

```bash
etool --json qrcode decode qr.png
```

```json
{"ok": true, "data": {"text": "https://example.com"}}
```

</details>

<details>
<summary><b>Jupyter</b> —— 合并 Notebook · 转 Markdown —— <code>etool ipynb</code></summary>

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

</details>

<details>
<summary><b>Markdown</b> —— 转 Word · 转 HTML · 表格转 Excel —— <code>etool md</code></summary>

```bash
etool --json md to-docx notes.md --out notes.docx
etool --json md to-html notes.md --out notes.html
etool --json md tables-to-xlsx tables.md --out tables.xlsx
```

```json
{"ok": true, "data": {"message": "Converted Markdown to Word document: notes.docx"}}
```

</details>

<details>
<summary><b>大模型</b> —— 对话 · 摘要 · 大纲 —— <code>etool llm</code></summary>

适配任意 OpenAI 兼容接口,仅用标准库 HTTP(不依赖 SDK)。凭据来自 `--api-key` / `--base-url` / `--model`,或环境变量 `ETOOL_LLM_API_KEY` / `ETOOL_LLM_BASE_URL` / `ETOOL_LLM_MODEL`(标准 `OPENAI_*` 变量同样可用)。推理模型的 `<think>...</think>` 块会被自动剔除。

**对话**

```bash
etool --json llm chat "天空为什么是蓝色的?" --system "用一句话回答。"
```

```json
{"ok": true, "data": {"text": "因为大气分子对蓝光的散射比红光更强。"}}
```

**摘要**(与原文同语言;文本可直接传入或用 `--file` 读文件)

```bash
etool --json llm summarize --file article.txt --min-words 50 --max-words 150
```

```json
{"ok": true, "data": {"summary": "..."}}
```

**层级大纲**(把文本结构化为 `main_title` / `sections` / `points` JSON)

```bash
etool --json llm outline --file article.txt
```

```json
{"ok": true, "data": {"outline": {"main_title": "...", "sections": [{"title": "...", "points": ["...", "..."]}]}}}
```

</details>

<details>
<summary><b>网页</b> —— 正文提取 · RSS / Atom · IP 脱敏 —— <code>etool web</code></summary>

**抓取网页正文文本**(自动去除 script/style 等噪声)

```bash
etool --json web fetch-text https://example.com
```

```json
{"ok": true, "data": {"text": "Example Domain\n..."}}
```

**解析 RSS 2.0 / Atom 订阅源**(URL、本地 XML 文件或 XML 字符串)

```bash
etool --json web rss https://example.com/feed.xml --limit 2
```

```json
{"ok": true, "data": {"entries": [{"title": "...", "link": "...", "published": "...", "summary": "..."}]}}
```

**IP 脱敏展示**

```bash
etool --json web mask-ip 8.8.4.4
```

```json
{"ok": true, "data": {"masked": "8.8.x.4", "is_public": true}}
```

</details>

<details>
<summary><b>命令速查壁纸</b> —— 生成速查表 PNG —— <code>etool cheatsheet</code></summary>

生成命令速查表 PNG 壁纸(最多 3×3 个分类卡片;默认左侧留出四分之一空间放桌面图标,可用 `--left-margin-ratio` 调整,0 表示不预留)。数据来自 JSON 文件(`--data`),或由大模型生成(`--keyword`,需要上文的 LLM 配置)。

```bash
etool --json cheatsheet generate --keyword git --out git.png --width 1920 --height 1080
etool --json cheatsheet generate --data uv.json --title "UV 速查表" --out uv.png
```

`uv.json` 格式:

```json
{"categories": [{"name": "基础", "commands": [{"command": "uv sync", "description": "安装依赖"}]}]}
```

```json
{"ok": true, "data": {"path": "git.png"}}
```

</details>

<details>
<summary><b>测速</b> —— 网络 · 磁盘 · 内存 —— <code>etool speed</code></summary>

**网络**(依赖 speedtest-cli,需外网,可能较慢)

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

**内存**(标准库缓冲粗略测速)

```bash
etool --json speed memory --size-mb 32
```

```json
{"ok": true, "data": {"report": "\n memory test result:\nread speed: ... MB/s\nwrite speed: ... MB/s"}}
```

</details>

<details>
<summary><b>密码</b> —— 随机密码 · 进制转换 —— <code>etool password</code></summary>

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

</details>

<details>
<summary><b>标准库调用分析</b> —— <code>etool stdlib</code></summary>

子命令只有一个:`stdlib analyze <目录>`。默认把统计嵌套在 `data.result`(JSON 对象)。若需要整份结果作为**一条 JSON 文本字符串**放在 `data.json` 里(而不是嵌套对象),加上 `--json-string`。

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

</details>

<details>
<summary><b>按 requirements 安装</b> —— <code>etool install-reqs</code></summary>

内部使用 `python -m pip install`。

```bash
etool --json install-reqs --file requirements.txt --failed-file failed.txt --retry 2
```

```json
{"ok": true, "data": {"success": true}}
```

失败时示例:

```json
{"ok": false, "error": {"code": "RUNTIME_ERROR", "message": "some packages failed to install", "details": {}}}
```

</details>

<details>
<summary><b>定时任务解析调试</b> —— <code>etool scheduler</code></summary>

```bash
etool --json scheduler parse 120
etool --json scheduler parse '"08:00"'
```

```json
{"ok": true, "data": {"log": "Execute every 120 seconds"}}
```

</details>

<details>
<summary><b>发邮件</b> —— SMTP —— <code>etool email</code></summary>

勿在命令行历史中暴露真实密码;自动化请用环境变量等注入。

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

</details>

## 在 Python 中使用

每个 CLI 功能都对应一个 `Manager*` 类的静态方法:

```python
from etool import ManagerPdf, ManagerImage, ManagerQrcode, ManagerMd

ManagerPdf.merge_pdfs(["part1.pdf", "part2.pdf"], "merged.pdf")
ManagerImage.fill_image("photo.jpg")                      # 填充为正方形
ManagerQrcode.generate_qrcode("https://example.com", "qr.png")
ManagerMd.convert_md_to_docx("notes.md", "notes.docx")
```

在自己的代码中使用结构化结果:

```python
from etool import ok, err, EtoolError, ErrorCode

payload = ok({"path": "/tmp/out.pdf"})
failure = err(EtoolError(ErrorCode.VALIDATION_ERROR, "参数错误", {"field": "x"}))
```

缺少可选依赖不会破坏整个包:每个管理器都是防御式导入,`etool.get_import_status()` 可查询哪些模块可用。

## 面向 AI Agent

`etool --json <命令>` 专为 Agent 与脚本调用设计:

- stdout 永远只有**一份** JSON 文档(合法 JSON,2 空格缩进);
- 用 `ok` 字段判断成功或失败;
- 错误码是稳定契约:

| 错误码 | 含义 |
|---|---|
| `VALIDATION_ERROR` | 输入参数错误或缺失 |
| `NOT_FOUND` | 文件或资源不存在 |
| `IO_ERROR` | 读写失败 |
| `DEPENDENCY_ERROR` | 缺少可选依赖(`details.install` 会给出安装命令) |
| `RUNTIME_ERROR` | 其他运行时错误 |

```json
{"ok": false, "error": {"code": "DEPENDENCY_ERROR", "message": "QR decoding requires OpenCV", "details": {"install": "pip install \"etool[qr-decode]\""}}}
```

### Agent Skills

仓库在 [`.cursor/skills/`](.cursor/skills/) 下内置了一组 [Agent Skill](https://cursor.com/docs/context/skills)——按领域拆分的 `SKILL.md`,教会编码 Agent(Cursor、Claude Code 等)何时以及如何调用 `etool` CLI:

| Skill | 覆盖范围 |
|---|---|
| `etool-pdf` | 合并 / 拆分 / 加密 / 解密 / 插入 / 水印 / 转图片 |
| `etool-office` | docx、excel、md、ipynb 相关命令 |
| `etool-image` | image、qrcode、cheatsheet 相关命令 |
| `etool-web` | fetch-text、rss、mask-ip |
| `etool-llm` | chat、summarize、outline |
| `etool-utils` | password、speed、stdlib analyze |

在本仓库中,Cursor 会自动发现这些 Skill。要在其他项目中使用,把 Skill 目录复制到项目的 `.cursor/skills/`(Cursor)或 `.claude/skills/`(Claude Code)即可——两者格式完全相同,并确保已安装 `etool`(`pip install etool`)。

## 开发

推荐使用 [uv](https://docs.astral.sh/uv/)(`uv.lock` 已纳入版本控制;dev 组包含重型可选依赖,可直接跑全量测试):

```bash
uv sync
uv run pytest tests/test_etool.py -v
```

使用 pip:

```bash
pip install -e ".[all,dev]"
pytest tests/test_etool.py -v
```

版本历史见 [CHANGELOG.md](https://github.com/jiangyangcreate/etool/blob/main/CHANGELOG.md)(包括 2.0 为保持完全跨平台而刻意移除的 Windows 专属能力)。

## 参与贡献

欢迎提 Issue 与 PR:[github.com/jiangyangcreate/etool](https://github.com/jiangyangcreate/etool)。如果 etool 帮你省了时间,点个 ⭐ 能让更多人发现它。

[![Star History Chart](https://api.star-history.com/svg?repos=jiangyangcreate/etool&type=Date)](https://star-history.com/#jiangyangcreate/etool&Date)

## 许可证

[Apache-2.0](https://github.com/jiangyangcreate/etool/blob/main/LICENSE)
