from __future__ import annotations

from pathlib import Path

from .qt_bootstrap import bootstrap_qt_dlls

bootstrap_qt_dlls()

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from .i18n import Translator


class TrayController(QObject):
    show_requested = Signal()
    settings_requested = Signal()
    open_log_requested = Signal()
    quit_requested = Signal()

    def __init__(
        self,
        icon_path: Path,
        hotkey_label: str,
        translator: Translator,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.hotkey_label = hotkey_label
        self.translator = translator
        self.icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
        self.tray = QSystemTrayIcon(self.icon, self)
        self._build_menu()
        self.tray.activated.connect(self._on_activated)

    def retranslate(self, translator: Translator, hotkey_label: str) -> None:
        self.translator = translator
        self.hotkey_label = hotkey_label
        self._build_menu()

    def _build_menu(self) -> None:
        menu = QMenu()
        self.tray.setToolTip(f"QuickInput - {self.hotkey_label}")

        title = QAction("QuickInput", menu)
        title.setEnabled(False)
        hotkey = QAction(
            self.translator.t("tray.hotkey", hotkey=self.hotkey_label),
            menu,
        )
        hotkey.setEnabled(False)

        show_action = QAction(self.translator.t("tray.show_window"), menu)
        show_action.triggered.connect(self.show_requested.emit)
        settings_action = QAction(self.translator.t("tray.settings"), menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        open_log_action = QAction(self.translator.t("tray.open_logs"), menu)
        open_log_action.triggered.connect(self.open_log_requested.emit)
        quit_action = QAction(self.translator.t("tray.quit"), menu)
        quit_action.triggered.connect(self.quit_requested.emit)

        menu.addAction(title)
        menu.addAction(hotkey)
        menu.addSeparator()
        menu.addAction(show_action)
        menu.addAction(settings_action)
        menu.addAction(open_log_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)

    def show(self) -> None:
        self.tray.show()

    def hide(self) -> None:
        self.tray.hide()

    def show_message(self, title: str, message: str) -> None:
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                4000,
            )

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_requested.emit()
