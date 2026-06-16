import asyncio
import sys
import uuid
import typer
import structlog
from rich.console import Console
from rich.panel import Panel
from sqlalchemy.ext.asyncio import AsyncSession

from src.pranali.bootstrap import bootstrap
from src.pranali.db.session import get_session_factory
from src.pranali.db.seed import seed_default_data
from src.pranali.db.health import check_db_health, check_pgvector_health
from src.pranali.llm.registry import registry
from src.pranali.llm.router import LLMRouter
from src.pranali.conversation.orchestrator import ConversationOrchestrator
from src.pranali.conversation.session_manager import SessionManager
from src.pranali.config import settings

app = typer.Typer(help="Pranali - Persistent Personal AI Companion")
console = Console()
logger = structlog.get_logger(__name__)

@app.command()
def voice():
    """Start voice interaction loop."""
    bootstrap()
    logger.info("app_start", command="voice")
    asyncio.run(_run_voice())

async def _run_voice():
    from src.pranali.audio.recorder import LocalAudioRecorder
    from src.pranali.audio.providers.mock_stt import MockSTTProvider
    from src.pranali.audio.providers.mock_tts import MockTTSProvider
    from src.pranali.audio.voice_loop import VoiceLoopManager
    from src.pranali.events.bus import InProcessEventBus
    from src.pranali.events.dispatcher import EventDispatcher
    from src.pranali.events.schemas import PranaliEvent
    from src.pranali.events.types import EventType
    from src.pranali.tasks.supervisor import TaskSupervisor
    from src.pranali.conversation.orchestrator import ConversationOrchestrator

    bus = InProcessEventBus()
    dispatcher = EventDispatcher(bus)
    recorder = LocalAudioRecorder()
    stt = MockSTTProvider()
    tts = MockTTSProvider()
    loop_mgr = VoiceLoopManager(recorder, stt, bus)
    task_supervisor = TaskSupervisor()

    async def extraction_handler(payload: dict):
        user_id = uuid.UUID(payload["user_id"])
        user_name = payload["user_name"]
        recent_turns = payload["recent_turns"]
        source_event_id = uuid.UUID(payload["source_event_id"]) if payload.get("source_event_id") else None

        # New DB session for background task
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as background_session:
            from src.pranali.llm.router import LLMRouter
            from src.pranali.memory.service import MemoryService
            memory_service = MemoryService(background_session, LLMRouter())
            await memory_service.extract_and_store_from_turn(
                user_id=user_id,
                user_name=user_name,
                recent_turns=recent_turns,
                source_event_id=source_event_id
            )

    task_supervisor.register_handler(TaskType.MEMORY_EXTRACTION, extraction_handler)

    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            sm = SessionManager(session)
            try:
                user = await sm.get_or_create_default_user()
                identity = await sm.get_active_identity()
            except ValueError as e:
                console.print(f"[red]{e}[/red]")
                return

            chat_session = await sm.create_session(user.id, title="Voice Chat")
            orchestrator = ConversationOrchestrator(session, LLMRouter(), task_supervisor=task_supervisor)

            await bus.start()
            await dispatcher.start()
            await task_supervisor.start()

            console.print(Panel.fit(f"[bold green]Voice Mode Started[/bold green]\nUser: {user.display_name} | Assistant: {identity.assistant_name}\nType /exit to quit.", border_style="green"))

            # Simple event handler to hook the generated user message event back into the conversation orchestrator
            async def handle_user_message(event: PranaliEvent):
                # When voice loop finishes transcription, it fires USER_MESSAGE_READY
                # We consume it here and feed it to the orchestrator manually for the loop
                content = event.content or ""
                console.print(f"\n[bold blue]{user.display_name} (Voice):[/bold blue] {content}")
                console.print(f"[bold magenta]{identity.assistant_name}:[/bold magenta] ", end="")

                full_response = ""
                async for chunk in orchestrator.process_message(user.id, chat_session.id, content, input_mode="voice", raw_payload=event.payload):
                    console.print(chunk, end="")
                    sys.stdout.flush()
                    full_response += chunk
                console.print()

                # Mock TTS generation/playback queue logic
                if settings.audio.output_enabled:
                    console.print("[yellow](Synthesizing and playing TTS...)[/yellow]")
                    audio_out = await tts.synthesize(full_response)
                    # player.play(audio_out.audio_path)

            await bus.subscribe(EventType.USER_MESSAGE_READY, handle_user_message)

            while True:
                console.print("\n[yellow]Recording audio...[/yellow] (Press Ctrl+C to stop recording/exit loop)")
                try:
                    await loop_mgr.record_and_publish(user.id, chat_session.id)
                    # wait a little bit for the dispatcher to pick it up and run orchestrator
                    await asyncio.sleep(2)
                except KeyboardInterrupt:
                    break

            console.print("\n[yellow]Shutting down voice mode gracefully...[/yellow]")
            await orchestrator.wait_for_background_tasks()
            await task_supervisor.stop()
            await dispatcher.stop()
            await bus.stop()
            console.print("[green]Goodbye![/green]")

    except Exception as e:
        console.print(f"[red]Database unavailable or error: {e}[/red]")

