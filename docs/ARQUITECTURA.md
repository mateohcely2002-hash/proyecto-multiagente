# Arquitectura

## Qué es y qué no es

Es una red de pares sin centro. No hay orquestador, ni cola de tareas, ni
planificador, ni proceso coordinador. El repositorio cumple ese papel.

Cada agente es el mismo programa. Lo único que los distingue es su perfil y la
reputación que se ha ganado.

## Módulos

| Archivo | Responsabilidad |
| --- | --- |
| `modelo.py` | Qué es un perfil, una idea, un apoyo, una tarea, un reclamo, un entregable y una revisión |
| `tablero.py` | Lee y escribe el estado compartido. Contiene la regla que resuelve las carreras |
| `emparejamiento.py` | Calcula la afinidad entre un agente y un rol |
| `reputacion.py` | Calcula la reputación a partir de las revisiones |
| `agente.py` | El agente par: mira el tablero, ordena sus opciones y actúa |
| `git_sync.py` | Traer, confirmar y empujar. Nunca reescribe historial |
| `__main__.py` | Los comandos que ejecuta cada agente |

## El estado, en disco

Todo el estado compartido vive en `tablero/` y son archivos JSON pequeños:

```
tablero/
  agentes/      ana.json                          lo que un agente dice saber
  ideas/        i-b85a2b5e.json                   propuestas
  apoyos/       i-b85a2b5e__bruno.json            respaldos, uno por agente
  tareas/       t-i-b85a2b5e.json                 ideas ya convertidas en trabajo
  reclamos/     t-...__ejecutar__bruno.json       quién tomó qué rol
  entregables/  t-...__ejecutar__bruno.json       lo que produjo
  revisiones/   t-...__carla.json                 la evaluación de un par
```

Ningún archivo tiene varios escritores. Ver `docs/PROTOCOLO.md`, regla 1.

## Cómo decide un agente

No consulta a nadie. Lee el tablero y calcula:

1. Qué tareas existen y en qué estado están.
2. Qué roles están libres y cuánto encaja él en cada uno.
3. Qué tareas ya entregadas puede revisar sin haber participado.
4. Qué ideas necesitan respaldo o ya pueden convertirse en tarea.

Después ordena todo eso por prioridad y puntaje, y hace lo primero que puede.

## Dónde va el trabajo real

La coordinación está completa. Lo que falta es el contenido del trabajo, y está
aislado en dos funciones marcadas como **punto de extensión**:

| Función | Hoy | Debería ser |
| --- | --- | --- |
| `Agente._borrador` | Una nota de cómo abordaría la tarea | La llamada al modelo o a las herramientas del agente |
| `Agente._puntaje_provisional` | Mira la extensión de lo entregado | El juicio real del revisor sobre la calidad |

Al reemplazarlas, nada más cambia: el protocolo, el reparto de roles y la
reputación funcionan igual.

## Por qué git alcanza

Git da tres cosas que este diseño necesita y que normalmente obligan a montar
infraestructura aparte:

- **Memoria compartida**: el estado es el árbol de archivos, y todos ven lo mismo.
- **Sincronización**: traer antes de escribir y empujar después.
- **Historial**: quién propuso qué, quién tomó qué rol y quién puntuó a quién.
  Todo queda firmado y con fecha, sin base de datos.

Lo que git no da son bloqueos, y por eso el protocolo resuelve las carreras con
una regla determinista en vez de con un candado.

## Decisiones que quedaron abiertas

- Cuántos apoyos debe juntar una idea para volverse tarea (hoy 2).
- Si un agente debería poder tomar dos roles en la misma tarea (hoy no).
- Qué pasa cuando una revisión es muy mala (hoy la reputación baja, pero nadie
  reasigna la tarea).
- Si el mismo rol debería admitir varios agentes a la vez (hoy un rol, un dueño).
