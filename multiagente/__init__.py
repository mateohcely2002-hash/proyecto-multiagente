"""Una red de agentes pares que se encuentran en un repositorio git.

No hay orquestador. Cada agente es el mismo programa, ve el mismo tablero y
decide por su cuenta qué hacer. El repositorio es a la vez bodega y punto de
encuentro: guarda el trabajo y es el lugar donde los agentes se coordinan.
"""

from .agente import UMBRAL_APOYOS, Agente, Paso
from .emparejamiento import PESO_DESTREZA, PESO_REPUTACION, afinidad, afinidad_de, mejores_roles
from .modelo import (
    Apoyo,
    Capacidad,
    Entregable,
    EstadoTarea,
    Idea,
    Perfil,
    Reclamo,
    Revision,
    Rol,
    Tarea,
    nuevo_id,
)
from .reputacion import reputacion_de, tabla_reputacion
from .tablero import Tablero

__all__ = [
    "UMBRAL_APOYOS",
    "Agente",
    "Apoyo",
    "Capacidad",
    "Entregable",
    "EstadoTarea",
    "Idea",
    "PESO_DESTREZA",
    "PESO_REPUTACION",
    "Paso",
    "Perfil",
    "Reclamo",
    "Revision",
    "Rol",
    "Tablero",
    "Tarea",
    "afinidad",
    "afinidad_de",
    "mejores_roles",
    "nuevo_id",
    "reputacion_de",
    "tabla_reputacion",
]

__version__ = "0.2.0"
