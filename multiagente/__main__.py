"""Interfaz de línea de comandos: python -m multiagente "objetivo"."""

from __future__ import annotations

import sys

from .orchestrator import Orchestrator

OBJETIVO_POR_DEFECTO = (
    "definir el alcance del proyecto; construir el orquestador; escribir las pruebas"
)


def main(argv: list[str] | None = None) -> int:
    argumentos = list(sys.argv[1:] if argv is None else argv)
    objetivo = " ".join(argumentos) if argumentos else OBJETIVO_POR_DEFECTO

    report = Orchestrator().run(objetivo)

    print(report.resumen())
    print()
    print("transcripcion:")
    for mensaje in report.transcript:
        print(f"  {mensaje.sender} -> {mensaje.recipient} [{mensaje.role.value}]: {mensaje.content}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
