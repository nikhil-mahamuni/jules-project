from src.pranali.config import Settings

def test_settings_load(settings: Settings):
    assert settings.app.name == "pranali"
    assert settings.llm.roles["CONVERSATION"].provider == "anthropic"
