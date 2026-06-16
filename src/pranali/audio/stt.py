from abc import ABC, abstractmethod
from pathlib import Path
from src.pranali.audio.types import TranscriptionResult

class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: Path) -> TranscriptionResult:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
