from __future__ import annotations

import unittest

from quickinput.hotkey_config import (
    MOD_ALT,
    MOD_CONTROL,
    MOD_NOREPEAT,
    format_hotkey_label,
    has_required_modifier,
    normalize_hotkey_modifiers,
    same_hotkey,
)


class HotkeyConfigTest(unittest.TestCase):
    def test_formats_display_label_without_norepeat(self) -> None:
        label = format_hotkey_label(MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x4B)

        self.assertEqual(label, "Ctrl+Alt+K")

    def test_normalizes_modifiers_with_norepeat(self) -> None:
        modifiers = normalize_hotkey_modifiers(MOD_CONTROL)

        self.assertEqual(modifiers, MOD_CONTROL | MOD_NOREPEAT)
        self.assertTrue(has_required_modifier(modifiers))

    def test_same_hotkey_ignores_missing_norepeat(self) -> None:
        self.assertTrue(same_hotkey(MOD_CONTROL, 0x4B, MOD_CONTROL | MOD_NOREPEAT, 0x4B))


if __name__ == "__main__":
    unittest.main()
