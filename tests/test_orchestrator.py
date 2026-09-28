"""Pruebas del flujo planificar -> ejecutar -> revisar."""

from multiagente import Orchestrator, TaskStatus
from multiagente.agents import PlannerAgent


def test_descompone_el_objetivo() -> None:
    assert PlannerAgent.descomponer("uno; dos\ntres") == ["uno", "dos", "tres"]


def test_objetivo_de_una_sola_tarea() -> None:
    assert PlannerAgent.descomponer("objetivo unico") == ["objetivo unico"]


def test_ejecucion_completa() -> None:
    report = Orchestrator().run("analizar los datos; generar el informe")

    assert len(report.tasks) == 2
    assert report.aprobadas == 2
    assert report.rechazadas == 0
    assert all(task.status is TaskStatus.DONE for task in report.tasks)


def test_la_transcripcion_registra_a_todos_los_agentes() -> None:
    report = Orchestrator().run("una sola tarea")
    remitentes = {mensaje.sender for mensaje in report.transcript}

    assert {"usuario", "planner", "worker", "reviewer"} <= remitentes


def test_el_revisor_rechaza_un_entregable_muy_corto() -> None:
    assert not Orchestrator().reviewer.aprobado("corto")
