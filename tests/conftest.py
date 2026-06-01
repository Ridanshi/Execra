"""
Shared pytest configuration and fixtures.

Imports are guarded so that this file can be loaded in minimal CI
environments (e.g. the regression-tests job that only installs pytest
and python-dotenv) without crashing on a missing package or a missing
required environment variable.
"""

import os

import pytest

# Provide safe defaults for required env vars so that
# core.config / env_validator can be imported in test environments that
# do not have a .env file.
os.environ.setdefault("LLM_BACKEND", "llama")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

try:
    import numpy as np

    _numpy_available = True
except ImportError:
    _numpy_available = False

try:
    from core.config import Settings

    _settings_available = True
except (ImportError, OSError):
    Settings = None  # type: ignore[assignment,misc]
    _settings_available = False


@pytest.fixture
def api_base_url():
    """Returns the base URL for the API in tests."""
    return "http://localhost:8000"


@pytest.fixture
def sample_frame():
    """Return a small dummy screen frame for tests."""
    if not _numpy_available:
        pytest.skip("numpy not installed")
    return np.zeros((10, 10, 3), dtype=np.uint8)  # type: ignore[name-defined]


@pytest.fixture
def mock_settings():
    """Return a Settings object configured for unit tests."""
    if not _settings_available or Settings is None:
        pytest.skip("core.config not available")
    settings = Settings()
    settings.LLM_BACKEND = "test-model"
    settings.OPENAI_API_KEY = "test-openai-key"
    settings.GEMINI_API_KEY = "test-gemini-key"
    settings.SCREEN_CAPTURE_FPS = 1
    settings.DETECTION_THRESHOLD = 0.1
    settings.DELTA_THRESHOLD = 0.01
    settings.API_HOST = "127.0.0.1"
    settings.API_PORT = 9001
    settings.LOG_LEVEL = "DEBUG"
    settings.REDIS_URL = "redis://localhost:6379"
    settings.TRUST_SCORE_W1 = 0.4
    settings.TRUST_SCORE_W2 = 0.35
    settings.TRUST_SCORE_W3 = 0.25
    return settings


@pytest.fixture(autouse=True, scope="module")
def cleanup_module_patches():
    """Automatically stop all active mocks after each module finishes."""
    yield
    from unittest.mock import patch

    patch.stopall()
