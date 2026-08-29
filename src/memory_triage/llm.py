from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from memory_triage.settings import LLMSettings


class LLMError(RuntimeError):
    """Base error for local LLM communication."""


class LLMConnectionError(LLMError):
    """The local server could not be reached."""


class LLMResponseError(LLMError):
    """The server returned an invalid or unsuccessful response."""


class UrlOpener(Protocol):
    def open(self, request: urllib.request.Request, timeout: float) -> Any: ...


@dataclass(frozen=True, slots=True)
class CompletionResult:
    content: str
    model: str
    prompt_tokens: int | None
    completion_tokens: int | None


class OpenAICompatibleClient:
    def __init__(self, settings: LLMSettings, opener: UrlOpener | None = None) -> None:
        self.settings = settings
        self._opener = opener or urllib.request.build_opener()

    def health(self) -> tuple[str, ...]:
        payload = self._request("GET", "/models")
        data = payload.get("data")
        if not isinstance(data, list):
            raise LLMResponseError("Model catalog does not contain a data list")
        model_ids = tuple(
            str(model["id"]) for model in data if isinstance(model, dict) and "id" in model
        )
        if self.settings.model not in model_ids:
            raise LLMResponseError(
                f"Configured model '{self.settings.model}' is not served; available={model_ids}"
            )
        return model_ids

    def complete_json(self, system_prompt: str, user_prompt: str) -> CompletionResult:
        payload = self._request(
            "POST",
            "/chat/completions",
            {
                "model": self.settings.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": self.settings.temperature,
                "seed": self.settings.seed,
                "max_tokens": self.settings.max_tokens,
                "response_format": {"type": "json_object"},
            },
        )
        try:
            choice = payload["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMResponseError(
                "Completion response has an invalid choices structure"
            ) from error
        if not isinstance(content, str) or not content.strip():
            raise LLMResponseError("Completion content is empty")
        try:
            decoded = json.loads(content)
        except json.JSONDecodeError as error:
            raise LLMResponseError("Completion content is not valid JSON") from error
        if not isinstance(decoded, dict):
            raise LLMResponseError("Completion content must be a JSON object")
        usage = payload.get("usage", {})
        return CompletionResult(
            content=content,
            model=str(payload.get("model", self.settings.model)),
            prompt_tokens=_optional_int(usage, "prompt_tokens"),
            completion_tokens=_optional_int(usage, "completion_tokens"),
        )

    def _request(
        self, method: str, path: str, body: dict[str, object] | None = None
    ) -> dict[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            f"{self.settings.base_url}{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with self._opener.open(request, timeout=self.settings.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            try:
                detail = error.read().decode("utf-8", errors="replace")
            except http.client.IncompleteRead as read_error:
                detail = read_error.partial.decode("utf-8", errors="replace")
            raise LLMResponseError(f"vLLM returned HTTP {error.code}: {detail}") from error
        except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError, OSError) as error:
            raise LLMConnectionError(f"Could not reach vLLM at {self.settings.base_url}") from error
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as error:
            raise LLMResponseError("vLLM returned invalid JSON") from error
        if not isinstance(parsed, dict):
            raise LLMResponseError("vLLM response root must be a JSON object")
        return parsed


def _optional_int(mapping: object, key: str) -> int | None:
    if not isinstance(mapping, dict):
        return None
    value = mapping.get(key)
    return value if isinstance(value, int) else None
