from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class SourceFormat(str, Enum):
    CSV = "csv"
    JSONL = "jsonl"
    PROMPT = "prompt"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResultStatus(str, Enum):
    OK = "ok"
    FAILED = "failed"


def enum_values(enum_class: type[Enum]) -> list[str]:
    return [member.value for member in enum_class]
