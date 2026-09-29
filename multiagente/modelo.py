"""Modelo de datos del tablero compartido.

Nada de esto vive en la memoria de un proceso. Cada objeto se guarda como un
archivo JSON dentro del repositorio, que es el lugar donde los agentes se
encuentran.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def ahora() -> str:
    """Marca de tiempo en UTC, ordenable como texto."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def nuevo_id(prefijo: str) -> str:
    return f"{prefijo}-{uuid4().hex[:8]}"


def clave(valor: Any) -> str:
    """Valor de texto de un rol o una capacidad, venga como enum o como texto."""
    return valor.value if isinstance(valor, Enum) else str(valor)


class Capacidad(str, Enum):
    """Aquello en lo que un agente puede ser bueno."""

    ANALISIS = "analisis"
    DATOS = "datos"
    DISENO = "diseno"
    IMPLEMENTACION = "implementacion"
    PRUEBAS = "pruebas"
    REDACION = "redaccion"
    REVISION = "revision"


class Rol(str, Enum):
    """Lo que una tarea necesita. No pertenece a ningún agente de antemano."""

    DISENAR = "disenar"
    EJECUTAR = "ejecutar"
    REVISAR = "revisar"


class EstadoTarea(str, Enum):
    ABIERTA = "abierta"
    EN_CURSO = "en_curso"
    EN_REVISION = "en_revision"
    CERRADA = "cerrada"


def como_diccionario(objeto: Any) -> dict[str, Any]:
    return asdict(objeto)


def desde_diccionario(clase: type, datos: dict[str, Any]) -> Any:
    """Construye un dataclass ignorando los campos que no reconoce."""
    conocidos = {campo.name for campo in fields(clase)}
    return clase(**{nombre: valor for nombre, valor in datos.items() if nombre in conocidos})


@dataclass
class Perfil:
    """Lo que un agente declara saber y los temas que le interesan."""

    id: str
    nombre: str = ""
    destrezas: dict[str, float] = field(default_factory=dict)
    temas: list[str] = field(default_factory=list)
    actualizado: str = field(default_factory=ahora)

    def destreza(self, capacidad: Any) -> float:
        return float(self.destrezas.get(clave(capacidad), 0.0))


@dataclass
class Idea:
    """Una propuesta que un agente pone sobre la mesa."""

    id: str
    autor: str
    titulo: str
    detalle: str = ""
    creada: str = field(default_factory=ahora)


@dataclass
class Apoyo:
    """El respaldo de un agente a una idea ajena."""

    idea: str
    agente: str
    comentario: str = ""
    momento: str = field(default_factory=ahora)


@dataclass
class Tarea:
    """Una idea que ya tiene forma de trabajo concreto."""

    id: str
    titulo: str
    origen: str = ""
    promovida_por: str = ""
    descripcion: str = ""
    requisitos: dict[str, str] = field(default_factory=dict)
    creada: str = field(default_factory=ahora)


@dataclass
class Reclamo:
    """La intención de un agente de cubrir un rol de una tarea."""

    tarea: str
    rol: str
    agente: str
    puntaje: float
    motivo: str = ""
    momento: str = field(default_factory=ahora)


@dataclass
class Entregable:
    """El resultado que un agente produce para el rol que tomó."""

    tarea: str
    rol: str
    agente: str
    contenido: str
    momento: str = field(default_factory=ahora)


@dataclass
class Revision:
    """La evaluación que un par hace del trabajo de otro."""

    tarea: str
    revisor: str
    puntajes: dict[str, float] = field(default_factory=dict)
    comentario: str = ""
    momento: str = field(default_factory=ahora)