@app.command()
def reflect():
    """Trigger manual memory reflection."""
    bootstrap()
    logger.info("app_start", command="reflect")
    asyncio.run(_run_reflect())

async def _run_reflect():
    from src.pranali.memory.reflection import MemoryReflection
    router = LLMRouter()
    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            sm = SessionManager(session)
            user = await sm.get_or_create_default_user()
            reflector = MemoryReflection(session, router)
            mem = await reflector.reflect(user.id)
            if mem:
                console.print(f"[green]Reflection created: {mem.content}[/green]")
            else:
                console.print("[yellow]No recent memories to reflect on.[/yellow]")
    except Exception as e:
        console.print(f"[red]Database unavailable: {e}[/red]")

@app.command()
def memory_maintenance():
    """Trigger memory decay and archival."""
    bootstrap()
    logger.info("app_start", command="memory-maintenance")
    asyncio.run(_run_memory_maintenance())

async def _run_memory_maintenance():
    from src.pranali.memory.decay import MemoryDecay
    from src.pranali.memory.archive import MemoryArchive

    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            sm = SessionManager(session)
            user = await sm.get_or_create_default_user()

            decay = MemoryDecay(session)
            decay_count = await decay.decay_memories(user.id)
            console.print(f"[green]Decayed {decay_count} memories.[/green]")

            archive = MemoryArchive(session)
            archive_count = await archive.archive_stale_memories(user.id)
            console.print(f"[green]Archived {archive_count} memories.[/green]")
    except Exception as e:
        console.print(f"[red]Database unavailable: {e}[/red]")

@app.command()
def consolidate_memories():
    """Consolidate duplicate memories."""
    bootstrap()
    logger.info("app_start", command="consolidate-memories")
    asyncio.run(_run_consolidate_memories())

async def _run_consolidate_memories():
    from src.pranali.memory.consolidator import MemoryConsolidator
    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            sm = SessionManager(session)
            user = await sm.get_or_create_default_user()

            consolidator = MemoryConsolidator(session)
            count = await consolidator.consolidate_duplicates(user.id)
            console.print(f"[green]Consolidated {count} duplicate memories.[/green]")
    except Exception as e:
        console.print(f"[red]Database unavailable: {e}[/red]")

@app.command()
def cache_health():
    """Check cache provider health."""
    bootstrap()
    logger.info("app_start", command="cache-health")
    asyncio.run(_run_cache_health())

async def _run_cache_health():
    from src.pranali.cache.store import CacheStore
    from src.pranali.cache.memory_cache import InMemoryCacheStore
    from src.pranali.cache.redis_cache import RedisCacheStore

    memory_cache = InMemoryCacheStore()
    mem_ok = await memory_cache.health_check()
    console.print(f"InMemoryCache: {'[green]OK[/green]' if mem_ok else '[red]FAILED[/red]'}")

    try:
        redis_cache = RedisCacheStore(settings.cache.redis_url)
        redis_ok = await redis_cache.health_check()
        console.print(f"RedisCache: {'[green]OK[/green]' if redis_ok else '[red]FAILED[/red]'}")
    except ImportError:
        console.print("[yellow]Redis cache disabled (package missing).[/yellow]")

@app.command()
def event_health():
    """Check event bus health."""
    bootstrap()
    logger.info("app_start", command="event-health")
    asyncio.run(_run_event_health())

async def _run_event_health():
    from src.pranali.events.bus import InProcessEventBus
    bus = InProcessEventBus()
    ok = await bus.health_check()
    console.print(f"InProcessEventBus: {'[green]OK[/green]' if ok else '[red]FAILED[/red]'}")

@app.command()
def chat():
    """Start terminal chat session."""
    bootstrap()
    logger.info("app_start", command="chat")
    asyncio.run(_run_chat())

