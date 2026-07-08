from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

from .appearance import DEFAULT_THEME, normalize_theme
from .hotkey_config import (
    DEFAULT_HOTKEY_LABEL,
    DEFAULT_HOTKEY_MODIFIERS,
    DEFAULT_HOTKEY_VIRTUAL_KEY,
    format_hotkey_label,
    normalize_hotkey_modifiers,
)
from .i18n import DEFAULT_LANGUAGE, normalize_language


@dataclass(frozen=True)
class AppSettings:
    hotkey_label: str = DEFAULT_HOTKEY_LABEL
    hotkey_modifiers: int = DEFAULT_HOTKEY_MODIFIERS
    hotkey_virtual_key: int = DEFAULT_HOTKEY_VIRTUAL_KEY
    popup_width: int = 520
    popup_height: int = 560
    paste_delay_ms: int = 120
    clipboard_restore_delay_ms: int = 1000
    ui_language: str = DEFAULT_LANGUAGE
    ui_theme: str = DEFAULT_THEME


def load_settings(path: Path) -> AppSettings:
    if not path.exists():
        settings = AppSettings()
        save_settings(path, settings)
        return settings

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8-sig")

    defaults = AppSettings()
    hotkey_modifiers = normalize_hotkey_modifiers(
        parser.getint(
            "hotkey", "modifiers", fallback=defaults.hotkey_modifiers
        )
    )
    hotkey_virtual_key = parser.getint(
        "hotkey", "virtual_key", fallback=defaults.hotkey_virtual_key
    )
    return AppSettings(
        hotkey_label=format_hotkey_label(hotkey_modifiers, hotkey_virtual_key),
        hotkey_modifiers=hotkey_modifiers,
        hotkey_virtual_key=hotkey_virtual_key,
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
        ui_theme=normalize_theme(parser.get("ui", "theme", fallback=defaults.ui_theme)),
    )


def save_settings(path: Path, settings: AppSettings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    parser["hotkey"] = {
        "label": format_hotkey_label(
            settings.hotkey_modifiers,
            settings.hotkey_virtual_key,
        ),
        "modifiers": str(normalize_hotkey_modifiers(settings.hotkey_modifiers)),
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
        "theme": normalize_theme(settings.ui_theme),
    }
    with path.open("w", encoding="utf-8") as file:
        parser.write(file)
