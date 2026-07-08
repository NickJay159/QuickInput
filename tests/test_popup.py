from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from quickinput.i18n import Translator
from quickinput.phrase_store import Phrase
from quickinput.popup import PhrasePopup
from quickinput.settings import AppSettings


class PhrasePopupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_uses_english_display_text(self) -> None:
        popup = PhrasePopup(
            [Phrase("1", "Hello")],
            AppSettings(ui_language="en_US"),
            Translator("en_US"),
        )

        self.assertEqual(popup._status_label.text(), "Ready")
        self.assertEqual(popup._count_label.text(), "1 phrases")
        self.assertEqual(
            popup._subtitle_label.text(),
            "Select a phrase to paste at the active cursor",
        )


if __name__ == "__main__":
    unittest.main()
