import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError
from cursoria.retrieval import load_chunks, lexical_search, semantic_search, cosine
from cursoria.generation import Ollama, ModelError, ABSTENTION

ROOT = Path(__file__).resolve().parents[1]

class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.chunks = load_chunks(ROOT / 'data' / 'docs')

    def test_metadata_and_sections(self):
        self.assertGreater(len(self.chunks), 6)
        self.assertTrue(all(c.source and c.section and c.reviewed for c in self.chunks))
        self.assertEqual(len({c.id for c in self.chunks}), len(self.chunks))

    def test_rules_retrieved(self):
        hits = lexical_search(self.chunks, 'archivos .mdc reglas proyecto')
        self.assertTrue(any(h.chunk.id.startswith('01_reglas') for h in hits))

    def test_no_overlap(self):
        self.assertEqual(lexical_search(self.chunks, 'ornitorrinco submarino'), [])
        self.assertEqual(lexical_search(self.chunks, ''), [])

    def test_semantic_order_and_threshold(self):
        chunks = self.chunks[:2]
        hits = semantic_search(chunks, [[1, 0], [0, 1]], [1, 0], threshold=0.5)
        self.assertEqual([h.chunk.id for h in hits], [chunks[0].id])
        self.assertEqual(cosine([0, 0], [1, 0]), 0)
        with self.assertRaises(ValueError):
            cosine([1], [1, 2])
        with self.assertRaises(ValueError):
            semantic_search(chunks, [[1, 0]], [1, 0])

    def test_invalid_chunk_parameters(self):
        with self.assertRaises(ValueError):
            load_chunks(ROOT / 'data/docs', size=10, overlap=10)

    def test_chunk_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            text = 'abcdefghijklmnopqrstuvwxyz'
            Path(directory, 'doc.md').write_text('---\ntitle: Test\nsource: Own\nkind: Own\nreviewed: 2026-10-04\n---\n## Test\n' + text)
            chunks = load_chunks(Path(directory), size=10, overlap=2)
            rebuilt = chunks[0].text + ''.join(c.text[2:] for c in chunks[1:])
            self.assertEqual(rebuilt, text)

    def test_empty_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                load_chunks(Path(directory))

class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.client = Ollama()
        self.hits = lexical_search(load_chunks(ROOT / 'data/docs'), 'reglas .mdc')

    def response(self, answer):
        return {'message': {'content': json.dumps(answer)}}

    def test_abstain_without_call(self):
        with patch.object(self.client, 'post') as post:
            result = self.client.answer('unknown', [])
            self.assertEqual(result['answer'], ABSTENTION)
            post.assert_not_called()

    def test_valid_citation_and_context(self):
        identifier = self.hits[0].chunk.id
        with patch.object(self.client, 'post', return_value=self.response(
                {'answer': 'Respuesta', 'citations': [identifier], 'supported': True})) as post:
            result = self.client.answer('reglas?', self.hits)
            self.assertTrue(result['supported'])
            payload = post.call_args.args[1]
            self.assertFalse(payload['stream'])
            self.assertIn(identifier, payload['messages'][1]['content'])
            self.assertEqual(payload['format']['type'], 'object')

    def test_invented_citation_rejected(self):
        with patch.object(self.client, 'post', return_value=self.response(
                {'answer': 'Inventada', 'citations': ['fake:1'], 'supported': True})):
            self.assertFalse(self.client.answer('?', self.hits)['supported'])

    def test_invalid_json(self):
        with patch.object(self.client, 'post', return_value={'message': {'content': 'oops'}}):
            with self.assertRaises(ModelError):
                self.client.answer('?', self.hits)

    def test_connection_failure(self):
        with patch('cursoria.generation.urlopen', side_effect=URLError('offline')):
            with self.assertRaises(ModelError):
                self.client.embed(['text'])

    def test_embeddings_contract(self):
        with patch.object(self.client, 'post', return_value={'embeddings': [[1.0, 0.0]]}):
            self.assertEqual(self.client.embed(['text']), [[1.0, 0.0]])
            with self.assertRaises(ModelError):
                self.client.embed(['one', 'two'])

if __name__ == '__main__':
    unittest.main()
