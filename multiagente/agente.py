"""Un agente par.

Todos los agentes son el mismo programa: la misma clase, el mismo ciclo, las
mismas reglas. Lo único que los distingue es su perfil y la reputación que se
ha ganado. Ninguno manda sobre otro: se encuentran en el tablero.

Un agente no sabe cuántos compañeros hay ni quiénes son. Mira el tablero, ve
qué hace falta, calcula qué encaja mejor con él y lo toma.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .emparejamiento import afinidad_de, mejores_roles
from .git_sync import publicar
from .modelo import (
    Apoyo,
    Capacidad,
    Entregable,
    Idea,
    Perfil,
    Reclamo,
    Revision,
    Rol,
    Tarea,
    clave,
    nuevo_id,
)
from .reputacion import reputacion_de
from .tablero import Tablero

# Cuántos apoyos necesita una idea para poder convertirse en tarea.
UMBRAL_APOYOS = 2

# Orden en que un agente atiende sus opciones. Terminar lo propio va primero,
# porque una tarea a medias bloquea a los demás. Dar ideas y respaldar las
# ajenas va después de trabajar, no antes.
PRIORIDAD = {
    "entregar": 0,
    "revisar": 1,
    "reclamar": 2,
    "apoyar": 3,
    "promover": 4,
    "proponer": 5,
}

REQUISITOS_POR_DEFECTO = {
    Rol.EJECUTAR: Capacidad.IMPLEMENTACION,
    Rol.REVISAR: Capacidad.REVISION,
}


@dataclass
class Paso:
    """Algo que el agente puede hacer ahora, con su motivo y su puntaje."""

    tipo: str
    detalle: str
    referencia: str = ""
    rol: str = ""
    puntaje: float = 0.0

    def orden(self) -> tuple[int, float, str]:
        return (PRIORIDAD.get(self.tipo, 9), -self.puntaje, self.referencia)


class Agente:
    """Un participante más de la red. Ni jefe ni subordinado."""

    def __init__(
        self,
        id: str,
        tablero: Tablero,
        destrezas: dict[Any, float] | None = None,
        nombre: str = "",
        temas: list[str] | None = None,
        sincronizar: bool = False,
    ) -> None:
        self.id = id
        self.tablero = tablero
        self.nombre = nombre or id
        self.temas = list(temas or [])
        self.sincronizar = sincronizar
        self.destrezas = {clave(capacidad): float(v) for capacidad, v in (destrezas or {}).items()}

    # --- identidad ---

    @property
    def perfil(self) -> Perfil:
        return Perfil(
            id=self.id,
            nombre=self.nombre,
            destrezas=dict(self.destrezas),
            temas=list(self.temas),
        )

    def publicar_perfil(self) -> Perfil:
        """Deja constancia en el tablero de lo que sabe hacer y qué le interesa."""
        perfil = self.perfil
        self.tablero.guardar_perfil(perfil)
        self._publicar(f"perfil de {self.id}")
        return perfil

    def reputacion(self) -> dict[str, float]:
        return reputacion_de(self.tablero, self.id)

    # --- ideas ---

    def proponer_idea(self, titulo: str, detalle: str = "") -> Idea:
        idea = Idea(id=nuevo_id("i"), autor=self.id, titulo=titulo, detalle=detalle)
        self.tablero.guardar_idea(idea)
        self._publicar(f"idea {idea.id} propuesta por {self.id}")
        return idea

    def apoyar_idea(self, idea: str, comentario: str = "") -> Apoyo | None:
        if self.tablero.idea(idea) is None or self.tablero.ya_apoya(idea, self.id):
            return None
        apoyo = Apoyo(idea=idea, agente=self.id, comentario=comentario)
        self.tablero.guardar_apoyo(apoyo)
        self._publicar(f"apoyo de {self.id} a la idea {idea}")
        return apoyo

    def promover_idea(
        self,
        idea: str,
        requisitos: dict[Any, Any] | None = None,
        descripcion: str = "",
    ) -> Tarea | None:
        """Convierte una idea con respaldo suficiente en una tarea con roles."""
        propuesta = self.tablero.idea(idea)
        if propuesta is None or self.tablero.tarea_de_idea(idea) is not None:
            return None
        if len(self.tablero.apoyos(idea)) < UMBRAL_APOYOS:
            return None

        elegidos = requisitos or REQUISITOS_POR_DEFECTO
        tarea = Tarea(
            id=self.tablero.siguiente_id_tarea(idea),
            titulo=propuesta.titulo,
            origen=idea,
            promovida_por=self.id,
            descripcion=descripcion or propuesta.detalle,
            requisitos={clave(rol): clave(capacidad) for rol, capacidad in elegidos.items()},
        )
        self.tablero.guardar_tarea(tarea)
        self._publicar(f"tarea {tarea.id} promovida por {self.id}")
        return tarea

    # --- roles ---

    def reclamar(self, tarea: str, rol: Any, puntaje: float, motivo: str = "") -> Reclamo | None:
        """Toma un rol y comprueba, ya publicado, que nadie se adelantó."""
        if self.tablero.tarea(tarea) is None or self.tablero.rol_ocupado(tarea, rol):
            return None

        reclamo = Reclamo(
            tarea=tarea,
            rol=clave(rol),
            agente=self.id,
            puntaje=round(float(puntaje), 4),
            motivo=motivo,
        )
        self.tablero.guardar_reclamo(reclamo)
        self._publicar(f"{self.id} reclama {rol} en {tarea}")

        # Si dos agentes reclamaron a la vez, la regla del protocolo decide.
        ganador = self.tablero.ganador(tarea, rol)
        if ganador is None or ganador.agente != self.id:
            return None
        return reclamo

    def entregar(self, tarea: str, rol: Any | None = None, contenido: str | None = None) -> Entregable | None:
        """Produce el resultado del rol que tomó."""
        registro = self.tablero.tarea(tarea)
        if registro is None:
            return None

        if rol is not None:
            candidatos = [clave(rol)]
        else:
            candidatos = [
                nombre for nombre, quien in self.tablero.ganadores(tarea).items() if quien == self.id
            ]

        for nombre_rol in candidatos:
            ganador = self.tablero.ganador(tarea, nombre_rol)
            if ganador is None or ganador.agente != self.id:
                continue
            if self.tablero.entregado(tarea, nombre_rol, self.id):
                continue
            entrega = Entregable(
                tarea=tarea,
                rol=nombre_rol,
                agente=self.id,
                contenido=contenido if contenido is not None else self._borrador(registro, nombre_rol),
            )
            self.tablero.guardar_entregable(entrega)
            self._publicar(f"entregable de {self.id} para {tarea}/{nombre_rol}")
            return entrega
        return None

    # --- revisión entre pares ---

    def puede_revisar(self, tarea: str) -> bool:
        registro = self.tablero.tarea(tarea)
        if registro is None:
            return False
        if self.tablero.participa(tarea, self.id):
            return False  # nadie revisa su propio trabajo
        if any(revision.revisor == self.id for revision in self.tablero.revisiones(tarea)):
            return False
        return self.tablero.lista_para_revision(registro)

    def revisar(
        self, tarea: str, puntajes: dict[str, float] | None = None, comentario: str = ""
    ) -> Revision | None:
        """Evalúa el trabajo de sus pares y deja los puntajes en el tablero."""
        if not self.puede_revisar(tarea):
            return None

        if puntajes is None:
            puntajes = {
                agente: self._puntaje_provisional(tarea, agente)
                for agente in set(self.tablero.ganadores(tarea).values())
            }

        revision = Revision(
            tarea=tarea,
            revisor=self.id,
            puntajes={agente: round(float(v), 4) for agente, v in puntajes.items()},
            comentario=comentario,
        )
        self.tablero.guardar_revision(revision)
        self._publicar(f"revisión de {self.id} sobre {tarea}")
        return revision

    # --- autonomía ---

    def pasos_posibles(self) -> list[Paso]:
        """Todo lo que este agente ve que puede hacer ahora, ya ordenado."""
        reputacion = self.reputacion()
        perfil = self.perfil
        pasos: list[Paso] = []

        for tarea in self.tablero.tareas():
            if self.tablero.participa(tarea.id, self.id):
                for rol, quien in self.tablero.ganadores(tarea.id).items():
                    if quien == self.id and not self.tablero.entregado(tarea.id, rol, self.id):
                        pasos.append(
                            Paso("entregar", f"entregar {rol} de «{tarea.titulo}»", tarea.id, rol, 1.0)
                        )
                continue

            if self.puede_revisar(tarea.id):
                pasos.append(
                    Paso(
                        "revisar",
                        f"revisar «{tarea.titulo}»",
                        tarea.id,
                        Rol.REVISAR.value,
                        afinidad_de(perfil, reputacion, Capacidad.REVISION),
                    )
                )

            for rol, puntaje in mejores_roles(self.tablero, perfil, tarea, reputacion):
                pasos.append(
                    Paso("reclamar", f"tomar {rol} en «{tarea.titulo}»", tarea.id, rol, puntaje)
                )

        for idea in self.tablero.ideas():
            if idea.autor == self.id or self.tablero.ya_apoya(idea.id, self.id):
                continue
            if self.tablero.tarea_de_idea(idea.id) is not None:
                continue
            if len(self.tablero.apoyos(idea.id)) < UMBRAL_APOYOS:
                pasos.append(Paso("apoyar", f"apoyar «{idea.titulo}»", idea.id, "", 0.4))

        for idea in self.tablero.ideas():
            if self.tablero.tarea_de_idea(idea.id) is not None:
                continue
            apoyos = len(self.tablero.apoyos(idea.id))
            if apoyos >= UMBRAL_APOYOS:
                pasos.append(
                    Paso(
                        "promover",
                        f"convertir en tarea «{idea.titulo}»",
                        idea.id,
                        "",
                        min(1.0, apoyos / (UMBRAL_APOYOS * 2)),
                    )
                )

        for titulo in self._temas_sin_idea():
            pasos.append(Paso("proponer", f"proponer «{titulo}»", titulo, "", 0.1))

        pasos.sort(key=lambda paso: paso.orden())
        return pasos

    def actuar(self) -> str:
        """Mira el tablero, elige lo mejor que puede hacer y lo hace."""
        for paso in self.pasos_posibles():
            resultado = self._ejecutar(paso)
            if resultado is not None:
                return f"{self.id}: {resultado}"
        return f"{self.id}: no encontró nada que hacer"

    def _ejecutar(self, paso: Paso) -> str | None:
        if paso.tipo == "reclamar":
            return paso.detalle if self.reclamar(paso.referencia, paso.rol, paso.puntaje, paso.detalle) else None

        if paso.tipo == "entregar":
            entrega = self.entregar(paso.referencia, paso.rol)
            return f"entregó {paso.rol} de {paso.referencia}" if entrega else None

        if paso.tipo == "revisar":
            revision = self.revisar(paso.referencia)
            return f"revisó {paso.referencia} y puntuó a sus pares" if revision else None

        if paso.tipo == "apoyar":
            apoyo = self.apoyar_idea(paso.referencia)
            return f"apoyó la idea {paso.referencia}" if apoyo else None

        if paso.tipo == "promover":
            tarea = self.promover_idea(paso.referencia)
            return f"convirtió en tarea la idea {paso.referencia}" if tarea else None

        if paso.tipo == "proponer":
            idea = self.proponer_idea(paso.referencia)
            return f"propuso la idea {idea.id}: «{idea.titulo}»"

        return None

    # --- auxiliares ---

    def _temas_sin_idea(self) -> list[str]:
        propios = {idea.titulo for idea in self.tablero.ideas() if idea.autor == self.id}
        return [tema for tema in self.temas if tema not in propios]

    def _borrador(self, tarea: Tarea, rol: str) -> str:
        """Punto de extensión: aquí va el trabajo real del agente.

        Sin un modelo detrás, el agente deja constancia de cómo aborda la
        tarea. En producción esta función llama al modelo o a las herramientas
        del agente; el resto del sistema no cambia.
        """
        encabezado = {
            Rol.DISENAR.value: "Diseño propuesto",
            Rol.EJECUTAR.value: "Entregable",
            Rol.REVISAR.value: "Revisión",
        }.get(rol, "Aporte")
        capacidad = tarea.requisitos.get(rol, "")
        destreza = self.destrezas.get(capacidad, 0.0)
        ganada = self.reputacion().get(capacidad, 0.5)
        return (
            f"{encabezado} de {self.nombre} para «{tarea.titulo}». "
            f"Rol tomado: {rol}. Capacidad exigida: {capacidad}. "
            f"Destreza declarada en esa capacidad: {destreza:.2f}. "
            f"Reputación ganada hasta ahora: {ganada:.2f}."
        )

    def _puntaje_provisional(self, tarea: str, agente: str) -> float:
        """Punto de extensión: aquí va el juicio real del revisor.

        Provisional: solo mira la extensión de lo entregado, para que el
        sistema se pueda probar de punta a punta sin un modelo detrás.
        """
        entregas = [e for e in self.tablero.entregables(tarea) if e.agente == agente]
        if not entregas:
            return 0.0
        return min(1.0, 0.5 + max(len(entrega.contenido) for entrega in entregas) / 600)

    def _publicar(self, mensaje: str) -> None:
        if not self.sincronizar:
            return
        publicar(self.tablero.raiz, mensaje)
