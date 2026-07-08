from __future__ import annotations

from .qt_bootstrap import bootstrap_qt_dlls

bootstrap_qt_dlls()

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .i18n import SUPPORTED_LANGUAGES, Translator, language_name, normalize_language
from .settings import AppSettings


class SettingsDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        translator: Translator,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.translator = translator

        self.language_combo: QComboBox

        self.setWindowTitle(self.translator.t("settings.window_title"))
        self.resize(460, 260)
        self.setMinimumSize(420, 240)
        self.setModal(False)
        self._build_ui()

    def selected_language(self) -> str:
        value = self.language_combo.currentData()
        return normalize_language(str(value) if value is not None else None)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 22)
        root.setSpacing(16)

        title = QLabel(self.translator.t("settings.title"))
        title.setObjectName("dialogTitle")
        subtitle = QLabel(self.translator.t("settings.subtitle"))
        subtitle.setObjectName("dialogSubtitle")

        panel = QFrame()
        panel.setObjectName("settingsPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 14, 16, 14)
        panel_layout.setSpacing(10)

        language_label = QLabel(self.translator.t("settings.language_label"))
        language_label.setObjectName("fieldLabel")
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        for language in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(language_name(language), language)

        selected_index = self.language_combo.findData(
            normalize_language(self.settings.ui_language)
        )
        if selected_index >= 0:
            self.language_combo.setCurrentIndex(selected_index)

        language_hint = QLabel(self.translator.t("settings.language_hint"))
        language_hint.setObjectName("fieldHint")
        language_hint.setWordWrap(True)

        panel_layout.addWidget(language_label)
        panel_layout.addWidget(self.language_combo)
        panel_layout.addWidget(language_hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if save_button:
            save_button.setObjectName("saveButton")
            save_button.setText(self.translator.t("settings.save"))
        if cancel_button:
            cancel_button.setObjectName("cancelButton")
            cancel_button.setText(self.translator.t("settings.cancel"))

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(panel, 1)
        root.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

        self.setStyleSheet(
            """
            QDialog {
                background: #eef3f1;
                color: #172026;
                font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", Arial;
                font-size: 13px;
            }
            QLabel#dialogTitle {
                color: #172026;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#dialogSubtitle,
            QLabel#fieldHint {
                color: #4f5f68;
                font-size: 12px;
            }
            QFrame#settingsPanel {
                background: rgba(255, 255, 255, 222);
                border: 1px solid rgba(34, 51, 59, 31);
                border-radius: 14px;
            }
            QLabel#fieldLabel {
                color: #4f5f68;
                font-size: 12px;
                font-weight: 700;
            }
            QComboBox {
                background: #f8fbfa;
                border: 1px solid rgba(34, 51, 59, 51);
                border-radius: 10px;
                color: #172026;
                min-height: 36px;
                padding: 0 12px;
                outline: 0;
            }
            QComboBox:focus {
                border-color: #0f8f86;
                background: #ffffff;
            }
            QPushButton {
                background: #ffffff;
                border: 1px solid rgba(34, 51, 59, 31);
                border-radius: 9px;
                color: #172026;
                min-height: 32px;
                padding: 0 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #f3fbfa;
                border-color: rgba(15, 143, 134, 92);
            }
            QPushButton#saveButton {
                background: #0f8f86;
                border-color: #0f8f86;
                color: #ffffff;
                font-weight: 800;
            }
            QPushButton#saveButton:hover {
                background: #08746d;
                border-color: #08746d;
            }
            """
        )
