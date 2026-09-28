# Hoja de ruta

## Fase 0 — Base (completada)

- [x] Repositorio en GitHub y control de versiones
- [x] Contrato de agente y memoria compartida
- [x] Orquestador con ciclo planificar -> ejecutar -> revisar
- [x] Pruebas del flujo completo

## Fase 1 — Definición (bloqueante)

Esta fase necesita decisiones que todavía no están tomadas. Sin ellas, el
trabajo siguiente sería adivinar.

- [ ] Definir el dominio: qué problema resuelve el sistema
- [ ] Definir la entrada y la salida esperadas
- [ ] Decidir si los agentes usan un modelo de lenguaje y cuál
- [ ] Definir cómo se mide el éxito

## Fase 2 — Agentes reales

- [ ] Conectar el planificador a un modelo
- [ ] Darle herramientas reales al ejecutor
- [ ] Escribir criterios de revisión del dominio
- [ ] Reintentos cuando una tarea se rechaza

## Fase 3 — Operación

- [ ] Persistir el contexto entre ejecuciones
- [ ] Registro estructurado y trazas
- [ ] Presupuesto de coste y límite de iteraciones
- [ ] Integración continua ejecutando las pruebas en cada push
