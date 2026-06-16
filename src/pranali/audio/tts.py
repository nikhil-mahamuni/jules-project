from abc import ABC, abstractmethod
from typing import Optional
from src.pranali.audio.types import AudioOutput

class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: Optional[str] = None) -> AudioOutput:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
