"""La afinidad entre un agente y un rol de una tarea."""

from multiagente import Agente, Tablero, Tarea, afinidad, mejores_roles
from multiagente.emparejamiento import PESO_DESTREZA, PESO_REPUTACION, REPUTACION_NEUTRA


def test_sin_reputacion_se_usa_un_valor_neutro() -> None:
    esperado = round(PESO_DESTREZA * 1.0 + PESO_REPUTACION * REPUTACION_NEUTRA, 4)
    assert afinidad(1.0, {}, "analisis") == esperado


def test_la_reputacion_pesa_mas_que_la_destreza_declarada() -> None:
    presumido = afinidad(1.0, {"analisis": 0.2}, "analisis")
    cumplidor = afinidad(0.5, {"analisis": 0.9}, "analisis")

    assert cumplidor > presumido


def test_los_roles_ocupados_no_se_ofrecen(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    tarea = Tarea(
        id="t-1",
        titulo="una tarea",
        requisitos={"ejecutar": "implementacion", "revisar": "revision"},
    )
    tablero.guardar_tarea(tarea)

    agente = Agente("ana", tablero, destrezas={"implementacion": 0.9, "revision": 0.9})
    perfil = agente.perfil

    assert [rol for rol, _ in mejores_roles(tablero, perfil, tarea, {})] == ["ejecutar", "revisar"]

    agente.reclamar("t-1", "ejecutar", 0.9)
    assert [rol for rol, _ in mejores_roles(tablero, perfil, tarea, {})] == ["revisar"]
