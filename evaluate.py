"""Evaluate retrieval separately from generation; never fabricate model metrics."""
import argparse
import json
from pathlib import Path
from cursoria.retrieval import load_chunks, lexical_search, semantic_search
from cursoria.generation import Ollama

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--semantic', action='store_true', help='Requiere Ollama y embeddings')
    args = parser.parse_args()
    chunks = load_chunks(ROOT / 'data/docs')
    cases = json.loads((ROOT / 'eval/questions.json').read_text(encoding='utf-8'))
    client = Ollama()
    vectors = client.embed([c.title + '\n' + c.section + '\n' + c.text for c in chunks]) if args.semantic else []
    correct = total = 0
    for case in cases:
        hits = (semantic_search(chunks, vectors, client.embed([case['question']])[0])
                if args.semantic else lexical_search(chunks, case['question']))
        ids = [h.chunk.id for h in hits]
        if case['expected'] is not None:
            ok = any(i.startswith(case['expected'] + ':') for i in ids)
            correct += ok
            total += 1
            print(f"{'OK' if ok else 'FAIL'} | {case['question']} | {ids}")
        else:
            print(f"SIN RESPUESTA ESPERADA | {case['question']} | candidatos: {ids}")
    print(f"{'Semántico' if args.semantic else 'Léxico'}: hit rate@3 = {correct}/{total}")
    print('Los casos sin respuesta requieren revisar abstención y fidelidad con el LLM; no se puntúan aquí.')

if __name__ == '__main__':
    main()
