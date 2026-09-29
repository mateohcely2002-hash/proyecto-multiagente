"""El tablero: un solo escritor por archivo y la regla que resuelve las carreras."""

from multiagente import Entregable, EstadoTarea, Reclamo, Revision, Tablero, Tarea

REQUISITOS = {"ejecutar": "implementacion", "revisar": "revision"}


def _tarea(tablero: Tablero, id: str = "t-1") -> Tarea:
    tarea = Tarea(id=id, titulo="una tarea", requisitos=dict(REQUISITOS))
    tablero.guardar_tarea(tarea)
    return tarea


def test_cada_archivo_tiene_un_solo_escritor_posible(tmp_path) -> None:
    tablero = Tablero(tmp_path)

    ana = tablero.ruta_reclamo("t-1", "ejecutar", "ana")
    bruno = tablero.ruta_reclamo("t-1", "ejecutar", "bruno")

    assert ana != bruno
    assert "ana" in ana.name
    assert "bruno" in bruno.name


def test_dos_reclamos_a_la_vez_los_resuelve_la_regla(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    _tarea(tablero)

    tablero.guardar_reclamo(
        Reclamo(
            tarea="t-1",
            rol="ejecutar",
            agente="zoe",
            puntaje=0.5,
            momento="2026-01-01T00:00:02+00:00",
        )
    )
    tablero.guardar_reclamo(
        Reclamo(
            tarea="t-1",
            rol="ejecutar",
            agente="ana",
            puntaje=0.5,
            momento="2026-01-01T00:00:01+00:00",
        )
    )

    ganador = tablero.ganador("t-1", "ejecutar")
    assert ganador is not None
    assert ganador.agente == "ana"


def test_empate_exacto_lo_decide_el_identificador(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    _tarea(tablero)
    momento = "2026-01-01T00:00:00+00:00"

    for agente in ("zoe", "ana"):
        tablero.guardar_reclamo(
            Reclamo(tarea="t-1", rol="ejecutar", agente=agente, puntaje=0.5, momento=momento)
        )

    ganador = tablero.ganador("t-1", "ejecutar")
    assert ganador is not None
    assert ganador.agente == "ana"


def test_el_estado_no_se_guarda_se_deduce(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    tarea = _tarea(tablero)

    assert tablero.estado(tarea) is EstadoTarea.ABIERTA

    tablero.guardar_reclamo(Reclamo(tarea=tarea.id, rol="ejecutar", agente="ana", puntaje=0.6))
    assert tablero.estado(tarea) is EstadoTarea.EN_CURSO

    tablero.guardar_entregable(
        Entregable(tarea=tarea.id, rol="ejecutar", agente="ana", contenido="listo")
    )
    assert tablero.estado(tarea) is EstadoTarea.EN_REVISION

    tablero.guardar_revision(Revision(tarea=tarea.id, revisor="bruno", puntajes={"ana": 0.8}))
    assert tablero.estado(tarea) is EstadoTarea.CERRADA


def test_promover_una_idea_es_idempotente(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    assert tablero.siguiente_id_tarea("i-abc") == tablero.siguiente_id_tarea("i-abc")


def test_los_roles_libres_son_los_que_nadie_reclamo(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    tarea = _tarea(tablero)

    assert sorted(tablero.roles_libres(tarea)) == ["ejecutar", "revisar"]

    tablero.guardar_reclamo(Reclamo(tarea=tarea.id, rol="ejecutar", agente="ana", puntaje=0.6))
    assert tablero.roles_libres(tarea) == ["revisar"]
