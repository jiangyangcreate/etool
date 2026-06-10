---
name: etool-llm
description: One-shot LLM calls against any OpenAI-compatible endpoint — chat, text summarization, and JSON outline extraction — via the etool CLI. Use when the user wants to summarize or outline text, or send a single prompt to an LLM from the command line.
---

# LLM helpers with etool

Requires the `etool` CLI: `pip install etool` (verify with `etool --json version`).

Always pass `--json`: stdout is exactly one envelope, either
`{"ok": true, "data": {...}}` or `{"ok": false, "error": {"code", "message", "details"}}`.

## Credentials

Resolved in order: explicit flags (`--api-key`, `--base-url`, `--model`) → `ETOOL_LLM_API_KEY` / `ETOOL_LLM_BASE_URL` / `ETOOL_LLM_MODEL` → `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`. All three values are required; a `VALIDATION_ERROR` with `details.missing` tells you which are absent. Prefer environment variables over passing secrets on the command line.

## Commands

Single-turn chat (reply in `data.text`):

```bash
etool --json llm chat "Explain CAP theorem in one paragraph" --system "Be concise" --temperature 0.2
```

Summarize text in its own language (inline text or `--file`; result in `data.summary`):

```bash
etool --json llm summarize --file article.txt --min-words 50 --max-words 150
```

Extract a structured outline as JSON (`data.outline` with `main_title` / `sections` / `points`):

```bash
etool --json llm outline --file article.txt
```
