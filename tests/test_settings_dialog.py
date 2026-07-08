from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from quickinput.i18n import Translator
from quickinput.settings import AppSettings
from quickinput.settings_dialog import SettingsDialog


class SettingsDialogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_returns_selected_language(self) -> None:
        dialog = SettingsDialog(AppSettings(), Translator("zh_CN"))
        index = dialog.language_combo.findData("en_US")

        self.assertGreaterEqual(index, 0)

        dialog.language_combo.setCurrentIndex(index)

        self.assertEqual(dialog.selected_language(), "en_US")


if __name__ == "__main__":
    unittest.main()
