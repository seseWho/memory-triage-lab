from __future__ import annotations

import http.client
import io
import json
import urllib.error
import urllib.request
from email.message import Message
from typing import Any, cast

import pytest

from memory_triage.llm import LLMConnectionError, LLMResponseError, OpenAICompatibleClient
from memory_triage.settings import LLMSettings


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self._body = json.dumps(payload).encode()

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class FakeOpener:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.requests: list[urllib.request.Request] = []

    def open(self, request: urllib.request.Request, timeout: float) -> Any:
        self.requests.append(request)
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return FakeResponse(response)


def test_health_requires_configured_model() -> None:
    client = OpenAICompatibleClient(
        LLMSettings(model="qwen3-8b-awq"), FakeOpener([{"data": [{"id": "qwen3-8b-awq"}]}])
    )
    assert client.health() == ("qwen3-8b-awq",)


def test_completion_requests_json_and_returns_usage() -> None:
    opener = FakeOpener(
        [
            {
                "model": "qwen3-8b-awq",
                "choices": [{"message": {"content": '{"status":"ok"}'}}],
                "usage": {"prompt_tokens": 11, "completion_tokens": 4},
            }
        ]
    )
    result = OpenAICompatibleClient(LLMSettings(), opener).complete_json("system", "user")
    request_body = json.loads(cast(bytes, opener.requests[0].data or b"{}"))
    assert request_body["response_format"] == {"type": "json_object"}
    assert result.content == '{"status":"ok"}'
    assert result.prompt_tokens == 11
    assert result.completion_tokens == 4


def test_completion_rejects_non_json_content() -> None:
    response = {"choices": [{"message": {"content": "not-json"}}]}
    client = OpenAICompatibleClient(LLMSettings(), FakeOpener([response]))
    with pytest.raises(LLMResponseError, match="not valid JSON"):
        client.complete_json("system", "user")


def test_completion_rejects_json_array_content() -> None:
    response = {"choices": [{"message": {"content": "[]"}}]}
    client = OpenAICompatibleClient(LLMSettings(), FakeOpener([response]))
    with pytest.raises(LLMResponseError, match="JSON object"):
        client.complete_json("system", "user")


def test_connection_failure_is_typed() -> None:
    error = urllib.error.URLError("offline")
    client = OpenAICompatibleClient(LLMSettings(), FakeOpener([error]))
    with pytest.raises(LLMConnectionError, match="Could not reach"):
        client.health()


def test_incomplete_response_is_typed() -> None:
    error = http.client.IncompleteRead(b'{"data":')
    client = OpenAICompatibleClient(LLMSettings(), FakeOpener([error]))
    with pytest.raises(LLMConnectionError, match="Could not reach"):
        client.health()


def test_http_failure_preserves_status() -> None:
    error = urllib.error.HTTPError(
        "http://localhost:8000/v1/models",
        503,
        "unavailable",
        Message(),
        io.BytesIO(b"busy"),
    )
    client = OpenAICompatibleClient(LLMSettings(), FakeOpener([error]))
    with pytest.raises(LLMResponseError, match="HTTP 503: busy"):
        client.health()
