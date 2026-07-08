from __future__ import annotations

import ctypes
import os
from ctypes import wintypes


class SingleInstance:
    def __init__(self, name: str = "QuickInput.SingleInstance"):
        self.name = name
        self._handle: int | None = None

    def acquire(self) -> bool:
        if os.name != "nt":
            return True

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = [
            wintypes.LPVOID,
            wintypes.BOOL,
            wintypes.LPCWSTR,
        ]
        kernel32.CreateMutexW.restype = wintypes.HANDLE

        ctypes.set_last_error(0)
        handle = kernel32.CreateMutexW(None, True, self.name)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())

        if ctypes.get_last_error() == 183:
            kernel32.CloseHandle(handle)
            return False

        self._handle = handle
        return True

    def release(self) -> None:
        if os.name != "nt" or not self._handle:
            return

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.ReleaseMutex(self._handle)
        kernel32.CloseHandle(self._handle)
        self._handle = None
