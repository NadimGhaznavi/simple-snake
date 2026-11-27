import json
from pathlib import Path
import tempfile
import unittest

from simplesnake.constants.DText import DText
from simplesnake.interface.Localizer import Localizer


class LocalizationTests(unittest.TestCase):
    def test_english_catalogue_matches_enum(self):
        directory = Path(__file__).resolve().parents[1] / 'simplesnake/locales'
        catalogue = json.loads((directory / 'en.json').read_text())
        self.assertEqual(set(catalogue), set(DText))
        localizer = Localizer(directory)
        self.assertEqual(localizer.select(explicit='unsupported'), 'en')
        self.assertEqual(localizer.text(DText.SCORE, score=4), 'Score: 4')
        with self.assertRaises(KeyError):
            localizer.text('missing.key')

    def test_translation_fallback_precedence_and_sibling_languages(self):
        # Tiny temporary catalogues isolate language matching from bundled translations.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for tag, messages in {
                'en': {'title': 'Hello {name}', 'fallback': 'English'},
                'fr': {'title': 'Bonjour {name}'},
                'zh-TW': {'title': 'TW {name}'},
            }.items():
                (path / f'{tag}.json').write_text(json.dumps(messages))
            localizer = Localizer(path)
            self.assertEqual(localizer.select(explicit='fr-CA', accept_language='en'), 'fr')
            self.assertEqual(localizer.select(accept_language='en;q=0.2,fr;q=0.9'), 'fr')
            self.assertEqual(localizer.select(explicit='zh-CN'), 'en')
            self.assertEqual(localizer.text('fallback', locale='fr'), 'English')
            self.assertEqual(localizer.text('title', locale='fr', name='Ada'), 'Bonjour Ada')
            self.assertEqual(localizer.text('title', locale='en', name='Ada'), 'Hello Ada')

    def test_invalid_translation_placeholders_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'en.json').write_text('{"title": "Hello {name}"}')
            for translation in ('{"title": "Bonjour {other}"}', '{"unknown": "x"}',
                                '{"title": "{name.attribute}"}'):
                (path / 'fr.json').write_text(translation)
                with self.assertRaises(ValueError):
                    Localizer(path)
