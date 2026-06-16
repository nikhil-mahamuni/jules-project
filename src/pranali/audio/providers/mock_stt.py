from pathlib import Path
from src.pranali.audio.stt import STTProvider
from src.pranali.audio.types import TranscriptionResult

class MockSTTProvider(STTProvider):
    async def transcribe(self, audio_path: Path) -> TranscriptionResult:
        return TranscriptionResult(
            text="This is a deterministic mock transcription.",
            confidence=0.99,
            language="en",
            provider="mock",
            duration_seconds=1.5
        )

    async def health_check(self) -> bool:
        return True
