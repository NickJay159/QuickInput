from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from quickinput.settings import AppSettings, load_settings, save_settings


class SettingsTest(unittest.TestCase):
    def test_load_settings_creates_default_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.ini"

            settings = load_settings(path)

            self.assertIsInstance(settings, AppSettings)
            self.assertTrue(path.exists())

    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.ini"
            expected = AppSettings(
                popup_width=640,
                popup_height=720,
                ui_language="en_US",
            )

            save_settings(path, expected)
            actual = load_settings(path)

            self.assertEqual(actual.popup_width, 640)
            self.assertEqual(actual.popup_height, 720)
            self.assertEqual(actual.ui_language, "en_US")

    def test_load_settings_normalizes_language_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.ini"
            path.write_text("[ui]\nlanguage = en\n", encoding="utf-8")

            settings = load_settings(path)

            self.assertEqual(settings.ui_language, "en_US")

    def test_load_settings_accepts_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.ini"
            path.write_text("[hotkey]\nlabel = Ctrl+[\n", encoding="utf-8-sig")

            settings = load_settings(path)

            self.assertEqual(settings.hotkey_label, "Ctrl+[")


if __name__ == "__main__":
    unittest.main()
