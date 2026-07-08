from __future__ import annotations

import logging
import os
import threading
import ctypes
from ctypes import wintypes


class ClipboardService:
    def __init__(
        self,
        restore_delay_ms: int = 1000,
        logger: logging.Logger | None = None,
    ):
        self.restore_delay_ms = restore_delay_ms
        self.logger = logger or logging.getLogger(__name__)

    def paste_text(self, text: str) -> None:
        try:
            import pyperclip
        except ImportError as exc:
            self.logger.error("缺少粘贴依赖: %s", exc)
            raise

        original_text: str | None
        try:
            original_text = pyperclip.paste()
        except Exception as exc:
            self.logger.warning("读取剪贴板失败，将不会恢复原内容: %s", exc)
            original_text = None

        pyperclip.copy(text)
        self._send_ctrl_v()

        if original_text is not None and self.restore_delay_ms > 0:
            timer = threading.Timer(
                self.restore_delay_ms / 1000,
                self._restore_if_unchanged,
                args=(text, original_text),
            )
            timer.daemon = True
            timer.start()

    def _restore_if_unchanged(self, inserted_text: str, original_text: str) -> None:
        try:
            import pyperclip

            if pyperclip.paste() == inserted_text:
                pyperclip.copy(original_text)
        except Exception as exc:
            self.logger.warning("恢复剪贴板失败: %s", exc)

    def _send_ctrl_v(self) -> None:
        if os.name != "nt":
            raise RuntimeError("当前粘贴实现仅支持 Windows")

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.SendInput.argtypes = [
            wintypes.UINT,
            ctypes.POINTER(_INPUT),
            ctypes.c_int,
        ]
        user32.SendInput.restype = wintypes.UINT

        input_events = (_INPUT * 4)(
            _keyboard_input(_VK_CONTROL, 0),
            _keyboard_input(_VK_V, 0),
            _keyboard_input(_VK_V, _KEYEVENTF_KEYUP),
            _keyboard_input(_VK_CONTROL, _KEYEVENTF_KEYUP),
        )
        sent = user32.SendInput(
            len(input_events),
            input_events,
            ctypes.sizeof(_INPUT),
        )
        if sent != len(input_events):
            raise ctypes.WinError(ctypes.get_last_error())


_INPUT_KEYBOARD = 1
_KEYEVENTF_KEYUP = 0x0002
_VK_CONTROL = 0x11
_VK_V = 0x56
_ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ULONG_PTR),
    ]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ULONG_PTR),
    ]


class _HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", _MOUSEINPUT),
        ("ki", _KEYBDINPUT),
        ("hi", _HARDWAREINPUT),
    ]


class _INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUT_UNION),
    ]


def _keyboard_input(virtual_key: int, flags: int) -> _INPUT:
    event = _INPUT()
    event.type = _INPUT_KEYBOARD
    event.union.ki = _KEYBDINPUT(
        wVk=virtual_key,
        wScan=0,
        dwFlags=flags,
        time=0,
        dwExtraInfo=0,
    )
    return event
