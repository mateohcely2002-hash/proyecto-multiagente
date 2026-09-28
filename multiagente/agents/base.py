"""Contrato que cumple cualquier agente del sistema."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..message import Message

if TYPE_CHECKING:  # pragma: no cover - solo para anotaciones
    from ..context import Context


class Agent(ABC):
    """Recibe un mensaje, consulta el contexto y devuelve la respuesta.

    Un agente no conoce a los demás: no los importa ni los llama. Coordinarlos
    es responsabilidad exclusiva del orquestador, y por eso se pueden añadir,
    quitar o sustituir agentes sin tocar el resto del sistema.
    """

    name = "agent"

    @abstractmethod
    def handle(self, message: Message, context: "Context") -> Message:
        """Procesa ``message`` y devuelve el mensaje de respuesta."""
