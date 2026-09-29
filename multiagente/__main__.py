"""Línea de comandos. Cada agente usa el mismo programa.

Desde la raíz del repositorio:

    python -m multiagente perfil --id ana --destrezas analisis=0.9,revision=0.6 ^
        --temas "medir el consumo,comparar proveedores"
    python -m multiagente rondar --id ana
    python -m multiagente estado

El comando ``simular`` monta un tablero de prueba y muestra la red
organizándose sola, sin tocar el repositorio real.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from .agente import Agente
from .reputacion import tabla_reputacion
from .tablero import Tablero


def _configurar_salida() -> None:
    """Escribe en UTF-8 para que los acentos no se rompan al redirigir la salida."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")


def _destrezas(texto: str) -> dict[str, float]:
    resultado: dict[str, float] = {}
    for par in texto.split(","):
        if not par.strip():
            continue
        nombre, _, valor = par.partition("=")
        resultado[nombre.strip()] = float(valor or 0.0)
    return resultado


def _temas(texto: str) -> list[str]:
    return [tema.strip() for tema in texto.split(",") if tema.strip()]


def _agente(tablero: Tablero, id: str, sincronizar: bool) -> Agente | None:
    perfil = tablero.perfil(id)
    if perfil is None:
        return None
    return Agente(
        id,
        tablero,
        destrezas=perfil.destrezas,
        nombre=perfil.nombre,
        temas=perfil.temas,
        sincronizar=sincronizar,
    )


def _mostrar_estado(tablero: Tablero) -> None:
    print(tablero.resumen())
    tabla = tabla_reputacion(tablero)
    con_datos = {agente: valores for agente, valores in tabla.items() if valores}
    if con_datos:
        print()
        print("reputación ganada:")
        for agente, valores in sorted(con_datos.items()):
            detalle = ", ".join(f"{capacidad}={puntaje:.2f}" for capacidad, puntaje in sorted(valores.items()))
            print(f"  {agente}: {detalle}")


def _simular(destino: Path, rondas: int) -> None:
    tablero = Tablero(destino)
    tablero.preparar()

    definiciones = [
        ("ana", "Ana", {"analisis": 0.9, "redaccion": 0.8, "revision": 0.6}, ["medir el consumo energético"]),
        ("bruno", "Bruno", {"implementacion": 0.9, "pruebas": 0.7, "revision": 0.5}, ["automatizar el informe mensual"]),
        ("carla", "Carla", {"datos": 0.9, "analisis": 0.7, "revision": 0.9}, ["cruzar las bases de mantenimiento"]),
    ]
    agentes = [
        Agente(id, tablero, destrezas=destrezas, nombre=nombre, temas=temas)
        for id, nombre, destrezas, temas in definiciones
    ]
    for agente in agentes:
        agente.publicar_perfil()

    print("Tablero de prueba en:", destino)
    print()
    for numero in range(1, rondas + 1):
        print(f"— ronda {numero} —")
        for agente in agentes:
            print(" ", agente.actuar())

    print()
    _mostrar_estado(tablero)


def main(argv: list[str] | None = None) -> int:
    _configurar_salida()
    analizador = argparse.ArgumentParser(prog="multiagente", description="Red de agentes pares sobre un repositorio.")
    analizador.add_argument("--raiz", default=".", help="raíz del repositorio (por defecto, el directorio actual)")
    subcomandos = analizador.add_subparsers(dest="comando", required=True)

    subcomandos.add_parser("estado", help="muestra el tablero y la reputación")

    perfil = subcomandos.add_parser("perfil", help="publica el perfil de un agente")
    perfil.add_argument("--id", required=True)
    perfil.add_argument("--nombre", default="")
    perfil.add_argument("--destrezas", default="")
    perfil.add_argument("--temas", default="")
    perfil.add_argument("--sin-publicar", action="store_true")

    idea = subcomandos.add_parser("idea", help="propone una idea")
    idea.add_argument("--id", required=True)
    idea.add_argument("--titulo", required=True)
    idea.add_argument("--detalle", default="")
    idea.add_argument("--sin-publicar", action="store_true")

    apoyar = subcomandos.add_parser("apoyar", help="respalda la idea de otro")
    apoyar.add_argument("--id", required=True)
    apoyar.add_argument("--idea", required=True)
    apoyar.add_argument("--comentario", default="")
    apoyar.add_argument("--sin-publicar", action="store_true")

    promover = subcomandos.add_parser("promover", help="convierte una idea respaldada en tarea")
    promover.add_argument("--id", required=True)
    promover.add_argument("--idea", required=True)
    promover.add_argument("--sin-publicar", action="store_true")

    rondar = subcomandos.add_parser("rondar", help="el agente da un paso por su cuenta")
    rondar.add_argument("--id", required=True)
    rondar.add_argument("--sin-publicar", action="store_true")

    simular = subcomandos.add_parser("simular", help="monta un tablero de prueba y muestra la red organizándose")
    simular.add_argument("--rondas", type=int, default=10)
    simular.add_argument("--dir", default="")

    argumentos = analizador.parse_args(argv)
    tablero = Tablero(argumentos.raiz)
    publicar = not getattr(argumentos, "sin_publicar", False)

    if argumentos.comando == "simular":
        if argumentos.dir:
            destino = Path(argumentos.dir)
        else:
            destino = Path(tempfile.mkdtemp(prefix="multiagente-"))
        try:
            _simular(destino, argumentos.rondas)
        finally:
            if not argumentos.dir:
                shutil.rmtree(destino, ignore_errors=True)
        return 0

    tablero.preparar()

    if argumentos.comando == "estado":
        _mostrar_estado(tablero)
        return 0

    agente = _agente(tablero, argumentos.id, sincronizar=publicar)
    if argumentos.comando == "perfil":
        agente = Agente(
            argumentos.id,
            tablero,
            destrezas=_destrezas(argumentos.destrezas),
            nombre=argumentos.nombre,
            temas=_temas(argumentos.temas),
            sincronizar=publicar,
        )
        perfil_publicado = agente.publicar_perfil()
        print(f"perfil publicado: {perfil_publicado.id}")
        return 0

    if agente is None:
        print(f"no hay perfil para «{argumentos.id}». Publícalo primero con el comando «perfil».", file=sys.stderr)
        return 1

    if argumentos.comando == "idea":
        nueva = agente.proponer_idea(argumentos.titulo, argumentos.detalle)
        print(f"idea propuesta: {nueva.id} «{nueva.titulo}»")
        return 0

    if argumentos.comando == "apoyar":
        apoyo = agente.apoyar_idea(argumentos.idea, argumentos.comentario)
        print(f"apoyo registrado en {apoyo.idea}" if apoyo else "no se pudo registrar el apoyo")
        return 0 if apoyo else 1

    if argumentos.comando == "promover":
        tarea = agente.promover_idea(argumentos.idea)
        if tarea is None:
            print("la idea no existe, ya es tarea, o no alcanzó los apoyos necesarios", file=sys.stderr)
            return 1
        print(f"tarea creada: {tarea.id} «{tarea.titulo}» con roles {', '.join(sorted(tarea.requisitos))}")
        return 0

    if argumentos.comando == "rondar":
        print(agente.actuar())
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
