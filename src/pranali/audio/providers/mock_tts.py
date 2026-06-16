from pathlib import Path
from typing import Optional
from src.pranali.audio.tts import TTSProvider
from src.pranali.audio.types import AudioOutput

class MockTTSProvider(TTSProvider):
    async def synthesize(self, text: str, voice: Optional[str] = None) -> AudioOutput:
        return AudioOutput(
            audio_path=Path("/tmp/dummy_out.wav"),
            text=text,
            provider="mock",
            voice_name=voice or "default",
            duration_seconds=2.0
        )

    async def health_check(self) -> bool:
        return True
