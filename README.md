# CursorIA

CursorIA es una aplicación en Python para consultar documentación sobre Cursor y programación con inteligencia artificial. Utiliza un sistema RAG (generación aumentada por recuperación) que busca información en los documentos disponibles y la incorpora al contexto del modelo para elaborar una respuesta.

Cada consulta permite revisar los fragmentos recuperados, su procedencia y la fecha de revisión. La aplicación incluye documentación resumida de fuentes oficiales y guías prácticas sobre prompts, diagnóstico de errores y organización del trabajo con IA.

## Funcionalidades

- Lectura de documentos Markdown con metadatos de origen y fecha.
- División del contenido en fragmentos por sección.
- Búsqueda semántica mediante embeddings y similitud coseno.
- Generación de respuestas con un modelo local a través de Ollama.
- Respuestas estructuradas y comprobación de las referencias citadas.
- Consulta por palabras sin necesidad de instalar modelos.
- Interfaz web con Streamlit.

## Requisitos

- Python 3.11 o posterior.
- Git, para clonar el repositorio.
- [Ollama](https://ollama.com/download), para utilizar la búsqueda semántica y la generación de respuestas.

El modo de consulta por palabras funciona sin Ollama. Para utilizar el RAG completo es necesario descargar los modelos y mantener Ollama en ejecución.

## Instalación

### Windows

Desde PowerShell:

```powershell
git clone https://github.com/yassmyss/cursorIA.git
cd cursorIA
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Linux y macOS

```bash
git clone https://github.com/yassmyss/cursorIA.git
cd cursorIA
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### Modelos de Ollama

Para utilizar el RAG:

```bash
ollama pull embeddinggemma
ollama pull llama3.2:3b
```

La descarga inicial requiere conexión a Internet. Con los modelos instalados y Ollama ejecutándose en el equipo, las consultas se procesan localmente. El tiempo de respuesta depende de los recursos disponibles.

## Ejecución

En Windows:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

En Linux y macOS:

```bash
.venv/bin/python -m streamlit run app.py
```

Abre en el navegador la dirección que muestra Streamlit en la terminal.

## Uso

La barra lateral permite seleccionar dos modos:

| Modo | Funcionamiento |
|---|---|
| Consulta sin modelos | Busca coincidencias por palabras y muestra los fragmentos encontrados. |
| RAG con Ollama | Busca por similitud semántica y utiliza los fragmentos recuperados para generar una respuesta. |

Escribe una pregunta y pulsa **Consultar**. Por ejemplo:

> ¿Dónde se guardan las reglas de proyecto .mdc?

La información disponible indica que se guardan en `.cursor/rules` y pueden versionarse con Git. Junto al resultado se muestran los fragmentos, sus identificadores y el enlace a la fuente original cuando está disponible.

Otras consultas:

- ¿Los checkpoints sustituyen a Git?
- ¿Cómo pedir un cambio pequeño y verificable?
- ¿Qué información debo aportar para investigar un error?
- ¿Cómo organizar el inicio de un proyecto con IA?

En el modo RAG, el índice se genera en la primera consulta y se reutiliza durante la sesión. Si cambian los documentos, se reconstruye. También puede renovarse mediante **Reconstruir índice**.

El umbral de similitud se puede ajustar desde la barra lateral. Su valor inicial es `0.30`; es un filtro experimental y no representa la probabilidad de que una respuesta sea correcta.

## Documentación incluida

El repositorio contiene seis guías en español, revisadas el **4 de octubre de 2026**.

| Contenido | Fuente |
|---|---|
| Reglas de proyecto | [Cursor: Rules](https://cursor.com/docs/rules) |
| Agent y checkpoints | [Cursor: Agent](https://cursor.com/docs/agent/overview) |
| Búsqueda de código y contexto | [Cursor: Search](https://cursor.com/docs/agent/tools/search) |
| Prompts para cambios pequeños | Guía práctica del proyecto |
| Diagnóstico de errores | Guía práctica del proyecto |
| Flujo de trabajo y documentación | Guía práctica del proyecto |

Los documentos basados en fuentes oficiales son resúmenes, no reproducciones completas. Las guías prácticas están identificadas como contenido propio del proyecto. Los ejemplos de prompts no se han comprobado dentro de Cursor.

### Añadir documentos

Crea un archivo `.md` en `data/docs/` con los siguientes metadatos:

```markdown
---
title: Título del documento
source: https://cursor.com/docs/rules
kind: Resumen propio de documentación oficial
reviewed: 2026-10-04
---
## Nombre de la sección
Contenido del documento.
```

Los campos `title`, `source`, `kind` y `reviewed` son obligatorios. Las secciones se delimitan con encabezados `##`.

La incorporación y revisión de documentos es manual. La aplicación no descarga páginas ni actualiza las fuentes automáticamente.

## Funcionamiento técnico

El proceso de consulta sigue estos pasos:

1. Leer los documentos y sus metadatos.
2. Dividir el contenido por secciones en fragmentos de hasta 900 caracteres, con un solapamiento de 120.
3. Generar embeddings con `embeddinggemma`.
4. Comparar el embedding de la pregunta con los de los documentos mediante similitud coseno.
5. Seleccionar hasta tres fragmentos que superen el umbral configurado.
6. Enviar la pregunta y los fragmentos a `llama3.2:3b`.
7. Validar la respuesta JSON y los identificadores de las referencias.

El índice se mantiene en memoria. El cliente de Ollama utiliza la biblioteca estándar de Python para las peticiones HTTP; Streamlit es la única dependencia externa declarada.

Si no se recuperan fragmentos, la aplicación devuelve un mensaje de información insuficiente sin consultar al modelo generativo. Si el modelo indica que no hay información suficiente, omite las citas o cita identificadores inexistentes, también se devuelve ese mensaje.

La validación comprueba que las referencias correspondan a los fragmentos enviados. No comprueba automáticamente que cada afirmación de la respuesta esté respaldada por ellos.

## Estructura del proyecto

| Ruta | Contenido |
|---|---|
| `app.py` | Interfaz y gestión del índice en caché |
| `cursoria/retrieval.py` | Lectura, fragmentación y búsqueda |
| `cursoria/generation.py` | Cliente de Ollama y validación de respuestas |
| `data/docs/` | Documentos y metadatos |
| `tests/test_rag.py` | Pruebas del núcleo de la aplicación |
| `eval/questions.json` | Preguntas y documentos de referencia |
| `eval/smoke_ui.py` | Comprobación básica de la interfaz |
| `evaluate.py` | Evaluación de la recuperación |
| `requirements.txt` | Dependencias |
| `.github/workflows/tests.yml` | Ejecución de pruebas en GitHub Actions |

## Configuración

La aplicación admite estas variables de entorno:

| Variable | Valor predeterminado |
|---|---|
| `OLLAMA_URL` | `http://localhost:11434` |
| `EMBEDDING_MODEL` | `embeddinggemma` |
| `CHAT_MODEL` | `llama3.2:3b` |

Ejemplo en PowerShell, antes de ejecutar la aplicación:

```powershell
$env:CHAT_MODEL = "llama3.2:3b"
```

Los archivos `.env` no se cargan automáticamente. Si se configura una dirección remota para Ollama, las preguntas y los fragmentos se enviarán a ese servidor.

## Pruebas y evaluación

Ejecuta los comandos desde la raíz del repositorio, con el Python del entorno virtual. En Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe eval/smoke_ui.py
.\.venv\Scripts\python.exe evaluate.py
.\.venv\Scripts\python.exe evaluate.py --semantic
```

En Linux y macOS, sustituye `.\.venv\Scripts\python.exe` por `.venv/bin/python`.

Las pruebas del núcleo y la evaluación por palabras no requieren Ollama. La comprobación de la interfaz requiere Streamlit. La evaluación semántica requiere Ollama y el modelo de embeddings.

### Comprobaciones realizadas

- 13 pruebas del núcleo superadas.
- Interfaz comprobada: inicio, consulta con fuentes y validación de preguntas vacías.
- Gestión del error de conexión comprobada con Ollama no disponible.
- Recuperación por palabras: documento esperado entre los tres primeros resultados en las ocho preguntas con fuente de referencia.

Los tests del cliente utilizan respuestas simuladas para comprobar errores de conexión, formato JSON y referencias inválidas. La ejecución con modelos reales y la calidad de las respuestas generadas están pendientes de validación.

El conjunto de evaluación incluye dos preguntas sin respuesta en los documentos. Se muestran para revisar el comportamiento de abstención, pero no se contabilizan en la métrica de recuperación. Los resultados del conjunto incluido no permiten concluir cómo se comportará la aplicación ante preguntas nuevas.

## Limitaciones

- La documentación disponible cubre un conjunto reducido de temas y puede quedar desactualizada.
- No se incluye información sobre precios ni todas las funciones de Cursor.
- El modelo puede generar respuestas incorrectas aunque las referencias sean válidas.
- El índice no se conserva entre reinicios.
- Solo se admiten documentos Markdown.
- No hay autenticación ni carga de archivos desde la interfaz.
- La aplicación consulta documentación; no ejecuta acciones en Cursor.

## Mejoras previstas

- Evaluar la recuperación semántica y la fidelidad de las respuestas con modelos reales.
- Ajustar el umbral a partir de los resultados de evaluación.
- Ampliar los casos de prueba con preguntas reformuladas y fuera del alcance de los documentos.
- Incorporar persistencia del índice y control de cambios en los documentos.
- Añadir soporte para PDF con referencias por página.
