from datetime import datetime


class Trace:
    def __init__(self):
        self.steps = []

    def add(self, agent_name: str, action: str, details=None):
        """
        Add a trace entry.
        
        Important:
        - Agents use this to record important actions.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": agent_name,
            "action": action,
            "details": details or {}
        }
        self.steps.append(entry)

    def export(self):
        """
        Return all trace steps.
        """
        return self.steps
