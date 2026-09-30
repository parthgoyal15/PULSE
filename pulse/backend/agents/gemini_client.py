"""
Shared Gemini caller.

Silent mock fallback is the judging failure mode. Every response is tagged
`ai_source: gemini | mock`. Mocks are used only when ALLOW_MOCK_AGENTS is true
(default true so the demo still runs without a key) — the UI must show that.
"""

from __future__ import annotations

import json
import os
import time

from google import genai
from google.genai import types

# Lite models first — higher free-tier headroom than gemini-3.8-flash (20/day).
MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-3.8-flash",
]

_quota_blocked_until = 0.0


class GeminiUnavailable(Exception):
    """No usable Gemini response. Callers may mock only if mocks_allowed()."""


def _key() -> str:
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if key in ("", "your_gemini_api_key"):
        return ""
    return key


def gemini_configured() -> bool:
    return bool(_key())


def quota_blocked() -> bool:
    return time.time() < _quota_blocked_until


def gemini_live() -> bool:
    return gemini_configured() and not quota_blocked()


def mocks_allowed() -> bool:
    raw = (os.getenv("ALLOW_MOCK_AGENTS") or "true").strip().lower()
    return raw in ("1", "true", "yes", "on")


def friendly_error(exc: Exception | str) -> str:
    msg = str(exc)
    lowered = msg.lower()
    if "429" in msg or "resource_exhausted" in lowered or "quota" in lowered:
        return (
            "Gemini free-tier quota is used up. The demo continues on labelled mock scores. "
            "Quota often resets tomorrow (free tier is per model). Enable billing in Google AI Studio for more requests."
        )
    if "404" in msg or "not found" in lowered:
        return "This Gemini model is not available on the current API key. Using labelled mock scores."
    if "not set" in lowered:
        return "No GEMINI_API_KEY set. Using labelled mock scores."
    return "Gemini is temporarily unavailable. Using labelled mock scores."


def generate_json(prompt: str) -> dict:
    """Return parsed JSON with ai_source / ai_model set. Raises GeminiUnavailable."""
    text, model = _generate(prompt, json_mode=True)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise GeminiUnavailable(f"Gemini returned non-JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise GeminiUnavailable("Gemini JSON was not an object")
    data["ai_source"] = "gemini"
    data["ai_model"] = model
    return data


def generate_text(prompt: str) -> tuple[str, str, str]:
    """Return (text, ai_source, ai_model)."""
    text, model = _generate(prompt, json_mode=False)
    return text, "gemini", model


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "resource_exhausted" in msg or "quota" in msg


def _generate(prompt: str, json_mode: bool) -> tuple[str, str]:
    global _quota_blocked_until

    key = _key()
    if not key:
        raise GeminiUnavailable(
            "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com/apikey"
        )

    if time.time() < _quota_blocked_until:
        raise GeminiUnavailable("Gemini free-tier quota is used up.")

    client = genai.Client(api_key=key)
    last_error: Exception | None = None
    config_kwargs: dict = {"temperature": 0.2}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )
            text = (response.text or "").strip()
            if not text:
                last_error = GeminiUnavailable(f"{model} returned empty text")
                continue
            return text, model
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if _is_quota_error(exc):
                # Don't keep hammering the same exhausted project today.
                _quota_blocked_until = time.time() + 6 * 60 * 60
                raise GeminiUnavailable(str(exc)) from exc
            continue

    raise GeminiUnavailable(f"Gemini call failed: {last_error}")
