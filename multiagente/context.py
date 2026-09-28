"""Memoria compartida del sistema (patrón blackboard)."""

from __future__ import annotations

from dataclasses import dataclass, field

from .message import Message, Task


@dataclass
class Context:
    """Estado visible para todos los agentes durante una ejecución.

    Guarda el objetivo, las tareas del plan y la transcripción completa de los
    mensajes. Al ser explícito, cualquier ejecución se puede auditar después.
    """

    goal: str = ""
    tasks: list[Task] = field(default_factory=list)
    transcript: list[Message] = field(default_factory=list)

    def record(self, message: Message) -> Message:
        """Añade un mensaje a la transcripción y lo devuelve."""
        self.transcript.append(message)
        return message
