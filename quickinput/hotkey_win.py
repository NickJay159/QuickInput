from __future__ import annotations

import ctypes
import logging
import os
import threading
from ctypes import wintypes

from .qt_bootstrap import bootstrap_qt_dlls

bootstrap_qt_dlls()

from PySide6.QtCore import QObject, Signal

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012


def is_hotkey_available(
    modifiers: int,
    virtual_key: int,
    hotkey_id: int = 0x5151,
) -> bool:
    if os.name != "nt":
        return True

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.RegisterHotKey.argtypes = [
        wintypes.HWND,
        ctypes.c_int,
        wintypes.UINT,
        wintypes.UINT,
    ]
    user32.RegisterHotKey.restype = wintypes.BOOL
    user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]

    ctypes.set_last_error(0)
    registered = user32.RegisterHotKey(
        None,
        hotkey_id,
        int(modifiers),
        int(virtual_key),
    )
    if not registered:
        return False

    user32.UnregisterHotKey(None, hotkey_id)
    return True


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


class HotkeyService(QObject):
    activated = Signal()
    registered = Signal()
    failed = Signal(str)

    def __init__(
        self,
        modifiers: int,
        virtual_key: int,
        hotkey_id: int = 1,
        logger: logging.Logger | None = None,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.modifiers = modifiers
        self.virtual_key = virtual_key
        self.hotkey_id = hotkey_id
        self.logger = logger or logging.getLogger(__name__)
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._ready = threading.Event()
        self._running = threading.Event()

    def start(self) -> None:
        if os.name != "nt":
            self.failed.emit("全局热键目前仅支持 Windows。")
            return
        if self._thread and self._thread.is_alive():
            return

        self._running.set()
        self._thread = threading.Thread(target=self._run_message_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()
        if self._thread_id is not None:
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.PostThreadMessageW.argtypes = [
                wintypes.DWORD,
                wintypes.UINT,
                wintypes.WPARAM,
                wintypes.LPARAM,
            ]
            user32.PostThreadMessageW(
                self._thread_id,
                WM_QUIT,
                0,
                0,
            )
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None
        self._thread_id = None

    def _run_message_loop(self) -> None:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        kernel32.GetCurrentThreadId.restype = wintypes.DWORD
        user32.RegisterHotKey.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user32.RegisterHotKey.restype = wintypes.BOOL
        user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.GetMessageW.argtypes = [
            ctypes.POINTER(MSG),
            wintypes.HWND,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user32.GetMessageW.restype = ctypes.c_int
        user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
        user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]

        self._thread_id = int(kernel32.GetCurrentThreadId())
        self._ready.set()

        ctypes.set_last_error(0)
        registered = user32.RegisterHotKey(
            None,
            self.hotkey_id,
            self.modifiers,
            self.virtual_key,
        )
        if not registered:
            error = ctypes.get_last_error()
            message = f"注册全局热键失败，Windows 错误码: {error}"
            self.logger.error(message)
            self.failed.emit(message)
            return

        self.logger.info("全局热键已注册")
        self.registered.emit()

        msg = MSG()
        try:
            while self._running.is_set():
                result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if result == 0:
                    break
                if result == -1:
                    error = ctypes.get_last_error()
                    self.failed.emit(f"热键消息循环失败，Windows 错误码: {error}")
                    break
                if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                    self.activated.emit()
                    continue
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, self.hotkey_id)
            self.logger.info("全局热键已释放")
