# Hoja de ruta

## Fase 0 — Coordinación (completada)

- [x] Agentes pares, sin orquestador ni jefe
- [x] El repositorio como bodega y punto de encuentro
- [x] Un solo escritor por archivo, sin conflictos de fusión
- [x] Roles que se reparten por capacidad y reputación, no por asignación
- [x] Ideas que se ganan el derecho a ser tareas con el respaldo de otros
- [x] Revisión entre pares, con puntajes firmados
- [x] Reputación que se gana y que pesa más que la destreza declarada
- [x] Pruebas, incluida la red organizándose sola

## Fase 1 — Agentes de verdad (siguiente)

Aquí es donde el sistema deja de ser un esqueleto.

- [ ] Reemplazar `Agente._borrador` por una llamada a un modelo
- [ ] Reemplazar `Agente._puntaje_provisional` por criterios de calidad reales
- [ ] Dar herramientas al agente (leer archivos, buscar, ejecutar código)
- [ ] Decidir qué modelo y con qué presupuesto por tarea

## Fase 2 — Varios agentes en paralelo

- [ ] Un agente por proceso, cada uno con su propio clon del repositorio
- [ ] Ejecución periódica de `rondar` para que ningún agente quede quieto
- [ ] Manejo de agentes que se caen a mitad de un rol
- [ ] Reasignación cuando una revisión sale mal

## Fase 3 — Operación

- [ ] Registro de quién hizo qué y cuánto costó
- [ ] Límite de iteraciones y de gasto por tarea
- [ ] Integración continua que valide el tablero en cada push
- [ ] Panel de lectura que muestre el tablero y la reputación
