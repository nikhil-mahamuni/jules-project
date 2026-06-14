import pytest
import os
from src.pranali.config import get_settings

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    # Make sure tests use mock as default to avoid real API calls
    os.environ["LLM_DEFAULT_PROVIDER"] = "mock"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://pranali:pranali@localhost:5432/pranali"

@pytest.fixture
def settings():
    return get_settings()
