"""Mensajes y tareas: las unidades que intercambian los agentes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class MessageRole(str, Enum):
    """Intención de un mensaje dentro de la conversación."""

    REQUEST = "request"
    RESULT = "result"
    CRITIQUE = "critique"


class TaskStatus(str, Enum):
    """Ciclo de vida de una tarea."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Message:
    """Un mensaje dirigido de un agente a otro."""

    sender: str
    recipient: str
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Task:
    """Una unidad de trabajo concreta del plan."""

    description: str
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    attempts: int = 0
