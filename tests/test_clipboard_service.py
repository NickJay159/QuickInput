from __future__ import annotations

import ctypes
import unittest

from quickinput import clipboard_service


class ClipboardServiceTest(unittest.TestCase):
    def test_windows_input_structure_uses_full_union_size(self) -> None:
        expected_size = 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28

        self.assertEqual(ctypes.sizeof(clipboard_service._INPUT), expected_size)


if __name__ == "__main__":
    unittest.main()
