import pytest
import uuid
from pathlib import Path
from src.pranali.audio.providers.mock_stt import MockSTTProvider
from src.pranali.audio.providers.mock_tts import MockTTSProvider
from src.pranali.audio.recorder import LocalAudioRecorder
from src.pranali.audio.voice_loop import VoiceLoopManager
from src.pranali.events.bus import InProcessEventBus
from src.pranali.events.types import EventType
import asyncio

@pytest.mark.asyncio
async def test_mock_stt():
    stt = MockSTTProvider()
    result = await stt.transcribe(Path("/tmp/fake.wav"))
    assert result.text == "This is a deterministic mock transcription."
    assert result.confidence == 0.99
    assert await stt.health_check() is True

@pytest.mark.asyncio
async def test_mock_tts():
    tts = MockTTSProvider()
    result = await tts.synthesize("Hello world")
    assert result.text == "Hello world"
    assert result.provider == "mock"
    assert str(result.audio_path) == "/tmp/dummy_out.wav"
    assert await tts.health_check() is True

@pytest.mark.asyncio
async def test_voice_loop_manager():
    bus = InProcessEventBus()
    stt = MockSTTProvider()
    recorder = LocalAudioRecorder()

    events_seen = []
    async def handler(event):
        events_seen.append(event)

    await bus.subscribe(EventType.USER_MESSAGE_READY, handler)

    loop_mgr = VoiceLoopManager(recorder, stt, bus)

    from src.pranali.events.dispatcher import EventDispatcher
    dispatcher = EventDispatcher(bus)
    await bus.start()
    await dispatcher.start()

    await loop_mgr.record_and_publish(uuid.uuid4(), uuid.uuid4())

    await asyncio.sleep(0.2)

    await dispatcher.stop()
    await bus.stop()

    assert len(events_seen) == 1
    assert events_seen[0].content == "This is a deterministic mock transcription."
    assert events_seen[0].payload["input_mode"] == "voice"
