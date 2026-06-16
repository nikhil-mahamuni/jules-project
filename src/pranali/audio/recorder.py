from abc import ABC, abstractmethod
from pathlib import Path
from src.pranali.audio.types import AudioInput

class AudioRecorder(ABC):
    @abstractmethod
    async def record_fixed_duration(self, seconds: float) -> AudioInput:
        pass

    @abstractmethod
    async def record_until_silence(self, max_seconds: float, silence_seconds: float) -> AudioInput:
        pass

class LocalAudioRecorder(AudioRecorder):
    # This class would use sounddevice/pyaudio via ThreadPoolExecutor.
    # We will implement a dummy mock version here so it doesn't break without libraries.

    async def record_fixed_duration(self, seconds: float) -> AudioInput:
        import asyncio
        await asyncio.sleep(0.1) # Simulate
        return AudioInput(
            audio_path=Path("/tmp/dummy_in.wav"),
            duration_seconds=seconds,
            sample_rate=16000,
            channels=1,
            format="wav"
        )

    async def record_until_silence(self, max_seconds: float, silence_seconds: float) -> AudioInput:
        import asyncio
        await asyncio.sleep(0.1)
        return AudioInput(
            audio_path=Path("/tmp/dummy_in_silence.wav"),
            duration_seconds=1.0,
            sample_rate=16000,
            channels=1,
            format="wav"
        )
