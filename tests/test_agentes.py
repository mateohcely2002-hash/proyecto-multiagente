"""El comportamiento de la red: agentes pares que se organizan solos."""

from multiagente import UMBRAL_APOYOS, Agente, EstadoTarea, Tablero
from multiagente.reputacion import reputacion_de


def _red(tablero: Tablero) -> list[Agente]:
    definiciones = [
        ("ana", {"analisis": 0.9, "revision": 0.6}, ["medir el consumo"]),
        ("bruno", {"implementacion": 0.9, "revision": 0.5}, ["automatizar el informe"]),
        ("carla", {"datos": 0.9, "revision": 0.9}, ["cruzar las bases"]),
    ]
    agentes = [
        Agente(id, tablero, destrezas=destrezas, temas=temas)
        for id, destrezas, temas in definiciones
    ]
    for agente in agentes:
        agente.publicar_perfil()
    return agentes


def test_nadie_revisa_su_propio_trabajo(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    ana, bruno, carla = _red(tablero)

    idea = ana.proponer_idea("medir el consumo")
    bruno.apoyar_idea(idea.id)
    carla.apoyar_idea(idea.id)
    tarea = bruno.promover_idea(idea.id)
    assert tarea is not None

    bruno.reclamar(tarea.id, "ejecutar", 0.9)
    bruno.entregar(tarea.id)

    assert bruno.puede_revisar(tarea.id) is False
    assert ana.puede_revisar(tarea.id) is True


def test_dos_agentes_no_pueden_tomar_el_mismo_rol(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    ana, bruno, carla = _red(tablero)

    idea = ana.proponer_idea("medir el consumo")
    bruno.apoyar_idea(idea.id)
    carla.apoyar_idea(idea.id)
    tarea = bruno.promover_idea(idea.id)
    assert tarea is not None

    assert bruno.reclamar(tarea.id, "ejecutar", 0.9) is not None
    assert ana.reclamar(tarea.id, "ejecutar", 0.9) is None


def test_una_idea_necesita_respaldo_para_volverse_tarea(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    ana, bruno, carla = _red(tablero)

    idea = ana.proponer_idea("medir el consumo")
    assert bruno.promover_idea(idea.id) is None

    bruno.apoyar_idea(idea.id)
    assert carla.promover_idea(idea.id) is None

    carla.apoyar_idea(idea.id)
    assert len(tablero.apoyos(idea.id)) >= UMBRAL_APOYOS
    assert carla.promover_idea(idea.id) is not None


def test_la_reputacion_solo_se_gana_siendo_evaluado(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    ana, bruno, carla = _red(tablero)

    assert reputacion_de(tablero, "bruno") == {}

    idea = ana.proponer_idea("medir el consumo")
    bruno.apoyar_idea(idea.id)
    carla.apoyar_idea(idea.id)
    tarea = bruno.promover_idea(idea.id)
    assert tarea is not None

    bruno.reclamar(tarea.id, "ejecutar", 0.9)
    bruno.entregar(tarea.id)
    ana.revisar(tarea.id, puntajes={"bruno": 0.95}, comentario="buen trabajo")

    assert reputacion_de(tablero, "bruno") == {"implementacion": 0.95}


def test_la_red_completa_una_tarea_sin_ningun_jefe(tmp_path) -> None:
    tablero = Tablero(tmp_path)
    agentes = _red(tablero)

    for _ in range(12):
        for agente in agentes:
            agente.actuar()

    tareas = tablero.tareas()
    assert tareas, "la red debería haber creado alguna tarea por su cuenta"

    cerradas = [tarea for tarea in tareas if tablero.estado(tarea) is EstadoTarea.CERRADA]
    assert cerradas, "alguna tarea debería haber llegado a cerrarse"

    ganadores = tablero.ganadores(cerradas[0].id)
    assert ganadores
    for agente_id in ganadores.values():
        assert reputacion_de(tablero, agente_id), f"{agente_id} debería tener reputación"
