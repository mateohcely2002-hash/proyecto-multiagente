# proyecto-multiagente

Una red de agentes **pares** que se encuentran en un repositorio de GitHub.
El repositorio no es solo una bodega donde se guarda el código: es también el
punto de encuentro, el tablero donde los agentes se coordinan.

No hay orquestador. No hay jefe. No hay un programa central que reparta tareas.
Cada agente ejecuta el mismo programa, mira el mismo tablero y decide por su
cuenta qué hacer.

## La idea

Cada agente tiene un perfil con lo que sabe hacer. Cuando aparece una tarea, la
tarea no tiene dueño asignado: declara qué roles necesita, y cada agente calcula
por su cuenta qué rol le conviene. El que mejor encaja lo toma.

Los roles no son etiquetas fijas de una persona. El mismo agente puede ejecutar
en una tarea y revisar en otra, según lo que exija cada una y según lo que los
demás opinen de su trabajo.

Esa opinión se acumula. Cuando un agente termina, otro agente que no participó
lo evalúa y deja sus puntajes en el tablero. De ahí sale la **reputación**, que
pesa más que lo que el agente declara saber sobre sí mismo. Nadie puede
regalarse reputación.

## El ciclo

```
   un agente propone una idea
              │
              ▼
   otros agentes la respaldan        (nadie decide: es apoyo, no permiso)
              │
              ▼
   alguien la convierte en tarea     (cuando alcanza los apoyos)
              │
              ▼
   cada rol libre se lo lleva        (destreza declarada + reputación ganada)
   quien mejor encaja
              │
              ▼
   cada uno entrega su parte
              │
              ▼
   un par que no participó revisa    (nadie revisa su propio trabajo)
   y puntúa
              │
              ▼
   esa puntuación se vuelve reputación, que decide los próximos repartos
```

## Verlo funcionar

No hace falta configurar nada. Este comando monta una red de tres agentes en un
tablero temporal y los deja actuar:

```bash
python -m multiagente simular
```

Una salida real, recortada:

```
— ronda 1 —
  ana: propuso la idea i-b85a2b5e: «medir el consumo energético»
  bruno: apoyó la idea i-b85a2b5e
  carla: apoyó la idea i-b85a2b5e
— ronda 2 —
  ana: convirtió en tarea la idea i-b85a2b5e
  bruno: tomar ejecutar en «medir el consumo energético»
  carla: tomar revisar en «medir el consumo energético»
— ronda 4 —
  ana: revisó t-i-b85a2b5e y puntuó a sus pares

  [cerrada] medir el consumo energético (ejecutar=bruno, revisar=carla)

reputación ganada:
  bruno: implementacion=0.82
  carla: revision=0.81
```

Nadie repartió esos roles. Bruno y Carla los tomaron porque eran los que mejor
encajaban, y Ana los evaluó porque no había participado.

## Uso con agentes reales

Cada agente es un proceso independiente que ejecuta estos comandos, todos sobre
el mismo repositorio clonado.

```bash
# cada agente publica su perfil una vez
python -m multiagente perfil --id ana ^
    --destrezas analisis=0.9,redaccion=0.8,revision=0.6 ^
    --temas "medir el consumo,comparar proveedores"

# proponer, respaldar y convertir en tarea
python -m multiagente idea --id ana --titulo "medir el consumo energético"
python -m multiagente apoyar --id bruno --idea i-b85a2b5e
python -m multiagente promover --id carla --idea i-b85a2b5e

# dar un paso por su cuenta: mira el tablero y decide
python -m multiagente rondar --id bruno

# ver el estado y la reputación
python -m multiagente estado
```

Cada comando confirma y empuja al repositorio, así que los demás agentes ven el
cambio en cuanto hacen `rondar`.

## Qué parte es real y qué parte es hueco

Real: la coordinación completa. Cómo se proponen ideas, cómo se ganan apoyos,
cómo se reparten los roles, cómo se resuelven las carreras, cómo se revisan
entre pares y cómo se acumula la reputación. Todo eso funciona y está probado.

Hueco: el contenido del trabajo. Cuando un agente "entrega", hoy escribe una
nota de cómo abordaría la tarea, porque no hay ningún modelo detrás. El punto
donde se conecta un modelo o una herramienta real está señalado en el código
con la etiqueta **punto de extensión**.

## Estructura

```
multiagente/
  modelo.py            qué es un perfil, una idea, una tarea, un reclamo
  tablero.py           el repositorio como memoria compartida
  emparejamiento.py    cómo un agente elige rol según capacidades y reputación
  reputacion.py        cómo se gana y se calcula la reputación
  agente.py            el agente par: mira, decide y actúa
  git_sync.py          traer, confirmar y empujar
  __main__.py          línea de comandos de cada agente
tablero/               el estado compartido: lo que los agentes leen y escriben
tests/                 14 pruebas, incluida la red organizándose sola
docs/PROTOCOLO.md      las reglas de convivencia entre agentes
docs/ARQUITECTURA.md   cómo está construido
docs/ROADMAP.md        qué falta
```

## Pruebas

```bash
python -m pytest
```

## Estado

Funcionando. Sin dueño, sin orquestador, sin coordinador central.
