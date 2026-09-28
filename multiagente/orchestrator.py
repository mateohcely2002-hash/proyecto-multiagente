"""Orquestador: coordina el ciclo planificar -> ejecutar -> revisar."""

from __future__ import annotations

from dataclasses import dataclass

from .agents import Agent, PlannerAgent, ReviewerAgent, WorkerAgent
from .context import Context
from .message import Message, MessageRole, Task, TaskStatus


@dataclass
class RunReport:
    """Resultado auditable de una ejecución completa."""

    goal: str
    context: Context

    @property
    def tasks(self) -> list[Task]:
        return self.context.tasks

    @property
    def transcript(self) -> list[Message]:
        return self.context.transcript

    @property
    def aprobadas(self) -> int:
        return sum(1 for task in self.tasks if task.status is TaskStatus.DONE)

    @property
    def rechazadas(self) -> int:
        return sum(1 for task in self.tasks if task.status is TaskStatus.REJECTED)

    def resumen(self) -> str:
        lineas = [
            f"objetivo: {self.goal}",
            f"tareas: {len(self.tasks)} (aprobadas: {self.aprobadas}, rechazadas: {self.rechazadas})",
        ]
        lineas.extend(f"  [{task.status.value}] {task.description}" for task in self.tasks)
        return "\n".join(lineas)


class Orchestrator:
    """Encadena a los agentes sin que ninguno conozca a los demás."""

    usuario = "usuario"

    def __init__(
        self,
        planner: Agent | None = None,
        worker: Agent | None = None,
        reviewer: Agent | None = None,
    ) -> None:
        self.planner = planner or PlannerAgent()
        self.worker = worker or WorkerAgent()
        self.reviewer = reviewer or ReviewerAgent()

    def run(self, goal: str) -> RunReport:
        contexto = Context(goal=goal)

        self._preguntar(self.planner, goal, contexto)
        for task in list(contexto.tasks):
            ejecucion = self._preguntar(self.worker, task.description, contexto)
            self._preguntar(self.reviewer, ejecucion.content, contexto)

        return RunReport(goal=goal, context=contexto)

    def _preguntar(self, agent: Agent, contenido: str, contexto: Context) -> Message:
        peticion = Message(
            sender=self.usuario,
            recipient=agent.name,
            role=MessageRole.REQUEST,
            content=contenido,
        )
        contexto.record(peticion)
        return contexto.record(agent.handle(peticion, contexto))
