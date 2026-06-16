import uuid
import structlog
from src.pranali.events.bus import EventBus
from src.pranali.events.schemas import PranaliEvent
from src.pranali.events.types import EventType, EventSource
from src.pranali.audio.recorder import AudioRecorder
from src.pranali.audio.stt import STTProvider

logger = structlog.get_logger(__name__)

class VoiceLoopManager:
    def __init__(self, recorder: AudioRecorder, stt_provider: STTProvider, event_bus: EventBus):
        self.recorder = recorder
        self.stt_provider = stt_provider
        self.event_bus = event_bus

    async def record_and_publish(self, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
        try:
            # Step 1: Record Audio
            audio_input = await self.recorder.record_fixed_duration(seconds=5.0)

            # Publish Recorded Event
            recorded_event = PranaliEvent(
                user_id=user_id,
                session_id=session_id,
                event_type=EventType.VOICE_AUDIO_RECORDED,
                source=EventSource.VOICE,
                payload=audio_input.model_dump()
            )
            await self.event_bus.publish(recorded_event)

            # Step 2: Transcribe
            transcription = await self.stt_provider.transcribe(audio_input.audio_path)

            if transcription.text.strip():
                # Publish Transcript Ready
                transcript_event = PranaliEvent(
                    user_id=user_id,
                    session_id=session_id,
                    event_type=EventType.VOICE_TRANSCRIPT_READY,
                    source=EventSource.VOICE,
                    content=transcription.text,
                    payload={
                        "input_mode": "voice",
                        "audio_path": str(audio_input.audio_path),
                        "transcription_provider": transcription.provider,
                        "transcript_confidence": transcription.confidence,
                        "language": transcription.language,
                        "duration_seconds": audio_input.duration_seconds,
                        "sample_rate": audio_input.sample_rate
                    }
                )
                await self.event_bus.publish(transcript_event)

                # Publish User Message Ready for Orchestrator to consume
                message_event = PranaliEvent(
                    user_id=user_id,
                    session_id=session_id,
                    event_type=EventType.USER_MESSAGE_READY,
                    source=EventSource.VOICE,
                    content=transcription.text,
                    payload=transcript_event.payload
                )
                await self.event_bus.publish(message_event)

        except Exception as e:
            logger.error("voice_loop_failed", error=str(e), exc_info=True)
