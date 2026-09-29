"""El tablero: el repositorio como memoria compartida entre pares.

Regla estructural: **cada archivo tiene un único escritor posible**.

El nombre de cada archivo incluye el identificador del agente que lo escribe,
por ejemplo ``reclamos/t-1a2b__ejecutar__ana.json``. Por eso dos agentes nunca
escriben la misma ruta y git nunca tiene que resolver un conflicto de fusión.

Cuando dos agentes compiten por el mismo rol, cada uno deja su propio archivo y
una regla determinista decide quién gana. Ver ``docs/PROTOCOLO.md``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .modelo import (
    Apoyo,
    Entregable,
    EstadoTarea,
    Idea,
    Perfil,
    Reclamo,
    Revision,
    Tarea,
    clave,
    como_diccionario,
    desde_diccionario,
)

CARPETAS = ("agentes", "ideas", "apoyos", "tareas", "reclamos", "entregables", "revisiones")


class Tablero:
    """Lee y escribe el estado compartido dentro de un repositorio git."""

    def __init__(self, raiz: str | Path) -> None:
        self.raiz = Path(raiz).resolve()
        self.dir = self.raiz / "tablero"

    def preparar(self) -> None:
        """Crea la estructura de carpetas si no existe."""
        for carpeta in CARPETAS:
            (self.dir / carpeta).mkdir(parents=True, exist_ok=True)

    # --- rutas: el nombre del archivo siempre incluye a su escritor ---

    def ruta_perfil(self, agente: str) -> Path:
        return self.dir / "agentes" / f"{agente}.json"

    def ruta_idea(self, idea: str) -> Path:
        return self.dir / "ideas" / f"{idea}.json"

    def ruta_apoyo(self, idea: str, agente: str) -> Path:
        return self.dir / "apoyos" / f"{idea}__{agente}.json"

    def ruta_tarea(self, tarea: str) -> Path:
        return self.dir / "tareas" / f"{tarea}.json"

    def ruta_reclamo(self, tarea: str, rol: str, agente: str) -> Path:
        return self.dir / "reclamos" / f"{tarea}__{clave(rol)}__{agente}.json"

    def ruta_entregable(self, tarea: str, rol: str, agente: str) -> Path:
        return self.dir / "entregables" / f"{tarea}__{clave(rol)}__{agente}.json"

    def ruta_revision(self, tarea: str, revisor: str) -> Path:
        return self.dir / "revisiones" / f"{tarea}__{revisor}.json"

    # --- lectura y escritura ---

    def escribir(self, ruta: Path, objeto: Any) -> Path:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(como_diccionario(objeto), ensure_ascii=False, indent=2, sort_keys=True)
        ruta.write_text(texto + "\n", encoding="utf-8")
        return ruta

    @staticmethod
    def leer(ruta: Path) -> dict[str, Any] | None:
        if not ruta.exists():
            return None
        return json.loads(ruta.read_text(encoding="utf-8"))

    def _todos(self, carpeta: str) -> list[dict[str, Any]]:
        directorio = self.dir / carpeta
        if not directorio.exists():
            return []
        registros = []
        for archivo in sorted(directorio.glob("*.json")):
            datos = self.leer(archivo)
            if datos is not None:
                registros.append(datos)
        return registros

    # --- perfiles ---

    def guardar_perfil(self, perfil: Perfil) -> Path:
        return self.escribir(self.ruta_perfil(perfil.id), perfil)

    def perfiles(self) -> list[Perfil]:
        return [desde_diccionario(Perfil, datos) for datos in self._todos("agentes")]

    def perfil(self, agente: str) -> Perfil | None:
        datos = self.leer(self.ruta_perfil(agente))
        return desde_diccionario(Perfil, datos) if datos else None

    # --- ideas y apoyos ---

    def guardar_idea(self, idea: Idea) -> Path:
        return self.escribir(self.ruta_idea(idea.id), idea)

    def ideas(self) -> list[Idea]:
        return [desde_diccionario(Idea, datos) for datos in self._todos("ideas")]

    def idea(self, idea: str) -> Idea | None:
        datos = self.leer(self.ruta_idea(idea))
        return desde_diccionario(Idea, datos) if datos else None

    def guardar_apoyo(self, apoyo: Apoyo) -> Path:
        return self.escribir(self.ruta_apoyo(apoyo.idea, apoyo.agente), apoyo)

    def apoyos(self, idea: str | None = None) -> list[Apoyo]:
        registros = [desde_diccionario(Apoyo, datos) for datos in self._todos("apoyos")]
        if idea is None:
            return registros
        return [apoyo for apoyo in registros if apoyo.idea == idea]

    def ya_apoya(self, idea: str, agente: str) -> bool:
        return self.ruta_apoyo(idea, agente).exists()

    # --- tareas ---

    def guardar_tarea(self, tarea: Tarea) -> Path:
        return self.escribir(self.ruta_tarea(tarea.id), tarea)

    def tareas(self) -> list[Tarea]:
        return [desde_diccionario(Tarea, datos) for datos in self._todos("tareas")]

    def tarea(self, tarea: str) -> Tarea | None:
        datos = self.leer(self.ruta_tarea(tarea))
        return desde_diccionario(Tarea, datos) if datos else None

    def tarea_de_idea(self, idea: str) -> Tarea | None:
        for tarea in self.tareas():
            if tarea.origen == idea:
                return tarea
        return None

    # --- reclamos, entregables y revisiones ---

    def guardar_reclamo(self, reclamo: Reclamo) -> Path:
        return self.escribir(
            self.ruta_reclamo(reclamo.tarea, reclamo.rol, reclamo.agente), reclamo
        )

    def reclamos(self, tarea: str | None = None) -> list[Reclamo]:
        registros = [desde_diccionario(Reclamo, datos) for datos in self._todos("reclamos")]
        if tarea is None:
            return registros
        return [reclamo for reclamo in registros if reclamo.tarea == tarea]

    def guardar_entregable(self, entregable: Entregable) -> Path:
        return self.escribir(
            self.ruta_entregable(entregable.tarea, entregable.rol, entregable.agente), entregable
        )

    def entregables(self, tarea: str | None = None) -> list[Entregable]:
        registros = [
            desde_diccionario(Entregable, datos) for datos in self._todos("entregables")
        ]
        if tarea is None:
            return registros
        return [entregable for entregable in registros if entregable.tarea == tarea]

    def guardar_revision(self, revision: Revision) -> Path:
        return self.escribir(self.ruta_revision(revision.tarea, revision.revisor), revision)

    def revisiones(self, tarea: str | None = None) -> list[Revision]:
        registros = [desde_diccionario(Revision, datos) for datos in self._todos("revisiones")]
        if tarea is None:
            return registros
        return [revision for revision in registros if revision.tarea == tarea]

    # --- la regla que resuelve las carreras ---

    def ganador(self, tarea: str, rol: Any) -> Reclamo | None:
        """Quién cubre un rol, según la regla determinista del protocolo.

        Gana el reclamo más antiguo. Si hay empate exacto de momento, gana el
        identificador de agente más pequeño. Así, dos agentes que reclaman el
        mismo rol al mismo tiempo llegan por separado a la misma conclusión.
        """
        candidatos = [r for r in self.reclamos(tarea) if r.rol == clave(rol)]
        if not candidatos:
            return None
        return min(candidatos, key=lambda reclamo: (reclamo.momento, reclamo.agente))

    def ganadores(self, tarea: str) -> dict[str, str]:
        """Rol a agente, para los roles que ya tienen dueño."""
        resultado: dict[str, str] = {}
        for reclamo in self.reclamos(tarea):
            ganador = self.ganador(tarea, reclamo.rol)
            if ganador is not None:
                resultado[ganador.rol] = ganador.agente
        return resultado

    def rol_ocupado(self, tarea: str, rol: Any) -> bool:
        return self.ganador(tarea, rol) is not None

    def roles_libres(self, tarea: Tarea) -> list[str]:
        return [rol for rol in tarea.requisitos if not self.rol_ocupado(tarea.id, rol)]

    def participa(self, tarea: str, agente: str) -> bool:
        return any(reclamo.agente == agente for reclamo in self.reclamos(tarea))

    def entregado(self, tarea: str, rol: Any, agente: str) -> bool:
        return self.ruta_entregable(tarea, rol, agente).exists()

    # --- estado derivado ---

    def estado(self, tarea: Tarea) -> EstadoTarea:
        """El estado no se guarda: se deduce de los archivos que existen."""
        if self.revisiones(tarea.id):
            return EstadoTarea.CERRADA
        ganadores = self.ganadores(tarea.id)
        if not ganadores:
            return EstadoTarea.ABIERTA
        if all(self.entregado(tarea.id, rol, agente) for rol, agente in ganadores.items()):
            return EstadoTarea.EN_REVISION
        return EstadoTarea.EN_CURSO

    def lista_para_revision(self, tarea: Tarea) -> bool:
        """Hay algo que revisar y todavía nadie lo revisó."""
        if self.revisiones(tarea.id):
            return False
        ganadores = self.ganadores(tarea.id)
        if not ganadores:
            return False
        return all(self.entregado(tarea.id, rol, agente) for rol, agente in ganadores.items())

    def siguiente_id_tarea(self, idea: str) -> str:
        """El identificador de tarea se deriva de la idea, para que promover sea idempotente."""
        return f"t-{idea}"

    def resumen(self) -> str:
        agentes = self.perfiles()
        ideas = self.ideas()
        tareas = self.tareas()
        lineas = [
            f"agentes: {', '.join(perfil.id for perfil in agentes) or 'ninguno'}",
            f"ideas: {len(ideas)}   tareas: {len(tareas)}",
        ]
        for tarea in tareas:
            ganadores = self.ganadores(tarea.id)
            roles = ", ".join(f"{rol}={quien}" for rol, quien in sorted(ganadores.items()))
            lineas.append(
                f"  [{self.estado(tarea).value}] {tarea.titulo} (id {tarea.id}) {roles}"
            )
        return "\n".join(lineas)

    def archivos(self) -> Iterable[Path]:
        if not self.dir.exists():
            return []
        return sorted(self.dir.rglob("*.json"))
