"""Publicar cambios en el repositorio remoto.

Como cada archivo del tablero tiene un único escritor posible, los conflictos
de fusión casi no existen. La única carrera real, dos agentes reclamando el
mismo rol, no se resuelve con git sino con la regla determinista del protocolo,
así que tampoco produce un conflicto.

Este módulo solo trae, confirma y empuja. Nunca reescribe el historial ni
descarta trabajo ajeno.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Resultado:
    ok: bool
    detalle: str


def _git(raiz: Path, *argumentos: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *argumentos],
        cwd=str(raiz),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def es_repositorio(raiz: Path) -> bool:
    return _git(raiz, "rev-parse", "--git-dir").returncode == 0


def tiene_remoto(raiz: Path) -> bool:
    return _git(raiz, "remote").stdout.strip() != ""


def hay_cambios(raiz: Path) -> bool:
    return _git(raiz, "status", "--porcelain").stdout.strip() != ""


def traer(raiz: Path) -> Resultado:
    """Trae lo que publicaron los demás."""
    if not tiene_remoto(raiz):
        return Resultado(True, "sin remoto configurado")
    resultado = _git(raiz, "pull", "--rebase", "--autostash")
    if resultado.returncode != 0:
        _git(raiz, "rebase", "--abort")
        return Resultado(False, f"no se pudo traer: {resultado.stderr.strip()}")
    return Resultado(True, "al día")


def publicar(raiz: Path, mensaje: str) -> Resultado:
    """Confirma los cambios locales y los empuja, reintentando una vez."""
    raiz = Path(raiz)
    if not es_repositorio(raiz):
        return Resultado(False, "la carpeta no es un repositorio git")

    al_dia = traer(raiz)
    if not al_dia.ok:
        return al_dia

    if not hay_cambios(raiz):
        return Resultado(True, "nada que publicar")

    _git(raiz, "add", "-A")
    confirmado = _git(raiz, "commit", "-m", mensaje)
    if confirmado.returncode != 0:
        return Resultado(False, f"no se pudo confirmar: {confirmado.stderr.strip()}")

    if not tiene_remoto(raiz):
        return Resultado(True, "confirmado en local, sin remoto configurado")

    empujado = _git(raiz, "push")
    if empujado.returncode != 0:
        # Alguien publicó antes que nosotros: traemos y reintentamos una vez.
        de_nuevo = traer(raiz)
        if not de_nuevo.ok:
            return de_nuevo
        empujado = _git(raiz, "push")
        if empujado.returncode != 0:
            return Resultado(False, f"no se pudo empujar: {empujado.stderr.strip()}")

    return Resultado(True, "publicado")
