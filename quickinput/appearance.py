from __future__ import annotations

DEFAULT_THEME = "system"
SUPPORTED_THEMES = ("system", "light", "dark")


def normalize_theme(value: str | None) -> str:
    if not value:
        return DEFAULT_THEME
    normalized = value.strip().lower()
    aliases = {
        "auto": "system",
        "follow_system": "system",
        "follow-system": "system",
        "default": "system",
        "light": "light",
        "dark": "dark",
    }
    return aliases.get(normalized, normalized if normalized in SUPPORTED_THEMES else DEFAULT_THEME)


def effective_theme(value: str | None) -> str:
    theme = normalize_theme(value)
    if theme != "system":
        return theme

    try:
        from .qt_bootstrap import bootstrap_qt_dlls

        bootstrap_qt_dlls()

        from PySide6.QtCore import Qt
        from PySide6.QtGui import QGuiApplication

        scheme = QGuiApplication.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return "dark"
    except Exception:
        pass

    return "light"


def is_dark_theme(value: str | None) -> bool:
    return effective_theme(value) == "dark"
