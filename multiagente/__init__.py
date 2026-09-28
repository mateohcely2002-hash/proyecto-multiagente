"""Sistema multiagente mínimo: orquestador y agentes especializados."""

from .context import Context
from .message import Message, MessageRole, Task, TaskStatus
from .orchestrator import Orchestrator, RunReport

__all__ = [
    "Context",
    "Message",
    "MessageRole",
    "Orchestrator",
    "RunReport",
    "Task",
    "TaskStatus",
]

__version__ = "0.1.0"
