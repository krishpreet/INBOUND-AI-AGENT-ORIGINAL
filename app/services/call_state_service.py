from enum import Enum

class CallStatus(str, Enum):
    ringing = "ringing"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

# Expand later to persist state transitions in DB
