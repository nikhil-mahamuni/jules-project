from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel

class AudioInput(BaseModel):
    audio_path: Path
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str
    metadata: Dict[str, Any] = {}

class TranscriptionResult(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    provider: str
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = {}

class AudioOutput(BaseModel):
    audio_path: Path
    text: str
    provider: str
    voice_name: Optional[str] = None
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = {}
