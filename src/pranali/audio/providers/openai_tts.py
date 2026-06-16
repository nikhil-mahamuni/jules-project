from pathlib import Path
from typing import Optional
from src.pranali.audio.tts import TTSProvider
from src.pranali.audio.types import AudioOutput
from src.pranali.utils.errors import ProviderCapabilityError

class OpenAITTSProvider(TTSProvider):
    async def synthesize(self, text: str, voice: Optional[str] = None) -> AudioOutput:
        raise ProviderCapabilityError("OpenAI TTS not fully implemented yet.")

    async def health_check(self) -> bool:
        return False
