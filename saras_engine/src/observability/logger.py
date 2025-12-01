import os
from datetime import datetime


LOG_FILE = "saras_logs.txt"


def log(agent_name: str, message: str):
    """
    Log a message with timestamp and agent label.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    formatted = f"[{timestamp}] [{agent_name}] {message}"

    # Print to console
    print(formatted)

    # Append to log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")
