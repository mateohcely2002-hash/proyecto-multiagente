"""Agente planificador: convierte un objetivo en tareas."""

from __future__ import annotations

import re

from ..context import Context
from ..message import Message, MessageRole, Task
from .base import Agent


class PlannerAgent(Agent):
    """Descompone el objetivo en una lista de tareas ejecutables."""

    name = "planner"

    def handle(self, message: Message, context: Context) -> Message:
        pasos = self.descomponer(message.content)
        context.tasks.extend(Task(description=paso) for paso in pasos)
        return Message(
            sender=self.name,
            recipient=message.sender,
            role=MessageRole.RESULT,
            content=f"{len(pasos)} tarea(s): " + "; ".join(pasos),
        )

    @staticmethod
    def descomponer(objetivo: str) -> list[str]:
        """Parte el objetivo por punto y coma, salto de línea o punto final.

        Punto de extensión: sustituir por una llamada a un modelo cuando el
        sistema necesite planes que el texto de entrada no insinúe.
        """
        partes = re.split(r"[;\n]+|(?<=\.)\s+", objetivo)
        limpias = [parte.strip(" .") for parte in partes if parte.strip(" .")]
        return limpias or [objetivo.strip()]
