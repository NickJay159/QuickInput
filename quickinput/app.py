from __future__ import annotations

import logging
import os
import sys
from dataclasses import replace
from pathlib import Path

from .qt_bootstrap import bootstrap_qt_dlls

bootstrap_qt_dlls()

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox, QSystemTrayIcon

from . import __app_name__, __version__
from .clipboard_service import ClipboardService
from .hotkey_win import HotkeyService
from .i18n import Translator
from .logging_setup import configure_logging
from .paths import (
    ensure_user_phrase_file,
    icon_path,
    logs_dir,
    settings_path,
    user_phrase_path,
)
from .phrase_manager import PhraseManagerDialog
from .phrase_store import Phrase, PhraseStore, PhraseStoreError
from .popup import PhrasePopup
from .settings import AppSettings, load_settings
from .settings import save_settings
from .settings_dialog import SettingsDialog
from .single_instance import SingleInstance
from .tray import TrayController


class QuickInputRuntime(QObject):
    def __init__(self, qt_app: QApplication):
        super().__init__()
        self.qt_app = qt_app
        self.logger = logging.getLogger(__name__)
        self.instance = SingleInstance()
        self.settings: AppSettings | None = None
        self.translator = Translator()
        self.phrases: list[Phrase] = []
        self.popup: PhrasePopup | None = None
        self.tray: TrayController | None = None
        self.hotkey: HotkeyService | None = None
        self.clipboard: ClipboardService | None = None
        self.log_file: Path = logs_dir() / "app.log"

    def start(self) -> bool:
        configure_logging(self.log_file)
        self.logger = logging.getLogger(__name__)
        self.settings = load_settings(settings_path())
        self.translator = Translator(self.settings.ui_language)

        if not self.instance.acquire():
            QMessageBox.information(
                None,
                __app_name__,
                self.translator.t("app.already_running"),
            )
            return False

        self.qt_app.setApplicationName(__app_name__)
        self.qt_app.setApplicationVersion(__version__)
        self.qt_app.setOrganizationName(__app_name__)
        self.qt_app.setQuitOnLastWindowClosed(False)

        ensure_user_phrase_file()
        self.phrases = self._load_phrases(show_errors=True)
        self.clipboard = ClipboardService(
            restore_delay_ms=self.settings.clipboard_restore_delay_ms,
            logger=logging.getLogger("quickinput.clipboard"),
        )

        self.popup = PhrasePopup(self.phrases, self.settings, self.translator)
        self.popup.phrase_selected.connect(self._paste_phrase)

        self.tray = TrayController(
            icon_path(),
            self.settings.hotkey_label,
            self.translator,
        )
        self.tray.show_requested.connect(self.show_popup)
        self.tray.manage_requested.connect(self.manage_phrases)
        self.tray.settings_requested.connect(self.configure_settings)
        self.tray.open_log_requested.connect(self.open_log_dir)
        self.tray.quit_requested.connect(self.quit)
        self.tray.show()

        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("当前系统未报告可用系统托盘")

        self.hotkey = HotkeyService(
            modifiers=self.settings.hotkey_modifiers,
            virtual_key=self.settings.hotkey_virtual_key,
            logger=logging.getLogger("quickinput.hotkey"),
        )
        self.hotkey.activated.connect(self.toggle_popup)
        self.hotkey.failed.connect(self._on_hotkey_failed)
        self.hotkey.registered.connect(
            lambda: self.logger.info("热键 %s 可用", self.settings.hotkey_label)
        )
        self.hotkey.start()

        self.logger.info("QuickInput %s 已启动", __version__)
        return True

    def shutdown(self) -> None:
        self.logger.info("QuickInput 正在退出")
        if self.hotkey:
            self.hotkey.stop()
        if self.tray:
            self.tray.hide()
        if self.popup:
            self.popup.hide()
            self.popup.deleteLater()
        self.instance.release()

    def quit(self) -> None:
        self.qt_app.quit()

    def toggle_popup(self) -> None:
        if not self.popup:
            return
        if self.popup.isVisible():
            self.popup.hide()
        else:
            self.show_popup()

    def show_popup(self) -> None:
        if self.popup:
            self.popup.show_centered()

    def reload_phrases(self) -> None:
        self.phrases = self._load_phrases(show_errors=True)
        if self.popup:
            self.popup.set_phrases(self.phrases)
        if self.tray:
            self.tray.show_message(
                "QuickInput",
                self.translator.t("app.loaded_count", count=len(self.phrases)),
            )

    def manage_phrases(self) -> None:
        dialog = PhraseManagerDialog(self.phrases, translator=self.translator)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        phrases = dialog.phrases()
        try:
            PhraseStore(user_phrase_path()).save(phrases)
        except PhraseStoreError as exc:
            self.logger.error("保存文本失败: %s", exc)
            if self.tray:
                self.tray.show_message(
                    "QuickInput",
                    self.translator.t("app.save_failed", error=exc),
                )
            QMessageBox.warning(None, "QuickInput", str(exc))
            return
        except OSError as exc:
            self.logger.error("保存文本失败: %s", exc)
            if self.tray:
                self.tray.show_message(
                    "QuickInput",
                    self.translator.t("app.save_failed", error=exc),
                )
            QMessageBox.warning(
                None,
                "QuickInput",
                self.translator.t("app.save_failed", error=exc),
            )
            return

        self.phrases = phrases
        if self.popup:
            self.popup.set_phrases(self.phrases)
        if self.tray:
            self.tray.show_message(
                "QuickInput",
                self.translator.t("app.saved_count", count=len(self.phrases)),
            )

    def configure_settings(self) -> None:
        if not self.settings:
            return
        dialog = SettingsDialog(self.settings, self.translator)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        updated = replace(self.settings, ui_language=dialog.selected_language())
        save_settings(settings_path(), updated)
        self.settings = updated
        self.translator = Translator(updated.ui_language)
        self._apply_language()
        if self.tray:
            self.tray.show_message("QuickInput", self.translator.t("settings.saved"))

    def open_log_dir(self) -> None:
        self._open_path(logs_dir())

    def _paste_phrase(self, text: str) -> None:
        if not self.settings or not self.clipboard:
            return
        QTimer.singleShot(
            self.settings.paste_delay_ms,
            lambda: self._safe_paste(text),
        )

    def _safe_paste(self, text: str) -> None:
        if not self.clipboard:
            return
        try:
            self.clipboard.paste_text(text)
        except Exception as exc:
            self.logger.error("粘贴文本失败: %s", exc)
            if self.tray:
                self.tray.show_message(
                    "QuickInput",
                    self.translator.t("app.paste_failed", error=exc),
                )

    def _load_phrases(self, show_errors: bool) -> list[Phrase]:
        try:
            result = PhraseStore(user_phrase_path()).load()
        except PhraseStoreError as exc:
            self.logger.error("加载文本失败: %s", exc)
            if show_errors and self.tray:
                self.tray.show_message("QuickInput", str(exc))
            return []

        for warning in result.warnings:
            self.logger.warning(warning)
        if result.warnings and show_errors and self.tray:
            self.tray.show_message("QuickInput", result.warnings[0])
        self.logger.info("已加载 %s 条文本", len(result.phrases))
        return result.phrases

    def _on_hotkey_failed(self, message: str) -> None:
        self.logger.error(message)
        if self.tray:
            self.tray.show_message(
                self.translator.t("app.hotkey_unavailable"),
                message,
            )

    def _apply_language(self) -> None:
        if not self.settings:
            return
        if self.popup:
            self.popup.apply_language(self.translator, self.settings)
        if self.tray:
            self.tray.retranslate(self.translator, self.settings.hotkey_label)

    def _open_path(self, path: Path) -> None:
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                self.logger.info("打开路径: %s", path)
        except Exception as exc:
            self.logger.error("打开路径失败 %s: %s", path, exc)
            if self.tray:
                self.tray.show_message(
                    "QuickInput",
                    self.translator.t("app.open_failed", path=path),
                )


def run(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    smoke_test = "--smoke-test" in argv
    app = QApplication(argv)
    runtime = QuickInputRuntime(app)
    if not runtime.start():
        runtime.shutdown()
        return 1

    if smoke_test:
        QTimer.singleShot(300, app.quit)

    exit_code = app.exec()
    runtime.shutdown()
    return int(exit_code)
