from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from quickinput.i18n import Translator
from quickinput.hotkey_config import MOD_ALT, MOD_CONTROL, MOD_NOREPEAT
from quickinput.phrase_store import Phrase
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

    def test_collects_phrase_edits_inside_settings(self) -> None:
        dialog = SettingsDialog(
            AppSettings(),
            Translator("en_US"),
            [Phrase("1", "Old")],
        )

        dialog.key_edit.setText("2")
        dialog.text_edit.setPlainText("New")

        self.assertEqual(dialog.phrases(), [Phrase("2", "New")])

    def test_updated_settings_include_theme_and_hotkey(self) -> None:
        dialog = SettingsDialog(AppSettings(), Translator("en_US"))
        theme_index = dialog.theme_combo.findData("dark")
        self.assertGreaterEqual(theme_index, 0)

        dialog.theme_combo.setCurrentIndex(theme_index)
        dialog.hotkey_edit.set_hotkey(MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x4B)
        updated = dialog.updated_settings()

        self.assertEqual(updated.ui_theme, "dark")
        self.assertEqual(updated.hotkey_label, "Ctrl+Alt+K")
        self.assertEqual(updated.hotkey_virtual_key, 0x4B)

    def test_conflicting_hotkey_disables_save(self) -> None:
        dialog = SettingsDialog(
            AppSettings(),
            Translator("en_US"),
            hotkey_checker=lambda modifiers, virtual_key: False,
        )

        dialog.hotkey_edit.set_hotkey(MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x4B)

        self.assertFalse(dialog.save_button.isEnabled())
        self.assertEqual(
            dialog.hotkey_status.text(),
            "This hotkey is already used by another app.",
        )


if __name__ == "__main__":
    unittest.main()
