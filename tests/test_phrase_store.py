from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from quickinput.phrase_store import Phrase, PhraseStore, PhraseStoreError


class PhraseStoreTest(unittest.TestCase):
    def test_loads_valid_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text.csv"
            path.write_text("key,text\n1,Hello\n2,World\n", encoding="utf-8")

            result = PhraseStore(path).load()

        self.assertEqual([phrase.key for phrase in result.phrases], ["1", "2"])
        self.assertEqual([phrase.text for phrase in result.phrases], ["Hello", "World"])
        self.assertEqual(result.warnings, [])

    def test_skips_duplicate_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text.csv"
            path.write_text("key,text\n1,Hello\n1,Again\n", encoding="utf-8")

            result = PhraseStore(path).load()

        self.assertEqual(len(result.phrases), 1)
        self.assertIn("重复", result.warnings[0])

    def test_requires_expected_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text.csv"
            path.write_text("id,value\n1,Hello\n", encoding="utf-8")

            with self.assertRaises(PhraseStoreError):
                PhraseStore(path).load()

    def test_save_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text.csv"

            PhraseStore(path).save(
                [
                    Phrase("1", "Hello"),
                    Phrase("2", "World"),
                ]
            )
            result = PhraseStore(path).load()

        self.assertEqual(result.phrases, [Phrase("1", "Hello"), Phrase("2", "World")])

    def test_save_rejects_duplicate_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text.csv"

            with self.assertRaises(PhraseStoreError):
                PhraseStore(path).save(
                    [
                        Phrase("1", "Hello"),
                        Phrase("1", "World"),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
