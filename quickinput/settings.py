from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

from .i18n import DEFAULT_LANGUAGE, normalize_language

MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000
VK_OEM_4 = 0xDB


@dataclass(frozen=True)
class AppSettings:
    hotkey_label: str = "Ctrl+["
    hotkey_modifiers: int = MOD_CONTROL | MOD_NOREPEAT
    hotkey_virtual_key: int = VK_OEM_4
    popup_width: int = 520
    popup_height: int = 560
    paste_delay_ms: int = 120
    clipboard_restore_delay_ms: int = 1000
    ui_language: str = DEFAULT_LANGUAGE


def load_settings(path: Path) -> AppSettings:
    if not path.exists():
        settings = AppSettings()
        save_settings(path, settings)
        return settings

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")

    defaults = AppSettings()
    return AppSettings(
        hotkey_label=parser.get("hotkey", "label", fallback=defaults.hotkey_label),
        hotkey_modifiers=parser.getint(
            "hotkey", "modifiers", fallback=defaults.hotkey_modifiers
        ),
        hotkey_virtual_key=parser.getint(
            "hotkey", "virtual_key", fallback=defaults.hotkey_virtual_key
        ),
        popup_width=max(
            360, parser.getint("popup", "width", fallback=defaults.popup_width)
        ),
        popup_height=max(
            360, parser.getint("popup", "height", fallback=defaults.popup_height)
        ),
        paste_delay_ms=max(
            0, parser.getint("paste", "delay_ms", fallback=defaults.paste_delay_ms)
        ),
        clipboard_restore_delay_ms=max(
            0,
            parser.getint(
                "paste",
                "clipboard_restore_delay_ms",
                fallback=defaults.clipboard_restore_delay_ms,
            ),
        ),
        ui_language=normalize_language(
            parser.get("ui", "language", fallback=defaults.ui_language)
        ),
    )


def save_settings(path: Path, settings: AppSettings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    parser["hotkey"] = {
        "label": settings.hotkey_label,
        "modifiers": str(settings.hotkey_modifiers),
        "virtual_key": str(settings.hotkey_virtual_key),
    }
    parser["popup"] = {
        "width": str(settings.popup_width),
        "height": str(settings.popup_height),
    }
    parser["paste"] = {
        "delay_ms": str(settings.paste_delay_ms),
        "clipboard_restore_delay_ms": str(settings.clipboard_restore_delay_ms),
    }
    parser["ui"] = {
        "language": normalize_language(settings.ui_language),
    }
    with path.open("w", encoding="utf-8") as file:
        parser.write(file)
