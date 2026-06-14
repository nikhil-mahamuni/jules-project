from typing import List
from src.pranali.db.models import Goal, AssistantIdentity
from src.pranali.memory.schemas import RetrievedMemory
from src.pranali.llm.types import Message

class ContextBuilder:
    def build(
        self,
        identity: AssistantIdentity,
        user_name: str,
        memories: List[RetrievedMemory],
        goals: List[Goal],
        buffer_messages: List[Message],
        current_message: str
    ) -> dict:

        memories_text = "\n".join([f"- [{m.memory_type}] {m.title}: {m.content}" for m in memories]) or "No relevant memories found."
        goals_text = "\n".join([f"- {g.title}: {g.description}" for g in goals]) or "No active goals."

        recent_turns = ""
        for msg in buffer_messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            recent_turns += f"{role}: {content}\n"

        system_kwargs = {
            "identity_summary": identity.persona_summary,
            "communication_style": identity.communication_style,
            "limitations": identity.limitations,
            "user_display_name": user_name,
            "retrieved_memories": memories_text,
            "active_goals": goals_text
        }

        return {
            "system_kwargs": system_kwargs,
            "recent_turns": recent_turns,
            "current_message": current_message
        }
