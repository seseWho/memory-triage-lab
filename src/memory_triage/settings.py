from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_BASE_URL = "http://localhost:8000/v1"
DEFAULT_MODEL = "qwen3-8b-awq"
DEFAULT_API_KEY = "local"
DEFAULT_TIMEOUT_SECONDS = 180.0
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.0
DEFAULT_SEED = 0


@dataclass(frozen=True, slots=True)
class LLMSettings:
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    api_key: str = DEFAULT_API_KEY
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    seed: int = DEFAULT_SEED

    def __post_init__(self) -> None:
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("LLM_BASE_URL must use http or https")
        if not self.model.strip():
            raise ValueError("LLM_MODEL must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("LLM_TIMEOUT_SECONDS must be positive")
        if self.max_tokens < 1:
            raise ValueError("LLM_MAX_TOKENS must be at least 1")
        if not 0 <= self.temperature <= 2:
            raise ValueError("LLM_TEMPERATURE must be between 0 and 2")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> LLMSettings:
        values = os.environ if environ is None else environ
        return cls(
            base_url=values.get("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            model=values.get("LLM_MODEL", DEFAULT_MODEL),
            api_key=values.get("LLM_API_KEY", DEFAULT_API_KEY),
            timeout_seconds=float(values.get("LLM_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)),
            max_tokens=int(values.get("LLM_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
            temperature=float(values.get("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
            seed=int(values.get("LLM_SEED", DEFAULT_SEED)),
        )
