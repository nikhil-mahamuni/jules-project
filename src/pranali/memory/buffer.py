from typing import List
from src.pranali.llm.types import Message

class ConversationBuffer:
    def __init__(self, max_turns: int = 8):
        self.max_turns = max_turns
        self.messages: List[Message] = []

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def get_messages(self) -> List[Message]:
        return self.messages

    def _trim(self):
        # max_turns represents number of conversational turns.
        # So we keep max_turns * 2 messages (user + assistant per turn)
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
