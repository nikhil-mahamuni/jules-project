from abc import ABC, abstractmethod
from pathlib import Path

class AudioPlayer(ABC):
    @abstractmethod
    async def play(self, audio_path: Path) -> None:
        pass

class LocalAudioPlayer(AudioPlayer):
    async def play(self, audio_path: Path) -> None:
        import asyncio
        await asyncio.sleep(0.1) # Simulate playback blocking duration via ThreadPoolExecutor ideally
