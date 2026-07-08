from __future__ import annotations

import importlib.util
import os
from pathlib import Path

_DLL_DIRECTORY_HANDLES = []


def bootstrap_qt_dlls() -> None:
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    package_dirs = []
    for package_name in ("PySide6", "shiboken6"):
        spec = importlib.util.find_spec(package_name)
        if spec and spec.origin:
            package_dirs.append(Path(spec.origin).resolve().parent)

    for path in package_dirs:
        if not path.exists():
            continue
        try:
            handle = os.add_dll_directory(str(path))
            _DLL_DIRECTORY_HANDLES.append(handle)
        except OSError:
            continue
