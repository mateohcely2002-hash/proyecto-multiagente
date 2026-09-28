"""Agente revisor: valida el entregable y decide si se acepta."""

from __future__ import annotations

from ..context import Context
from ..message import Message, MessageRole, Task, TaskStatus
from .base import Agent


class ReviewerAgent(Agent):
    """Revisa la última tarea completada y la aprueba o la rechaza."""

    name = "reviewer"
    minimo_caracteres = 20

    def handle(self, message: Message, context: Context) -> Message:
        task = self._ultima_completada(context)
        if self.aprobado(message.content):
            veredicto = "aprobado"
        else:
            task.status = TaskStatus.REJECTED
            veredicto = "rechazado"
        return Message(
            sender=self.name,
            recipient=message.sender,
            role=MessageRole.CRITIQUE,
            content=f"{veredicto}: {task.description}",
        )

    @classmethod
    def aprobado(cls, entregable: str) -> bool:
        """Punto de extensión: sustituir por criterios reales de calidad."""
        return len(entregable.strip()) >= cls.minimo_caracteres

    @staticmethod
    def _ultima_completada(context: Context) -> Task:
        for task in reversed(context.tasks):
            if task.status is TaskStatus.DONE:
                return task
        raise LookupError("no hay tarea completada por revisar")
