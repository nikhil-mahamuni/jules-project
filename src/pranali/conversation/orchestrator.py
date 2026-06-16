import asyncio
import uuid
import structlog
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.config import settings
from src.pranali.db.repositories.events import EventRepository
from src.pranali.llm.router import LLMRouter
from src.pranali.llm.roles import LLMRole
from src.pranali.memory.service import MemoryService
from src.pranali.memory.buffer import ConversationBuffer
from src.pranali.memory.context_builder import ContextBuilder
from src.pranali.conversation.session_manager import SessionManager
from src.pranali.prompts.system_prompts import build_system_prompt
from src.pranali.tasks.supervisor import TaskSupervisor
from src.pranali.tasks.types import TaskType

logger = structlog.get_logger(__name__)

class ConversationOrchestrator:
    def __init__(self, session: AsyncSession, router: LLMRouter, task_supervisor: TaskSupervisor = None):
        self.session = session
        self.router = router
        self.session_manager = SessionManager(session)
        self.event_repo = EventRepository(session)
        self.memory_service = MemoryService(session, router)
        self.context_builder = ContextBuilder()
        self.buffer = ConversationBuffer(max_turns=settings.memory.recent_turns)
        self.task_supervisor = task_supervisor
        self.background_tasks = set()

    async def _add_background_task(self, coro):
        task = asyncio.create_task(coro)
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)

    async def wait_for_background_tasks(self):
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

    async def process_message(self, user_id: uuid.UUID, session_id: uuid.UUID, content: str, input_mode: str = "text", raw_payload: dict = None) -> AsyncIterator[str]:
        # 1. Ensure identity and user
        identity = await self.session_manager.get_active_identity()
        user = await self.session_manager.get_or_create_default_user()
        goals = await self.session_manager.goal_repo.get_active_goals(user_id)

        # 2. Write user event
        payload = raw_payload or {}
        payload["input_mode"] = input_mode
        user_event = await self.event_repo.create(
            user_id=user_id,
            session_id=session_id,
            event_type="message",
            content=content,
            role="user",
            raw_payload=payload
        )
        logger.info("user_event_written", event_id=str(user_event.id))

        # 3. Retrieve memories
        memories = await self.memory_service.retrieve_context_for_message(user_id, content)

        # 4. Build context
        context_data = self.context_builder.build(
            identity=identity,
            user_name=user.display_name,
            memories=memories,
            goals=goals,
            buffer_messages=self.buffer.get_messages(),
            current_message=content
        )

        system_prompt = build_system_prompt(**context_data["system_kwargs"])

        messages = self.buffer.get_messages() + [{"role": "user", "content": content}]

        # 5. Call LLM
        provider, model = await self.router.get_provider_for_role(LLMRole.CONVERSATION)
        logger.info("llm_call_started", provider=provider.__class__.__name__, model=model)

        assistant_response = ""
        try:
            stream = provider.stream(messages=messages, model=model, system_prompt=system_prompt)
            async for chunk in stream:
                assistant_response += chunk
                yield chunk
        finally:
            logger.info("llm_call_completed", length=len(assistant_response))

            # 7. Write assistant event
            # Note: Phase 2 audio TTS events are handled outside by Voice Loop triggering on ASSISTANT_RESPONSE_READY
            assistant_event = await self.event_repo.create(
                user_id=user_id,
                session_id=session_id,
                event_type="message",
                content=assistant_response,
                role="assistant"
            )
            logger.info("assistant_event_written", event_id=str(assistant_event.id))

            # 8. Update buffer
            self.buffer.add_user_message(content)
            self.buffer.add_assistant_message(assistant_response)

            # 9. Background extraction (Use Phase 2 Tasks if enabled, else fallback to asyncio)
            recent_turns = context_data["recent_turns"] + f"User: {content}\nAssistant: {assistant_response}\n"

            if self.task_supervisor and settings.tasks.enabled:
                await self.task_supervisor.enqueue(
                    task_type=TaskType.MEMORY_EXTRACTION,
                    payload={
                        "user_id": str(user_id),
                        "user_name": user.display_name,
                        "recent_turns": recent_turns,
                        "source_event_id": str(user_event.id)
                    }
                )
            else:
                await self._add_background_task(
                    self.memory_service.extract_and_store_from_turn(
                        user_id=user_id,
                        user_name=user.display_name,
                        recent_turns=recent_turns,
                        source_event_id=user_event.id
                    )
                )
