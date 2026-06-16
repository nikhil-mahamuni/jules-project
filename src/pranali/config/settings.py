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
    consolidation_enabled: bool = True
    reflection_enabled: bool = True
    decay_enabled: bool = True
    archive_enabled: bool = True
    confirmation_enabled: bool = True

class EventsConfig(BaseModel):
    enabled: bool = True
    queue_max_size: int = 2000
    dispatcher_workers: int = 4

class ConcurrencyConfig(BaseModel):
    thread_pool_workers: int = 4
    process_pool_workers: int = 2
    session_lock_enabled: bool = True

class TasksConfig(BaseModel):
    enabled: bool = True
    worker_count: int = 4
    queue_max_size: int = 1000
    max_retries: int = 3
    task_timeout_seconds: int = 60

class AudioConfig(BaseModel):
    enabled: bool = True
    input_enabled: bool = True
    output_enabled: bool = True
    recorder_provider: str = "local"
    stt_provider: str = "mock"
    tts_provider: str = "mock"
    audio_dir: str = "./runtime/audio"
    input_sample_rate: int = 16000
    channels: int = 1
    record_seconds: int = 5
    silence_detection_enabled: bool = False
    silence_seconds: float = 1.0
    voice_name: str = "default"

class STTConfig(BaseModel):
    provider: str = "mock"
    whisper_model_size: str = "base"
    openai_model: str = "whisper-1"

class TTSConfig(BaseModel):
    provider: str = "mock"
    piper_model_path: str = ""
    piper_binary_path: str = ""
    openai_model: str = "gpt-4o-mini-tts"
    voice_name: str = "default"

class CacheConfig(BaseModel):
    provider: str = "memory"
    redis_url: str = "redis://localhost:6379/0"
    default_ttl_seconds: int = 3600

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
    events: EventsConfig
    concurrency: ConcurrencyConfig
    tasks: TasksConfig
    audio: AudioConfig
    stt: STTConfig
    tts: TTSConfig
    cache: CacheConfig
    llm: LLMConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
