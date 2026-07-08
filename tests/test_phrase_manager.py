from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from quickinput.phrase_manager import PhraseManagerDialog
from quickinput.phrase_store import Phrase


class PhraseManagerDialogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_collects_current_editor_values(self) -> None:
        dialog = PhraseManagerDialog([Phrase("1", "Old")])

        dialog.key_edit.setText("2")
        dialog.text_edit.setPlainText("New")

        self.assertEqual(dialog.phrases(), [Phrase("2", "New")])


if __name__ == "__main__":
    unittest.main()
