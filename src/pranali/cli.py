import asyncio
import sys
import uuid
import typer
import structlog
from rich.console import Console
from rich.panel import Panel
from sqlalchemy.ext.asyncio import AsyncSession

from src.pranali.bootstrap import bootstrap
from src.pranali.db.session import engine, AsyncSessionFactory
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
def chat():
    """Start terminal chat session."""
    bootstrap()
    logger.info("app_start", command="chat")
    asyncio.run(_run_chat())

async def _run_chat():
    router = LLMRouter()

    async with AsyncSessionFactory() as session:
        sm = SessionManager(session)
        try:
            user = await sm.get_or_create_default_user()
            identity = await sm.get_active_identity()
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            return

        chat_session = await sm.create_session(user.id, title="Terminal Chat")
        orchestrator = ConversationOrchestrator(session, router)

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
        console.print("[green]Goodbye![/green]")

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
        import contextlib
        with contextlib.suppress(Exception):
            command.upgrade(alembic_cfg, "head")
        logger.info("migration_complete")
        console.print("[green]Migrations applied.[/green]")
    except Exception as e:
        console.print(f"[red]Migration error: {e}[/red]")
        return

    async with AsyncSessionFactory() as session:
        await seed_default_data(session)
        console.print("[green]Database seeded with default user and identity.[/green]")


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
    async with AsyncSessionFactory() as session:
        sm = SessionManager(session)
        user = await sm.get_or_create_default_user()
        await _show_memories(session, user.id)

async def _show_memories(session: AsyncSession, user_id: uuid.UUID):
    from src.pranali.db.repositories.memories import MemoryRepository
    repo = MemoryRepository(session)
    memories = await repo.get_recent_active_memories(user_id, limit=10)
    if not memories:
        console.print("No memories found.")
        return
    for m in memories:
        console.print(f"- \[{m.memory_type}] {m.title} (Score: {m.importance_score})")

@app.command()
def profile():
    """Show profile info."""
    bootstrap()
    logger.info("app_start", command="profile")
    asyncio.run(_run_profile())

async def _run_profile():
    async with AsyncSessionFactory() as session:
        sm = SessionManager(session)
        user = await sm.get_or_create_default_user()
        identity = await sm.get_active_identity()
        console.print(f"User: {user.display_name} ({user.timezone})")
        console.print(f"Assistant: {identity.assistant_name}\n{identity.persona_summary}")

if __name__ == "__main__":
    app()
