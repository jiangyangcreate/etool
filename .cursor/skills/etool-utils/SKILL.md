---
name: etool-utils
description: Generate random passwords, convert integers between numeric bases (2-36), benchmark network/disk/memory speed, and count Python standard-library usage in a project via the etool CLI. Use when the user asks for a password, base conversion, a quick speed test, or stdlib usage statistics.
---

# Utility commands with etool

Requires the `etool` CLI: `pip install etool` (verify with `etool --json version`).

Always pass `--json`: stdout is exactly one envelope, either
`{"ok": true, "data": {...}}` or `{"ok": false, "error": {"code", "message", "details"}}`.

## Passwords and bases

```bash
etool --json password random --length 16
etool --json password convert-base ff --from-base 16 --to-base 2
```

## Benchmarks

Reports are returned as text in `data.report`. The network test uses speedtest-cli, needs internet, and can take a minute or more — run it with a generous timeout.

```bash
etool --json speed network
etool --json speed disk --file-size-mb 20
etool --json speed memory --size-mb 64
```

## Standard-library usage analysis

Recursively scan `.py` files under a folder (skips `.venv`) and count stdlib calls as a nested `module → attribute → count` dict in `data.result`:

```bash
etool --json stdlib analyze ./src
```
