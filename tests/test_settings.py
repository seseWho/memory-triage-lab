import pytest

from memory_triage.settings import LLMSettings


def test_settings_load_expected_environment_values() -> None:
    settings = LLMSettings.from_env(
        {
            "LLM_BASE_URL": "http://localhost:9000/v1/",
            "LLM_MODEL": "test-model",
            "LLM_TIMEOUT_SECONDS": "30",
            "LLM_MAX_TOKENS": "512",
            "LLM_TEMPERATURE": "0.25",
            "LLM_SEED": "42",
        }
    )
    assert settings.base_url == "http://localhost:9000/v1"
    assert settings.model == "test-model"
    assert settings.timeout_seconds == 30
    assert settings.max_tokens == 512
    assert settings.temperature == 0.25
    assert settings.seed == 42


def test_settings_reject_invalid_timeout() -> None:
    with pytest.raises(ValueError, match="positive"):
        LLMSettings(timeout_seconds=0)
