from pathlib import Path
import streamlit as st
from cursoria.retrieval import load_chunks, lexical_search, semantic_search
from cursoria.generation import Ollama, ModelError, ABSTENTION

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='CursorIA', page_icon=None, layout='wide')
st.title('CursorIA')
st.write('Consulta documentación sobre Cursor y programación con IA, con fuentes visibles.')
mode = st.sidebar.radio('Modo', ['Consulta sin modelos', 'RAG con Ollama'])
st.sidebar.caption('Corpus revisado el 04/10/2026. Las funciones de Cursor pueden cambiar.')
threshold = st.sidebar.slider('Umbral de similitud semántica', 0.0, 1.0, 0.30, 0.05)
st.sidebar.caption('Es un filtro experimental, no una probabilidad de respuesta correcta.')

try:
    chunks = load_chunks(ROOT / 'data' / 'docs')
except ValueError as exc:
    st.error(str(exc))
    st.stop()

@st.cache_resource(show_spinner=False)
def build_index(signature, embedding_model, url):
    client = Ollama()
    client.embedding_model, client.url = embedding_model, url
    docs = load_chunks(ROOT / 'data' / 'docs')
    vectors = []
    for start in range(0, len(docs), 16):
        vectors.extend(client.embed([c.title + '\n' + c.section + '\n' + c.text
                                     for c in docs[start:start + 16]]))
    return docs, vectors

st.sidebar.metric('Fragmentos disponibles', len(chunks))
if st.sidebar.button('Reconstruir índice'):
    build_index.clear()

if mode == 'Consulta sin modelos':
    st.info('Búsqueda por palabras: muestra fragmentos originales. Este modo no genera respuestas con IA.')
else:
    st.caption('RAG local: embeddings → similitud coseno → contexto → respuesta de Ollama.')
    st.caption('Las citas identifican fragmentos usados; no garantizan que la respuesta sea correcta.')

with st.form('question'):
    question = st.text_input('Tu pregunta', placeholder='¿Cómo configuro las reglas de mi proyecto?')
    submitted = st.form_submit_button('Consultar', type='primary')

if submitted:
    if not question.strip() or len(question) > 2000:
        st.warning('Escribe una pregunta de entre 1 y 2000 caracteres.')
    else:
        try:
            with st.spinner('Consultando documentos…'):
                answer = None
                if mode == 'Consulta sin modelos':
                    hits = lexical_search(chunks, question)
                else:
                    client = Ollama()
                    signature = tuple((c.id, c.text, c.title, c.section) for c in chunks)
                    indexed, vectors = build_index(signature, client.embedding_model, client.url)
                    query = client.embed([question])[0]
                    hits = semantic_search(indexed, vectors, query, threshold=threshold)
                    answer = client.answer(question, hits)
            if answer:
                st.subheader('Respuesta')
                st.write(answer['answer'])
                if answer['citations']:
                    st.caption('Referencias citadas: ' + ', '.join(answer['citations']))
            if not hits:
                st.warning(ABSTENTION)
            for hit in hits:
                c = hit.chunk
                cited = answer and c.id in answer['citations']
                with st.expander(f'{c.title} · {c.section}' + (' · Citado' if cited else ''), expanded=True):
                    st.text(c.text)
                    st.caption(f'ID: {c.id} · {c.kind} · Revisado: {c.reviewed} · Similitud: {hit.score:.3f}')
                    if c.source.startswith('https://'):
                        st.link_button('Consultar fuente original', c.source)
                    else:
                        st.caption('Fuente: ' + c.source)
        except (ModelError, ValueError) as exc:
            st.error(str(exc))

with st.expander('Ejemplos de preguntas y alcance'):
    st.write('- ¿Dónde se guardan las reglas de proyecto?\n'
             '- ¿Los checkpoints sustituyen a Git?\n'
             '- ¿Cómo pido a la IA un cambio pequeño y verificable?\n'
             '- ¿Cómo investigo un error con Cursor?')
    st.caption('No incluye precios, planes ni todas las funciones. No consulta Internet en tiempo real.')
