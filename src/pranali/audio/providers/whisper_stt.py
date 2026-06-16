from pathlib import Path
from src.pranali.audio.stt import STTProvider
from src.pranali.audio.types import TranscriptionResult
from src.pranali.utils.errors import ProviderCapabilityError

class WhisperSTTProvider(STTProvider):
    async def transcribe(self, audio_path: Path) -> TranscriptionResult:
        raise ProviderCapabilityError("Whisper STT not fully implemented yet.")

    async def health_check(self) -> bool:
        return False
