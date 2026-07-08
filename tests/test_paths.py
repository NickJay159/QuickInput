from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quickinput.paths import DEFAULT_TEXT_CSV, ensure_user_phrase_file, user_data_dir


class PathsTest(unittest.TestCase):
    def test_user_data_dir_honors_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"QUICKINPUT_DATA_DIR": tmp}):
                self.assertEqual(user_data_dir(), Path(tmp))

    def test_ensure_user_phrase_file_writes_builtin_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "user" / "text.csv"

            result = ensure_user_phrase_file(target=target)

            self.assertEqual(result, target)
            self.assertEqual(target.read_text(encoding="utf-8"), DEFAULT_TEXT_CSV)


if __name__ == "__main__":
    unittest.main()
