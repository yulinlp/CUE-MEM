import json
import tempfile
import unittest
from pathlib import Path
from scripts.prepare_dataset import prepare


class DatasetPreparationTests(unittest.TestCase):
    def test_preserves_annotations_and_resolves_media_without_changing_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'dataset'
            source = root / 'data/dialog/base/history_with_qa_p0.json'
            source.parent.mkdir(parents=True)
            media = root / 'data/event/images/example.png'
            media.parent.mkdir(parents=True)
            media.write_bytes(b'fixture')
            original = {'input_image': ['data/event/images/example.png'],
                        'input_voice_message': ['data/event/voice_mixed/missing.wav'],
                        'answer': 'B', 'question': 'Which item?', 'score': 0.8}
            source.write_text(json.dumps(original))
            out = Path(temp) / 'benchmark'
            report = prepare(root, out)
            result = json.loads((out / 'data/dialog/base' / source.name).read_text())
            self.assertEqual(result['input_image'], [str(media)])
            self.assertEqual(result['answer'], 'B')
            self.assertEqual(result['question'], original['question'])
            self.assertEqual(result['score'], original['score'])
            self.assertEqual(json.loads(source.read_text()), original)
            self.assertEqual(report['missing_media'], ['data/event/voice_mixed/missing.wav'])
            with self.assertRaises(ValueError):
                prepare(root, out)
            with self.assertRaises(ValueError):
                prepare(root, root / 'generated')

    def test_rejects_path_outside_dataset(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'dataset'
            source = root / 'data/dialog/base/p0.json'
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps({'input_image': ['data/../../outside.png']}))
            with self.assertRaises(ValueError):
                prepare(root, Path(temp) / 'output')


if __name__ == '__main__':
    unittest.main()
