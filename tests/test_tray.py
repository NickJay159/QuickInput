from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from quickinput.i18n import Translator
from quickinput.tray import TrayController


class TrayControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_context_menu_uses_settings_as_single_management_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tray = TrayController(Path(tmp) / "missing.png", "Ctrl+[", Translator("en_US"))
            menu = tray.tray.contextMenu()

            texts = [action.text() for action in menu.actions()]

            self.assertIn("Settings", texts)
            self.assertNotIn("Manage Phrases", texts)


if __name__ == "__main__":
    unittest.main()
