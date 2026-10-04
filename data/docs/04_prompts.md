---
title: Prompts para cambios pequeños con IA
source: Guía propia de CursorIA
kind: Guía práctica propia; ejemplos no probados dentro de Cursor
reviewed: 2026-10-04
---
## Pedir un cambio verificable
Una petición útil indica objetivo, archivos relevantes, restricciones y criterio de aceptación. Divide una tarea grande en cambios pequeños. Primero pide que se revise el código existente y se expliquen los archivos afectados. Después solicita un cambio concreto y su verificación.
## Ejemplo Python
Prompt de ejemplo: En el módulo de validación, añade una comprobación para rechazar importes negativos. Conserva la interfaz pública. Explica el cambio y ejecuta las pruebas relacionadas. Si falta información, pregunta antes de asumir requisitos.
## Revisar resultados
Revisa el diff y las pruebas. Solicita una explicación de las decisiones y comprueba los comandos ejecutados. La buena redacción del modelo no demuestra que el código funcione. Conserva en Git un estado conocido antes de cambios importantes.
