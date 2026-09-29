"""La reputación de un agente, ganada en las revisiones de sus pares.

No hay ninguna autoridad que reparta puntajes. Cada agente que revisa el
trabajo de otro deja sus puntajes en el tablero, y la reputación es el promedio
de esos puntajes agrupado por la capacidad que estaba en juego.

Consecuencia importante: la reputación no se puede declarar, solo se puede
ganar. Un agente que se pone 1.0 de destreza en todo arranca con ventaja, pero
si sus entregas no convencen a los demás, su puntaje de afinidad baja solo.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def reputacion_de(tablero: Any, agente: str) -> dict[str, float]:
    """Promedio de los puntajes recibidos, por capacidad."""
    acumulado: dict[str, list[float]] = defaultdict(list)

    for tarea in tablero.tareas():
        ganadores = tablero.ganadores(tarea.id)
        if agente not in ganadores.values():
            continue
        capacidad_por_rol = {rol: tarea.requisitos.get(rol, rol) for rol in ganadores}
        for revision in tablero.revisiones(tarea.id):
            puntaje = revision.puntajes.get(agente)
            if puntaje is None:
                continue
            for rol, quien in ganadores.items():
                if quien == agente:
                    acumulado[capacidad_por_rol[rol]].append(float(puntaje))

    return {capacidad: round(sum(valores) / len(valores), 4) for capacidad, valores in acumulado.items()}


def tabla_reputacion(tablero: Any) -> dict[str, dict[str, float]]:
    """Reputación de todos los agentes, por capacidad."""
    return {perfil.id: reputacion_de(tablero, perfil.id) for perfil in tablero.perfiles()}
