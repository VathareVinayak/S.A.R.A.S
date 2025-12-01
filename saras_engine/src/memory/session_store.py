from typing import List, Dict

class SessionStore:
    def __init__(self, max_messages: int = 8):
        """
        Important:
        - Only keep last N messages for context engineering.
        - Avoid unlimited memory growth.
        """
        self.max_messages = max_messages
        self._messages: List[Dict] = []

    def add_message(self, role: str, content: str):
        """
        Store a new message.
        """
        self._messages.append({"role": role, "content": content})

        # Compact memory if limit exceeded
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]

    def get_history(self) -> List[Dict]:
        """
        Return the full history for building context.
        """
        return self._messages

    def clear(self):
        """
        Clear session memory.
        """
        self._messages = []