async def _run_chat():
    router = LLMRouter()
    from src.pranali.tasks.supervisor import TaskSupervisor
    from src.pranali.tasks.types import TaskType
    from src.pranali.memory.service import MemoryService

    task_supervisor = TaskSupervisor()

    async def extraction_handler(payload: dict):
        user_id = uuid.UUID(payload["user_id"])
        user_name = payload["user_name"]
        recent_turns = payload["recent_turns"]
        source_event_id = uuid.UUID(payload["source_event_id"]) if payload.get("source_event_id") else None

        # New DB session for background task
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as background_session:
            memory_service = MemoryService(background_session, router)
            await memory_service.extract_and_store_from_turn(
                user_id=user_id,
                user_name=user_name,
                recent_turns=recent_turns,
                source_event_id=source_event_id
            )

    task_supervisor.register_handler(TaskType.MEMORY_EXTRACTION, extraction_handler)
    await task_supervisor.start()

    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            sm = SessionManager(session)
            try:
                user = await sm.get_or_create_default_user()
                identity = await sm.get_active_identity()
            except ValueError as e:
                console.print(f"[red]{e}[/red]")
                return

            chat_session = await sm.create_session(user.id, title="Terminal Chat")
            orchestrator = ConversationOrchestrator(session, router, task_supervisor=task_supervisor)

            console.print(Panel.fit(f"[bold green]Welcome to Pranali Phase 1[/bold green]\nUser: {user.display_name} | Assistant: {identity.assistant_name}\nType /help for commands.", border_style="green"))

            while True:
                try:
                    user_input = console.input(f"\n[bold blue]{user.display_name}:[/bold blue] ")
                    if not user_input.strip():
                        continue

                    if user_input.startswith("/"):
                        if user_input == "/exit":
                            break
                        elif user_input == "/help":
                            console.print("Commands: /exit, /help, /memories, /profile, /health")
                            continue
                        elif user_input == "/memories":
                            await _show_memories(session, user.id)
                            continue
                        elif user_input == "/profile":
                            console.print(f"User: {user.display_name} ({user.timezone})")
                            console.print(f"Assistant: {identity.assistant_name}\n{identity.persona_summary}")
                            continue
                        elif user_input == "/health":
                            await _run_health()
                            continue
                        else:
                            console.print("Unknown command.")
                            continue

                    console.print(f"[bold magenta]{identity.assistant_name}:[/bold magenta] ", end="")

                    async for chunk in orchestrator.process_message(user.id, chat_session.id, user_input):
                        console.print(chunk, end="")
                        sys.stdout.flush()
                    console.print()

                except (KeyboardInterrupt, EOFError):
                    break
                except Exception as e:
                    logger.error("chat_error", error=str(e), exc_info=True)
                    console.print(f"\n[red]Error: {e}[/red]")

            console.print("\n[yellow]Shutting down gracefully, saving memories...[/yellow]")
            await orchestrator.wait_for_background_tasks()
            await task_supervisor.stop()
            console.print("[green]Goodbye![/green]")
    except Exception as e:
        console.print(f"[red]Database unavailable: {e}[/red]")

@app.command()
def init_db():
    """Initialize database and seed default data."""
    bootstrap()
    logger.info("app_start", command="init-db")
    asyncio.run(_run_init_db())

async def _run_init_db():
    from alembic.config import Config
    from alembic import command

    console.print("[yellow]Applying migrations...[/yellow]")
    alembic_cfg = Config("alembic.ini")

    try:
        # Run sync command in executor to not block async loop if we were deep, but here we just block
        command.upgrade(alembic_cfg, "head")
        logger.info("migration_complete")
        console.print("[green]Migrations applied.[/green]")
    except Exception as e:
        console.print(f"[red]Migration error: {e}[/red]")
        sys.exit(1)

    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            await seed_default_data(session)
            console.print("[green]Database seeded with default user and identity.[/green]")
    except Exception as e:
        console.print(f"[red]Database unavailable for seeding: {e}[/red]")
        sys.exit(1)


@app.command()
def health():
    """Check system health."""
    bootstrap()
    logger.info("app_start", command="health")
    asyncio.run(_run_health())

async def _run_health():
    db_ok = await check_db_health()
    pgvector_ok = await check_pgvector_health()

    console.print(f"Database OK: {'[green]Yes[/green]' if db_ok else '[red]No[/red]'}")
    console.print(f"pgvector OK: {'[green]Yes[/green]' if pgvector_ok else '[red]No[/red]'}")

    router = LLMRouter()
    roles = settings.llm.roles
    for role_name, config in roles.items():
        provider = registry.get(config.provider)
        status = await provider.health_check()
        console.print(f"Provider '{config.provider}' (Role: {role_name}): {'[green]OK[/green]' if status else '[red]FAILED (Fallback to Mock)[/red]'}")


@app.command()
def memories():
    """List recent memories."""
    bootstrap()
    logger.info("app_start", command="memories")
    asyncio.run(_run_memories())

async def _run_memories():
    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            sm = SessionManager(session)
            user = await sm.get_or_create_default_user()
            await _show_memories(session, user.id)
    except Exception as e:
        console.print(f"[red]Database unavailable: {e}[/red]")

async def _show_memories(session: AsyncSession, user_id: uuid.UUID):
    from src.pranali.db.repositories.memories import MemoryRepository
    repo = MemoryRepository(session)
    memories = await repo.get_recent_active_memories(user_id, limit=10)
    if not memories:
        console.print("No memories found.")
        return
    for m in memories:
        console.print(f"- \\[{m.memory_type}] {m.title} (Score: {m.importance_score})")

@app.command()
def profile():
    """Show profile info."""
    bootstrap()
    logger.info("app_start", command="profile")
    asyncio.run(_run_profile())

async def _run_profile():
    try:
        AsyncSessionFactory = get_session_factory()
        async with AsyncSessionFactory() as session:
            sm = SessionManager(session)
            user = await sm.get_or_create_default_user()
            identity = await sm.get_active_identity()
            console.print(f"User: {user.display_name} ({user.timezone})")
            console.print(f"Assistant: {identity.assistant_name}\n{identity.persona_summary}")
    except Exception as e:
        console.print(f"[red]Database unavailable: {e}[/red]")

if __name__ == "__main__":
    app()
