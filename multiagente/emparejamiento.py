"""Cómo decide un agente qué rol tomar.

Ningún agente trae un rol fijo. Cada tarea declara qué capacidad exige cada
rol, y cada agente calcula su afinidad con esos roles a partir de dos cosas:

1. Lo que declara saber (destreza).
2. Lo que los demás opinan de su trabajo (reputación, ganada en las revisiones).

El segundo peso es mayor a propósito: el paso del tiempo y las revisiones de
los pares pesan más que la autoestima de cada agente.
"""

from __future__ import annotations

from typing import Any

from .modelo import Perfil, Tarea, clave

PESO_DESTREZA = 0.4
PESO_REPUTACION = 0.6
REPUTACION_NEUTRA = 0.5


def afinidad(destreza: float, reputacion: dict[str, float], capacidad: Any) -> float:
    """Mezcla lo que el agente dice saber con lo que los demás han visto de él."""
    ganada = reputacion.get(clave(capacidad), REPUTACION_NEUTRA)
    return round(PESO_DESTREZA * float(destreza) + PESO_REPUTACION * float(ganada), 4)


def afinidad_de(perfil: Perfil, reputacion: dict[str, float], capacidad: Any) -> float:
    return afinidad(perfil.destreza(capacidad), reputacion, capacidad)


def mejores_roles(
    tablero: Any, perfil: Perfil, tarea: Tarea, reputacion: dict[str, float]
) -> list[tuple[str, float]]:
    """Roles libres de una tarea, del mejor al peor para este agente."""
    opciones: list[tuple[str, float]] = []
    for rol, capacidad in tarea.requisitos.items():
        if tablero.rol_ocupado(tarea.id, rol):
            continue
        puntaje = afinidad(perfil.destreza(capacidad), reputacion, capacidad)
        opciones.append((rol, puntaje))
    return sorted(opciones, key=lambda par: (-par[1], par[0]))
