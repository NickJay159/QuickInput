from __future__ import annotations

import os
import sys
from pathlib import Path

from . import __app_name__

DEFAULT_TEXT_CSV = """key,text
1,Welcome to our website!
2,Thank you for your visit.
3,Please contact us at: contact@example.com
4,Check out our latest blog post.
5,Subscribe to our newsletter for updates.
6,Learn more about our services here.
7,Follow us on social media.
8,Visit our FAQ page for more information.
9,Click here to see our latest offers.
"""


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def application_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return project_root()


def bundled_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", application_dir())).resolve()


def icon_path() -> Path:
    bundled_icon = bundled_root() / "icon.png"
    if bundled_icon.exists():
        return bundled_icon
    return application_dir() / "icon.png"


def user_data_dir() -> Path:
    override = os.environ.get("QUICKINPUT_DATA_DIR")
    if override:
        path = Path(override)
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        path = base / __app_name__
    else:
        path = Path.home() / f".{__app_name__.lower()}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = user_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def settings_path() -> Path:
    return user_data_dir() / "settings.ini"


def user_phrase_path() -> Path:
    return user_data_dir() / "text.csv"


def ensure_user_phrase_file(target: Path | None = None) -> Path:
    target = target or user_phrase_path()
    if target.exists():
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(DEFAULT_TEXT_CSV, encoding="utf-8", newline="")
    return target
