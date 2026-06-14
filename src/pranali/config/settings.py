from typing import Dict, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseModel):
    name: str = "pranali"
    environment: str = "development"

class LoggingConfig(BaseModel):
    level: str = "INFO"
    json_format: bool = Field(False, alias="json")

class UserConfig(BaseModel):
    default_display_name: str = "Nikhil"
    timezone: str = "Asia/Kolkata"
    locale: str = "en-IN"

class AssistantConfig(BaseModel):
    name: str = "Pranali"
    persona_summary: str
    communication_style: str
    limitations: str

class DatabaseConfig(BaseModel):
    url: str

class MemoryConfig(BaseModel):
    top_k: int = 8
    recent_turns: int = 8
    extraction_enabled: bool = True
    min_importance_to_store: float = 0.55
    min_confidence_to_store: float = 0.50

class LLMRoleConfig(BaseModel):
    provider: str
    model: str
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None

class LLMConfig(BaseModel):
    default_provider: str = "mock"
    roles: Dict[str, LLMRoleConfig]

class Settings(BaseSettings):
    app: AppConfig
    logging: LoggingConfig
    user: UserConfig
    assistant: AssistantConfig
    database: DatabaseConfig
    memory: MemoryConfig
    llm: LLMConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
