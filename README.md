# CursorIA

Asistente documental sobre **Cursor y programación con IA**. Prototipo RAG local en Python con búsqueda semántica, respuestas estructuradas y referencias a fragmentos del corpus.

## Qué puedes demostrar

- Ingesta de Markdown con metadatos, fragmentación por sección y solapamiento.
- Embeddings con Ollama (`embeddinggemma`) y recuperación por similitud coseno.
- Generación con un LLM local (`llama3.2:3b`), contexto limitado a los documentos y salida JSON con citas.
- Validación de IDs citados, abstención cuando no se recupera contexto y errores comprensibles.
- Interfaz Streamlit y modo de consulta léxica sin modelos.
- Pruebas automatizadas y evaluación reproducible de recuperación.

**Estado:** MVP implementado. Pruebas del núcleo y evaluación léxica ejecutadas. La calidad de embeddings y generación con Ollama debe evaluarse en un equipo con los modelos instalados. No es un agente que ejecute herramientas ni una integración oficial de Cursor.

## Inicio rápido (Windows)

Necesitas Python 3.11 o posterior y Git. Para el RAG completo, instala [Ollama](https://ollama.com/download), mantenlo en ejecución y descarga los modelos. No necesitas una clave API.

```powershell
git clone https://github.com/yassmyss/cursorIA.git
cd cursorIA
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

La interfaz arranca en **Consulta sin modelos**. Ese modo busca palabras y muestra fragmentos; no genera respuestas ni utiliza embeddings.

Para activar **RAG con Ollama**:

```powershell
ollama pull embeddinggemma
ollama pull llama3.2:3b
```

Selecciona el modo RAG en la barra lateral. El primer uso genera el índice en memoria; las consultas posteriores lo reutilizan. La primera descarga requiere Internet. Después, usando modelos locales y la dirección predeterminada, la consulta al corpus no requiere acceso a Internet. La velocidad depende de la RAM, CPU y GPU del equipo.

En Linux/macOS usa `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`.

## Ejemplo de uso

Pregunta: **¿Dónde se guardan las reglas de proyecto .mdc?**

Información esperada: se guardan en `.cursor/rules` y pueden versionarse con Git. La aplicación muestra el fragmento recuperado, su ID, tipo de fuente, fecha de revisión y enlace original. La redacción exacta depende del modelo.

Otras preguntas:

- ¿Los checkpoints sustituyen a Git?
- ¿Cómo pedir un cambio pequeño y verificable?
- ¿Qué información debo aportar para investigar un error?
- ¿Cuál es el precio exacto de Cursor hoy? → No está en el corpus: debe abstenerse. Revisa este comportamiento manualmente.

## Corpus y fuentes

Seis guías en español, revisadas el **4 de octubre de 2026**. Los resúmenes oficiales son paráfrasis propias y no copias completas de páginas. Las recomendaciones originales están identificadas como guías propias; sus prompts no se han probado dentro de Cursor.

| Documento | Origen |
|---|---|
| Reglas | [Cursor: Rules](https://cursor.com/docs/rules) |
| Agent y checkpoints | [Cursor: Agent](https://cursor.com/docs/agent/overview) |
| Búsqueda y contexto | [Cursor: Search](https://cursor.com/docs/agent/tools/search) |
| Prompts, diagnóstico y flujo | Elaboración propia de CursorIA |

Para añadir documentos, crea un `.md` en `data/docs` con esta cabecera y secciones `##`:

```markdown
---
title: Título
source: https://fuente-original.example/documento
kind: Resumen propio de documentación oficial
reviewed: 2026-10-04
---
## Tema
Contenido revisado y redactado con tus palabras.
```

La aplicación recarga el corpus al consultar y reconstruye el índice si cambia el contenido. También puedes usar «Reconstruir índice». No descarga páginas ni actualiza documentación automáticamente.

## Arquitectura y decisiones

Documentos → fragmentos → embeddings → top 3 por coseno → contexto + pregunta → LLM → JSON validado → respuesta y fuentes.

- Índice en memoria: suficiente para un corpus pequeño; no es una base de datos vectorial persistente.
- Cliente HTTP basado en la biblioteca estándar; Streamlit es la única dependencia externa.
- No se añaden LangChain ni LangGraph: el flujo lineal cabe en módulos pequeños y puede explicarse paso a paso.
- Umbral semántico inicial 0.30, configurable y experimental. No representa confianza ni está calibrado con una evaluación semántica.
- El modelo recibe instrucciones de usar exclusivamente el contexto. Se comprueba que las citas existan, pero no se demuestra automáticamente que respalden cada afirmación.

## Estructura

| Ruta | Responsabilidad |
|---|---|
| `app.py` | Interfaz y caché del índice |
| `cursoria/retrieval.py` | Lectura, fragmentación, búsqueda y coseno |
| `cursoria/generation.py` | HTTP Ollama, prompts y validación |
| `data/docs/` | Corpus con fuentes y fecha |
| `tests/test_rag.py` | Contratos y casos de error |
| `eval/questions.json` | Preguntas con documentos esperados |
| `evaluate.py` | Evaluación de recuperación |
| `.github/workflows/tests.yml` | Pruebas en GitHub Actions |

## Pruebas y evaluación

Desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
python evaluate.py
python evaluate.py --semantic
```

Los dos primeros comandos no requieren Ollama ni Streamlit. El tercero requiere Ollama y `embeddinggemma`.

Validación del núcleo: **13 pruebas pasan**. Interfaz comprobada con Streamlit AppTest: inicio, consulta con fuentes, entrada vacía y error controlado sin Ollama. Baseline léxico: **hit rate@3 de 8/8** en ocho preguntas del pequeño conjunto incluido. Esta cifra no mide calidad semántica, generación ni rendimiento en preguntas nuevas. Los dos casos sin respuesta se muestran para revisión manual y no se puntúan como aciertos.

Los tests del cliente usan respuestas simuladas: comprueban contratos, IDs inventados, JSON inválido y fallos de conexión. No sustituyen una prueba de extremo a extremo con un modelo real.

Para evaluar la generación registra, por pregunta: respuesta, citas, si cada afirmación está respaldada y si se abstiene cuando corresponde. Comprueba también la estabilidad ante preguntas que intenten cambiar las instrucciones.

## Configuración opcional

Variables de entorno (la aplicación no lee automáticamente archivos `.env`):

| Variable | Predeterminado |
|---|---|
| `OLLAMA_URL` | `http://localhost:11434` |
| `EMBEDDING_MODEL` | `embeddinggemma` |
| `CHAT_MODEL` | `llama3.2:3b` |

Ejemplo PowerShell: `$env:CHAT_MODEL = "llama3.2:3b"` antes de ejecutar Streamlit. Si configuras un servidor remoto, los fragmentos y preguntas se envían a ese servidor.

## Limitaciones y próximos hitos

- El corpus es pequeño y no cubre precios ni todas las funciones de Cursor. Las guías pueden quedar desactualizadas.
- El modelo puede alucinar incluso con citas válidas. La abstención y las instrucciones contra inyección no son garantías de seguridad.
- No hay PDF, autenticación, carga de documentos por interfaz ni persistencia del índice.
- El código no ejecuta acciones en Cursor ni modifica archivos del proyecto consultado.

Próximos hitos: evaluar RAG real y calibrar umbral; ampliar preguntas con paráfrasis y casos fuera del corpus; persistir el índice con invalidación; añadir PDF y referencias por página solo si aporta valor.

## Para una entrevista

Explica la diferencia entre búsqueda léxica y embeddings; por qué se fragmentan los documentos; cómo se calcula el coseno; por qué una cita válida no garantiza fidelidad; y qué medirías antes de ampliar el sistema. Presenta este proyecto como prototipo educativo, con sus pruebas y límites.
