"""Generic OpenAI-compatible LLM client (stdlib HTTP; no SDK dependency)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from .._core.errors import ErrorCode, EtoolError

_ENV_KEYS = ("ETOOL_LLM_API_KEY", "OPENAI_API_KEY")
_ENV_BASE_URLS = ("ETOOL_LLM_BASE_URL", "OPENAI_BASE_URL")
_ENV_MODELS = ("ETOOL_LLM_MODEL", "OPENAI_MODEL")

_FENCE_RE = re.compile(r"^```[\w-]*\s*|\s*```$", re.MULTILINE)
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _from_env(names: tuple[str, ...]) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


class ManagerLlm:
    """Chat with any OpenAI-compatible endpoint, plus AI-output cleanup helpers.

    Credentials resolve from explicit arguments, then ``ETOOL_LLM_API_KEY`` /
    ``ETOOL_LLM_BASE_URL`` / ``ETOOL_LLM_MODEL``, then the standard
    ``OPENAI_API_KEY`` / ``OPENAI_BASE_URL`` / ``OPENAI_MODEL`` variables.
    """

    @staticmethod
    def resolve_config(
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> tuple[str, str, str]:
        """Resolve (api_key, base_url, model), raising VALIDATION_ERROR if incomplete."""
        key = api_key or _from_env(_ENV_KEYS)
        url = base_url or _from_env(_ENV_BASE_URLS)
        mdl = model or _from_env(_ENV_MODELS)
        missing = [
            name
            for name, value in (("api_key", key), ("base_url", url), ("model", mdl))
            if not value
        ]
        if missing:
            raise EtoolError(
                ErrorCode.VALIDATION_ERROR,
                "missing LLM configuration",
                {"missing": missing, "env": ["ETOOL_LLM_*", "OPENAI_*"]},
            )
        return key, url, mdl  # type: ignore[return-value]

    @classmethod
    def chat(
        cls,
        prompt: str,
        *,
        system: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        timeout: int = 120,
    ) -> str:
        """Send one chat-completion request and return the assistant text."""
        key, url, mdl = cls.resolve_config(api_key, base_url, model)

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {"model": mdl, "messages": messages}
        if temperature is not None:
            payload["temperature"] = temperature

        request = urllib.request.Request(
            url=url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:500]
            raise EtoolError(
                ErrorCode.RUNTIME_ERROR,
                f"LLM request failed with HTTP {e.code}",
                {"body": detail},
            ) from e
        except urllib.error.URLError as e:
            raise EtoolError(
                ErrorCode.RUNTIME_ERROR, f"LLM request failed: {e.reason}"
            ) from e

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise EtoolError(
                ErrorCode.RUNTIME_ERROR,
                "unexpected LLM response shape",
                {"keys": sorted(body) if isinstance(body, dict) else str(type(body))},
            ) from e
        return cls.strip_think(content)

    @staticmethod
    def strip_think(text: str) -> str:
        """Remove reasoning-model <think>...</think> blocks."""
        return _THINK_RE.sub("", text).strip()

    @classmethod
    def extract_json(cls, text: str) -> Any:
        """Parse JSON out of an LLM reply, tolerating markdown fences and prose."""
        cleaned = _FENCE_RE.sub("", cls.strip_think(text)).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        for opener, closer in (("{", "}"), ("[", "]")):
            start = cleaned.find(opener)
            end = cleaned.rfind(closer)
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    continue
        raise EtoolError(
            ErrorCode.RUNTIME_ERROR,
            "no valid JSON found in LLM reply",
            {"text": cleaned[:200]},
        )

    @classmethod
    def summarize(
        cls,
        text: str,
        *,
        min_words: int = 50,
        max_words: int = 150,
        **chat_kwargs: Any,
    ) -> str:
        """Summarize text in min_words–max_words, replying in the input language."""
        prompt = (
            f"Summarize the following text in {min_words} to {max_words} words. "
            "Reply with the summary only, as plain text without markdown, "
            f"in the same language as the text.\n\nText:\n{text}"
        )
        return cls.chat(prompt, **chat_kwargs)

    @classmethod
    def outline(cls, text: str, **chat_kwargs: Any) -> dict[str, Any]:
        """Structure text into {"main_title", "sections": [{"title", "points"}]}."""
        prompt = (
            "Organize the following text into a hierarchical outline. "
            "Output exactly one JSON object with this shape and nothing else "
            "(no markdown fences, no comments, valid double-quoted JSON):\n"
            '{"main_title": "...", "sections": [{"title": "...", "points": ["...", "..."]}]}\n'
            "Use the same language as the text.\n\nText:\n" + text
        )
        result = cls.extract_json(cls.chat(prompt, **chat_kwargs))
        if not isinstance(result, dict) or "sections" not in result:
            raise EtoolError(
                ErrorCode.RUNTIME_ERROR,
                "LLM outline reply is not the expected JSON object",
                {"result": str(result)[:200]},
            )
        return result
