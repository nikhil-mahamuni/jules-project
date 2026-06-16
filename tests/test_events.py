import pytest
import asyncio
from src.pranali.events.bus import InProcessEventBus
from src.pranali.events.dispatcher import EventDispatcher
from src.pranali.events.schemas import PranaliEvent
from src.pranali.events.types import EventType, EventSource, EventPriority

@pytest.mark.asyncio
async def test_event_bus_publish_and_dispatch():
    bus = InProcessEventBus()
    dispatcher = EventDispatcher(bus)

    received_events = []

    async def mock_handler(event: PranaliEvent):
        received_events.append(event)

    await bus.subscribe(EventType.USER_MESSAGE_READY, mock_handler)

    await bus.start()
    await dispatcher.start()

    event = PranaliEvent(
        event_type=EventType.USER_MESSAGE_READY,
        source=EventSource.TERMINAL,
        content="Test event"
    )

    await bus.publish(event)

    # Wait for dispatcher to process
    await asyncio.sleep(0.1)

    await dispatcher.stop()
    await bus.stop()

    assert len(received_events) == 1
    assert received_events[0].content == "Test event"

@pytest.mark.asyncio
async def test_event_handler_failure_is_safe():
    bus = InProcessEventBus()
    dispatcher = EventDispatcher(bus)

    async def crashing_handler(event: PranaliEvent):
        raise ValueError("Simulated handler crash")

    await bus.subscribe(EventType.SYSTEM_HEALTH_CHECK_REQUESTED, crashing_handler)

    await bus.start()
    await dispatcher.start()

    event = PranaliEvent(
        event_type=EventType.SYSTEM_HEALTH_CHECK_REQUESTED,
        source=EventSource.SYSTEM
    )

    await bus.publish(event)
    await asyncio.sleep(0.1) # Wait for it to process and crash

    # Dispatcher should still be running without crashing the main loop
    assert len(dispatcher._workers) > 0
    await dispatcher.stop()
    await bus.stop()
