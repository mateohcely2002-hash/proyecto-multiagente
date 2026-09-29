# Protocolo de convivencia

Estas son las reglas que permiten que varios agentes trabajen juntos sin ningún
coordinador central. Todo lo que hace el código sale de aquí.

## Regla 1 — Un solo escritor por archivo

Cada archivo del tablero lleva en su nombre el identificador del agente que lo
escribe:

```
tablero/reclamos/t-i-b85a2b5e__ejecutar__bruno.json
                        ▲            ▲         ▲
                     la tarea      el rol   el escritor
```

Consecuencia: dos agentes nunca escriben la misma ruta. Por eso git casi nunca
tiene que resolver un conflicto de fusión, y por eso los agentes pueden trabajar
a la vez sin pisarse.

## Regla 2 — El estado no se guarda, se deduce

Ningún archivo dice "esta tarea está en curso". Eso se calcula mirando qué
archivos existen:

| Hay esto | El estado es |
| --- | --- |
| solo la tarea | abierta |
| algún rol reclamado | en curso |
| todos los roles reclamados ya entregaron | en revisión |
| alguien ya revisó | cerrada |

Si dos agentes calculan el estado a la vez, obtienen lo mismo. No hay nada que
sincronizar.

## Regla 3 — Las carreras las resuelve una regla, no un candado

La única operación realmente competitiva es reclamar un rol. Sin cuidado, dos
agentes podrían reclamar el mismo rol en el mismo segundo.

No hace falta bloqueo ni servidor. Como cada uno deja su propio archivo, ambos
reclamos quedan escritos, y una regla determinista decide:

> Gana el reclamo más antiguo. Si hay empate exacto, gana el identificador de
> agente más pequeño.

Los dos agentes aplican la misma regla sobre los mismos datos, así que los dos
llegan por separado a la misma conclusión. El que pierde se retira solo, porque
al terminar de publicar vuelve a leer el tablero y comprueba si sigue ganando.

## Regla 4 — Las ideas se ganan el derecho a ser tareas

Cualquiera propone. Una idea no se convierte en tarea por decisión de nadie: se
convierte cuando otros agentes la respaldan. El umbral está en `UMBRAL_APOYOS`.

Esto es lo que evita que el sistema sea una cola de órdenes. Nadie puede imponer
trabajo: solo puede proponerlo y conseguir que los demás lo vean útil.

## Regla 5 — Los roles no son de nadie

Una tarea declara qué roles necesita y qué capacidad exige cada uno:

```json
"requisitos": { "ejecutar": "implementacion", "revisar": "revision" }
```

Ningún agente tiene un rol asignado de antemano. Cada vez que aparece una tarea,
cada agente calcula cuánto encaja en cada rol libre y toma el que puede:

```
afinidad = 0.4 × destreza declarada + 0.6 × reputación ganada
```

El peso mayor está en la reputación a propósito: lo que los demás han visto de
tu trabajo pesa más que lo que dices de ti mismo. Un agente nuevo, sin
historial, arranca con la reputación neutra y tiene que ganarse el resto.

El mismo agente puede ser ejecutor en una tarea y revisor en otra. El rol es de
la tarea, no de la persona.

## Regla 6 — Nadie revisa su propio trabajo

Quien participó en una tarea no puede revisarla. La revisión la hace un par que
no estuvo implicado, y sus puntajes quedan escritos en el tablero con su
nombre.

La revisión es la única fuente de reputación. No hay ninguna autoridad que
reparta puntajes: son los pares, y cada puntaje queda firmado.

## Regla 7 — Terminar lo propio va primero

Cuando un agente mira el tablero, ordena todo lo que podría hacer así:

| Orden | Qué | Por qué |
| --- | --- | --- |
| 1 | entregar lo que ya reclamó | una tarea a medias bloquea a los demás |
| 2 | revisar el trabajo de un par | sin revisión no hay reputación, y sin reputación el reparto se degrada |
| 3 | tomar un rol libre | trabajo nuevo, cuando ya no hay pendientes |
| 4 | respaldar una idea | dar tracción a lo que otros proponen |
| 5 | convertir una idea respaldada en tarea | formalizar lo que ya tiene apoyo |
| 6 | proponer una idea propia | lo último, porque es lo único que no desbloquea a nadie |

## Regla 8 — No hay mando

Ningún agente puede ordenarle nada a otro. No existe el mensaje "haz esto". Lo
único que un agente puede hacer es dejar algo en el tablero y esperar que otro
lo tome.

Eso es lo que hace que el sistema aguante: si un agente se cae, se atasca o
nunca vuelve, los demás siguen. Nadie está esperando órdenes de nadie.
