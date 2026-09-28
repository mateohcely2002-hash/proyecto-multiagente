# Arquitectura

## Idea central

Tres reglas sostienen el diseño:

1. **Los agentes no se conocen entre sí.** Cada uno implementa `Agent.handle`
   y no importa ni llama a ningún otro agente.
2. **Todo pasa por el orquestador.** Él decide el orden y es el único que sabe
   quién habla con quién.
3. **Todo queda registrado.** Cada mensaje se guarda en el `Context`, así que
   una ejecución se puede auditar después.

Esa separación es lo que permite añadir un agente nuevo sin tocar los
existentes, y lo que hace que el sistema se pueda probar por piezas.

## Flujo

```
usuario ──objetivo──> Orchestrator
                          │
                          ├─> PlannerAgent   : objetivo -> lista de tareas
                          │
                          ├─> WorkerAgent    : tarea -> entregable
                          │
                          └─> ReviewerAgent  : entregable -> aprobado/rechazado
```

Ciclo completo:

1. El orquestador pide el plan al planificador.
2. Para cada tarea, pide el entregable al ejecutor.
3. Pasa el entregable al revisor, que lo aprueba o lo rechaza.

## Piezas

| Archivo | Responsabilidad |
| --- | --- |
| `message.py` | `Message` y `Task`: qué se dicen los agentes y qué trabajo hay |
| `context.py` | `Context`: memoria compartida y transcripción |
| `orchestrator.py` | `Orchestrator` y `RunReport`: el ciclo y su resultado |
| `agents/base.py` | Contrato `Agent` |
| `agents/planner.py` | Descompone el objetivo |
| `agents/worker.py` | Produce el entregable |
| `agents/reviewer.py` | Valida el entregable |

## Puntos de extensión

El esqueleto funciona sin red y sin claves. Para pasar a un sistema real hay
exactamente tres funciones que reemplazar:

| Función | Hoy | Debería ser |
| --- | --- | --- |
| `PlannerAgent.descomponer` | Parte el texto por puntuación | Un plan generado por un modelo |
| `WorkerAgent.ejecutar` | Devuelve un texto de relleno | Herramientas reales o un modelo |
| `ReviewerAgent.aprobado` | Longitud mínima | Criterios de calidad del dominio |

Al cambiarlas, ni el orquestador ni los demás agentes necesitan modificarse.

## Decisiones pendientes

- Dominio del proyecto: qué problema resuelve.
- Si los agentes serán deterministas, basados en un modelo, o mixtos.
- Dónde vive la memoria entre ejecuciones (hoy es solo en memoria).
- Cómo se manejan los reintentos cuando el revisor rechaza una tarea.
