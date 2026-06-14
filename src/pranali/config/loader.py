import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict

from .settings import Settings

def load_yaml_config(filepath: str | Path) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    path = Path(filepath)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def substitute_env_vars(config: Any) -> Any:
    """Substitute environment variables like ${VAR_NAME} in configuration values."""
    if isinstance(config, dict):
        return {k: substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [substitute_env_vars(v) for v in config]
    elif isinstance(config, str):
        if config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.environ.get(env_var, config)
        return config
    return config

def get_settings() -> Settings:
    """Load environment variables, read YAML, and instantiate Settings."""
    load_dotenv()

    yaml_path = Path(__file__).parent.parent.parent.parent / "config" / "settings.yaml"
    yaml_data = load_yaml_config(yaml_path)

    # Substitute environment variables in YAML values (e.g. database URL)
    yaml_data = substitute_env_vars(yaml_data)

    # Pydantic BaseSettings merges the passed kwargs with values from .env
    # We pass the YAML data as the base dict.
    return Settings(**yaml_data)

settings = get_settings()
