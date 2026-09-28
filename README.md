# proyecto-multiagente

Sistema multiagente mínimo: un **orquestador** que coordina agentes especializados
(planificador, ejecutor y revisor) sobre una memoria compartida.

El repositorio arranca con un esqueleto que **funciona sin claves de API**, para
que el flujo completo se pueda ejecutar y probar desde el primer commit. Cada
agente tiene un único punto de extensión donde se conecta un modelo de lenguaje
o una herramienta real.

## Estado

Borrador inicial. El dominio del proyecto (qué problema resuelve el sistema)
está **pendiente de definir**; ver `docs/ROADMAP.md`.

## Estructura

```
multiagente/
  message.py         Mensajes y tareas que circulan entre agentes
  context.py         Memoria compartida (blackboard)
  orchestrator.py    Coordina el ciclo planificar -> ejecutar -> revisar
  agents/
    base.py          Contrato mínimo de un agente
    planner.py       Descompone el objetivo en tareas
    worker.py        Ejecuta cada tarea
    reviewer.py      Valida el entregable
tests/               Pruebas del flujo completo
docs/                Arquitectura y hoja de ruta
```

## Uso

Requiere Python 3.10 o superior.

```bash
python -m multiagente "analizar los datos; generar el informe; revisar el informe"
```

Sin argumentos usa un objetivo de ejemplo.

## Pruebas

```bash
python -m pytest
```

## Cómo convertirlo en un sistema real

Los tres puntos de extensión son:

1. `PlannerAgent.descomponer` — hoy parte el objetivo por puntuación.
2. `WorkerAgent.ejecutar` — hoy genera un texto de relleno.
3. `ReviewerAgent.aprobado` — hoy comprueba una longitud mínima.

Al reemplazarlos por llamadas a un modelo, el resto del sistema no cambia.

## Licencia

Pendiente de definir.
