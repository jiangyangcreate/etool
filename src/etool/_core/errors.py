"""Unified error model and JSON-serializable result envelopes for AI-friendly tooling."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Stable machine-readable error codes."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    IO_ERROR = "IO_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"


@dataclass
class EtoolError(Exception):
    """Structured error; safe to convert to JSON for agents and CLI."""

    code: ErrorCode
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code.value, "message": self.message, "details": self.details}


def ok(data: Any = None) -> dict[str, Any]:
    """Success envelope (JSON-serializable when data is)."""
    return {"ok": True, "data": data}


def err(error: EtoolError) -> dict[str, Any]:
    """Failure envelope."""
    return {"ok": False, "error": error.to_dict()}


def is_ok(envelope: dict[str, Any]) -> bool:
    return bool(envelope.get("ok"))
