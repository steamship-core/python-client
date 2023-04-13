from enum import Enum


class InvocableInitStatus(str, Enum):
    NOT_NEEDED = "notNeeded"
    INITIALIZING = "initializing"
    COMPLETE = "complete"
    FAILED = "failed"
