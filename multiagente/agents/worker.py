"""Agente ejecutor: produce el entregable de cada tarea."""

from __future__ import annotations

from ..context import Context
from ..message import Message, MessageRole, Task, TaskStatus
from .base import Agent


class WorkerAgent(Agent):
    """Ejecuta una tarea concreta del plan."""

    name = "worker"

    def handle(self, message: Message, context: Context) -> Message:
        task = self._siguiente_pendiente(message.content, context)
        task.status = TaskStatus.RUNNING
        task.attempts += 1
        task.result = self.ejecutar(task)
        task.status = TaskStatus.DONE
        return Message(
            sender=self.name,
            recipient=message.sender,
            role=MessageRole.RESULT,
            content=task.result,
        )

    @staticmethod
    def _siguiente_pendiente(descripcion: str, context: Context) -> Task:
        for task in context.tasks:
            if task.description == descripcion and task.status is TaskStatus.PENDING:
                return task
        raise LookupError(f"no hay tarea pendiente para: {descripcion!r}")

    @staticmethod
    def ejecutar(task: Task) -> str:
        """Punto de extensión: aquí va el trabajo real (herramientas o modelo)."""
        return f"entregable generado para: {task.description}"
