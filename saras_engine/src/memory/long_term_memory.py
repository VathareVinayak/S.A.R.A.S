import json
import os
from typing import Dict, Any


class LongTermMemory:
    def __init__(self, file_path: str = "memory_store.json"):
        self.file_path = file_path
        self.memory = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def store_fact(self, topic: str, fact: str):
        """
        Store a fact under a topic.
        """
        if topic not in self.memory:
            self.memory[topic] = []
        self.memory[topic].append(fact)
        self.save()

    def get_facts(self, topic: str):
        """
        Fetch facts for a given topic.
        """
        return self.memory.get(topic, [])
    