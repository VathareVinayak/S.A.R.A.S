class Metrics:
    def __init__(self):
        self.data = {
            "tool_calls": 0,
            "agent_calls": 0,
            "errors": 0
        }

    def inc(self, key: str):
        """
        Increase a counter.
        """
        if key in self.data:
            self.data[key] += 1

    def get(self):
        """
        Return metrics snapshot.
        """
        return self.data
