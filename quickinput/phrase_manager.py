from __future__ import annotations

from .qt_bootstrap import bootstrap_qt_dlls

bootstrap_qt_dlls()

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .i18n import Translator
from .phrase_store import Phrase, PhraseStoreError, validate_phrases


class PhraseManagerDialog(QDialog):
    def __init__(
        self,
        phrases: list[Phrase],
        parent: QWidget | None = None,
        translator: Translator | None = None,
    ):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setWindowTitle(self.translator.t("manager.window_title"))
        self.resize(860, 560)
        self.setMinimumSize(760, 500)
        self.setModal(False)

        self._phrases: list[Phrase] = list(phrases)
        self._current_index = -1
        self._loading = False
        self._dirty = False

        self.list_widget: QListWidget
        self.key_edit: QLineEdit
        self.text_edit: QTextEdit
        self.delete_button: QPushButton
        self.up_button: QPushButton
        self.down_button: QPushButton
        self.count_label: QLabel

        self._build_ui()
        self._refresh_list()
        if self._phrases:
            self.list_widget.setCurrentRow(0)
        else:
            self._set_editor_enabled(False)

    def phrases(self) -> list[Phrase]:
        self._commit_current()
        return list(self._phrases)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 22)
        root.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(12)

        heading_block = QVBoxLayout()
        heading_block.setSpacing(3)
        heading = QLabel(self.translator.t("manager.title"))
        heading.setObjectName("dialogTitle")
        heading_hint = QLabel(self.translator.t("manager.subtitle"))
        heading_hint.setObjectName("dialogSubtitle")
        heading_block.addWidget(heading)
        heading_block.addWidget(heading_hint)

        self.count_label = QLabel()
        self.count_label.setObjectName("countBadge")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addLayout(heading_block, 1)
        header.addWidget(self.count_label, 0, Qt.AlignmentFlag.AlignTop)

        body = QHBoxLayout()
        body.setSpacing(16)

        left_panel = QFrame()
        left_panel.setObjectName("sidePanel")
        left_panel.setMinimumWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(12)

        title = QLabel(self.translator.t("manager.list_title"))
        title.setObjectName("panelTitle")
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("phraseList")
        self.list_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.list_widget.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.list_widget.currentRowChanged.connect(self._on_current_row_changed)

        add_button = QPushButton(self.translator.t("manager.add"))
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(self._add_phrase)
        self.delete_button = QPushButton(self.translator.t("manager.delete"))
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self._delete_phrase)
        self.up_button = QPushButton(self.translator.t("manager.up"))
        self.up_button.setObjectName("secondaryButton")
        self.up_button.clicked.connect(lambda: self._move_current(-1))
        self.down_button = QPushButton(self.translator.t("manager.down"))
        self.down_button.setObjectName("secondaryButton")
        self.down_button.clicked.connect(lambda: self._move_current(1))

        row_buttons = QHBoxLayout()
        row_buttons.setSpacing(8)
        row_buttons.addWidget(add_button)
        row_buttons.addWidget(self.delete_button)
        row_buttons.addWidget(self.up_button)
        row_buttons.addWidget(self.down_button)

        left_layout.addWidget(title)
        left_layout.addWidget(self.list_widget, 1)
        left_layout.addLayout(row_buttons)

        right_panel = QFrame()
        right_panel.setObjectName("editPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 14, 16, 14)
        right_layout.setSpacing(12)

        editor_title = QLabel(self.translator.t("manager.edit_title"))
        editor_title.setObjectName("panelTitle")
        editor_hint = QLabel(self.translator.t("manager.edit_hint"))
        editor_hint.setObjectName("panelHint")

        key_label = QLabel(self.translator.t("manager.key_label"))
        key_label.setObjectName("fieldLabel")
        self.key_edit = QLineEdit()
        self.key_edit.setObjectName("keyInput")
        self.key_edit.setMaxLength(8)
        self.key_edit.setPlaceholderText(self.translator.t("manager.key_placeholder"))
        self.key_edit.textEdited.connect(self._mark_dirty)

        text_label = QLabel(self.translator.t("manager.text_label"))
        text_label.setObjectName("fieldLabel")
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("textEditor")
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setPlaceholderText(self.translator.t("manager.text_placeholder"))
        self.text_edit.textChanged.connect(self._mark_dirty)
        self.text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_save)
        buttons.rejected.connect(self.reject)
        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if save_button:
            save_button.setObjectName("saveButton")
            save_button.setText(self.translator.t("manager.save"))
        if cancel_button:
            cancel_button.setObjectName("cancelButton")
            cancel_button.setText(self.translator.t("manager.cancel"))

        right_layout.addWidget(editor_title)
        right_layout.addWidget(editor_hint)
        right_layout.addWidget(key_label)
        right_layout.addWidget(self.key_edit)
        right_layout.addWidget(text_label)
        right_layout.addWidget(self.text_edit, 1)
        right_layout.addWidget(buttons)

        body.addWidget(left_panel, 0)
        body.addWidget(right_panel, 1)

        root.addLayout(header)
        root.addLayout(body, 1)

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
            QLabel#dialogSubtitle, QLabel#panelHint {
                color: #4f5f68;
                font-size: 12px;
            }
            QLabel#countBadge {
                background: #172026;
                color: #ffffff;
                border-radius: 10px;
                font-weight: 800;
                padding: 8px 12px;
            }
            QFrame#sidePanel,
            QFrame#editPanel {
                background: rgba(255, 255, 255, 222);
                border: 1px solid rgba(34, 51, 59, 31);
                border-radius: 14px;
            }
            QLabel#panelTitle {
                color: #172026;
                font-size: 16px;
                font-weight: 800;
            }
            QLabel#fieldLabel {
                color: #4f5f68;
                font-size: 12px;
                font-weight: 700;
            }
            QListWidget#phraseList,
            QLineEdit,
            QTextEdit {
                background: #f8fbfa;
                border: 1px solid rgba(34, 51, 59, 51);
                border-radius: 10px;
                color: #172026;
                selection-background-color: #0f8f86;
                selection-color: #ffffff;
                outline: 0;
            }
            QLineEdit:focus,
            QTextEdit:focus,
            QListWidget#phraseList:focus {
                border-color: #0f8f86;
                background: #ffffff;
            }
            QListWidget#phraseList::item {
                padding: 10px 9px;
                border-radius: 9px;
                margin: 3px;
                color: #4f5f68;
                outline: 0;
            }
            QListWidget#phraseList::item:selected {
                background: #ffffff;
                color: #172026;
                border-left: 4px solid #0f8f86;
                border-top: 1px solid rgba(15, 143, 134, 92);
                border-right: 1px solid rgba(15, 143, 134, 92);
                border-bottom: 1px solid rgba(15, 143, 134, 92);
            }
            QListWidget#phraseList::item:hover {
                background: #f3fbfa;
            }
            QPushButton {
                background: #ffffff;
                border: 1px solid rgba(34, 51, 59, 31);
                border-radius: 9px;
                color: #172026;
                min-height: 32px;
                padding: 0 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #f3fbfa;
                border-color: rgba(15, 143, 134, 92);
            }
            QPushButton:disabled {
                color: #a5afb6;
                background: #eef3f1;
                border-color: rgba(34, 51, 59, 20);
            }
            QPushButton#primaryButton,
            QPushButton#saveButton {
                background: #0f8f86;
                border-color: #0f8f86;
                color: #ffffff;
                font-weight: 800;
            }
            QPushButton#primaryButton:hover,
            QPushButton#saveButton:hover {
                background: #08746d;
                border-color: #08746d;
            }
            QPushButton#dangerButton {
                color: #c45548;
            }
            QPushButton#dangerButton:hover {
                background: #fff0ed;
                border-color: rgba(196, 85, 72, 92);
            }
            QScrollBar:vertical {
                background: transparent;
                width: 5px;
                margin: 4px 0 4px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(23, 32, 38, 42);
                border-radius: 2px;
                min-height: 28px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(15, 143, 134, 92);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                height: 0;
            }
            """
        )

    def _refresh_list(self, select_row: int | None = None) -> None:
        self._loading = True
        self.list_widget.clear()
        for phrase in self._phrases:
            item = QListWidgetItem(self._format_list_item(phrase))
            self.list_widget.addItem(item)
        self._loading = False
        self.count_label.setText(
            self.translator.t("manager.count", count=len(self._phrases))
        )

        if select_row is not None and self._phrases:
            self.list_widget.setCurrentRow(max(0, min(select_row, len(self._phrases) - 1)))
        self._update_buttons()

    def _format_list_item(self, phrase: Phrase) -> str:
        preview = " ".join(phrase.text.split())
        if len(preview) > 26:
            preview = f"{preview[:26]}..."
        return f"{phrase.key}  {preview}"

    def _on_current_row_changed(self, row: int) -> None:
        if self._loading:
            return
        self._commit_current()
        self._current_index = row
        self._load_editor(row)
        self._update_buttons()

    def _load_editor(self, row: int) -> None:
        self._loading = True
        if 0 <= row < len(self._phrases):
            phrase = self._phrases[row]
            self._set_editor_enabled(True)
            self.key_edit.setText(phrase.key)
            self.text_edit.setPlainText(phrase.text)
        else:
            self._set_editor_enabled(False)
            self.key_edit.clear()
            self.text_edit.clear()
        self._loading = False

    def _commit_current(self) -> None:
        if self._loading:
            return
        index = self._current_index
        if not (0 <= index < len(self._phrases)):
            return
        self._phrases[index] = Phrase(
            key=self.key_edit.text(),
            text=self.text_edit.toPlainText(),
        )
        item = self.list_widget.item(index)
        if item:
            item.setText(self._format_list_item(self._phrases[index]))

    def _add_phrase(self) -> None:
        self._commit_current()
        key = self._next_key()
        self._phrases.append(Phrase(key=key, text=""))
        self._dirty = True
        self._refresh_list(select_row=len(self._phrases) - 1)
        self.text_edit.setFocus(Qt.FocusReason.OtherFocusReason)

    def _delete_phrase(self) -> None:
        row = self.list_widget.currentRow()
        if not (0 <= row < len(self._phrases)):
            return
        del self._phrases[row]
        self._dirty = True
        self._current_index = -1
        self._refresh_list(select_row=min(row, len(self._phrases) - 1))
        if not self._phrases:
            self._load_editor(-1)

    def _move_current(self, offset: int) -> None:
        self._commit_current()
        row = self.list_widget.currentRow()
        target = row + offset
        if not (0 <= row < len(self._phrases)) or not (0 <= target < len(self._phrases)):
            return
        self._phrases[row], self._phrases[target] = self._phrases[target], self._phrases[row]
        self._dirty = True
        self._current_index = -1
        self._refresh_list(select_row=target)

    def _next_key(self) -> str:
        used = {phrase.key.strip() for phrase in self._phrases}
        for index in range(1, 10):
            key = str(index)
            if key not in used:
                return key
        return ""

    def _mark_dirty(self) -> None:
        if not self._loading:
            self._dirty = True

    def _set_editor_enabled(self, enabled: bool) -> None:
        self.key_edit.setEnabled(enabled)
        self.text_edit.setEnabled(enabled)

    def _update_buttons(self) -> None:
        row = self.list_widget.currentRow()
        has_row = 0 <= row < len(self._phrases)
        self.delete_button.setEnabled(has_row)
        self.up_button.setEnabled(has_row and row > 0)
        self.down_button.setEnabled(has_row and row < len(self._phrases) - 1)

    def _accept_save(self) -> None:
        self._commit_current()
        try:
            self._phrases = validate_phrases(self._phrases)
        except PhraseStoreError as exc:
            QMessageBox.warning(self, self.translator.t("manager.cannot_save"), str(exc))
            return
        self._dirty = False
        self.accept()

    def reject(self) -> None:
        if self._confirm_discard():
            super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()

    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        result = QMessageBox.question(
            self,
            self.translator.t("manager.discard_title"),
            self.translator.t("manager.discard_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes
