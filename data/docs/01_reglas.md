---
title: Reglas de proyecto en Cursor
source: https://cursor.com/docs/rules
kind: Resumen propio de documentación oficial
reviewed: 2026-10-04
---
## Configuración de reglas
Las reglas de proyecto se guardan en .cursor/rules mediante archivos .mdc y pueden versionarse con Git. Incluyen contenido y metadatos como description, globs y alwaysApply. Permiten expresar convenciones del proyecto y aplicar instrucciones según su alcance. Un archivo .md en esa carpeta no es una regla .mdc.
## Alternativa sencilla
AGENTS.md permite definir instrucciones en Markdown sin los metadatos de las reglas .mdc. Puede servir para una configuración inicial sencilla. Las reglas aportan contexto al modelo; no sustituyen controles ejecutables, pruebas ni revisión del código.
