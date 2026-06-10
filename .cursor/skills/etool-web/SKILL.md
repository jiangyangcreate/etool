---
name: etool-web
description: Fetch readable text from a web page, parse RSS 2.0 / Atom feeds into structured entries, and mask IP addresses for display via the etool CLI. Use when the user wants page text, feed entries, or anonymized IPs without writing scraping code.
---

# Web utilities with etool

Requires the `etool` CLI: `pip install etool` (verify with `etool --json version`).

Always pass `--json`: stdout is exactly one envelope, either
`{"ok": true, "data": {...}}` or `{"ok": false, "error": {"code", "message", "details"}}`.

Fetch a URL and return its readable text (scripts/markup stripped; text in `data.text`):

```bash
etool --json web fetch-text https://example.com --timeout 30
```

Parse an RSS 2.0 / Atom feed — `source` may be a URL, a local XML file path, or raw XML; entries in `data.entries`:

```bash
etool --json web rss https://example.com/feed.xml --limit 5
```

Mask an IPv4/IPv6 address for safe display (returns `data.masked` and `data.is_public`):

```bash
etool --json web mask-ip 203.0.113.42
```
