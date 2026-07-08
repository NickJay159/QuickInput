from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from .qt_bootstrap import bootstrap_qt_dlls

bootstrap_qt_dlls()

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal  # noqa: E402
from PySide6.QtGui import QColor, QCloseEvent, QKeyEvent, QPainter, QPen  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .appearance import SUPPORTED_THEMES, effective_theme, normalize_theme
from .hotkey_config import (
    DEFAULT_HOTKEY_MODIFIERS,
    DEFAULT_HOTKEY_VIRTUAL_KEY,
    MOD_ALT,
    MOD_CONTROL,
    MOD_NOREPEAT,
    MOD_SHIFT,
    MOD_WIN,
    format_hotkey_label,
    has_required_modifier,
    normalize_hotkey_modifiers,
    same_hotkey,
)
from .hotkey_win import is_hotkey_available
from .i18n import SUPPORTED_LANGUAGES, Translator, language_name, normalize_language
from .phrase_store import Phrase, PhraseStoreError, validate_phrases
from .settings import AppSettings


_MODIFIER_KEYS = {
    int(Qt.Key.Key_Control),
    int(Qt.Key.Key_Shift),
    int(Qt.Key.Key_Alt),
    int(Qt.Key.Key_Meta),
}

_QT_KEY_TO_VK = {
    int(Qt.Key.Key_Escape): 0x1B,
    int(Qt.Key.Key_Tab): 0x09,
    int(Qt.Key.Key_Backspace): 0x08,
    int(Qt.Key.Key_Return): 0x0D,
    int(Qt.Key.Key_Enter): 0x0D,
    int(Qt.Key.Key_Insert): 0x2D,
    int(Qt.Key.Key_Delete): 0x2E,
    int(Qt.Key.Key_Pause): 0x13,
    int(Qt.Key.Key_Print): 0x2C,
    int(Qt.Key.Key_Home): 0x24,
    int(Qt.Key.Key_End): 0x23,
    int(Qt.Key.Key_Left): 0x25,
    int(Qt.Key.Key_Up): 0x26,
    int(Qt.Key.Key_Right): 0x27,
    int(Qt.Key.Key_Down): 0x28,
    int(Qt.Key.Key_PageUp): 0x21,
    int(Qt.Key.Key_PageDown): 0x22,
    int(Qt.Key.Key_Space): 0x20,
    int(Qt.Key.Key_Semicolon): 0xBA,
    int(Qt.Key.Key_Equal): 0xBB,
    int(Qt.Key.Key_Comma): 0xBC,
    int(Qt.Key.Key_Minus): 0xBD,
    int(Qt.Key.Key_Period): 0xBE,
    int(Qt.Key.Key_Slash): 0xBF,
    int(Qt.Key.Key_QuoteLeft): 0xC0,
    int(Qt.Key.Key_BracketLeft): 0xDB,
    int(Qt.Key.Key_Backslash): 0xDC,
    int(Qt.Key.Key_BracketRight): 0xDD,
    int(Qt.Key.Key_Apostrophe): 0xDE,
}


def _virtual_key_from_event(event: QKeyEvent) -> int:
    native_virtual_key = int(event.nativeVirtualKey() or 0)
    if native_virtual_key:
        return native_virtual_key

    key = int(event.key())
    if int(Qt.Key.Key_0) <= key <= int(Qt.Key.Key_9):
        return 0x30 + key - int(Qt.Key.Key_0)
    if int(Qt.Key.Key_A) <= key <= int(Qt.Key.Key_Z):
        return 0x41 + key - int(Qt.Key.Key_A)
    if int(Qt.Key.Key_F1) <= key <= int(Qt.Key.Key_F24):
        return 0x70 + key - int(Qt.Key.Key_F1)
    return _QT_KEY_TO_VK.get(key, 0)


def _modifiers_from_event(event: QKeyEvent) -> int:
    qt_modifiers = event.modifiers()
    modifiers = 0
    if qt_modifiers & Qt.KeyboardModifier.ControlModifier:
        modifiers |= MOD_CONTROL
    if qt_modifiers & Qt.KeyboardModifier.AltModifier:
        modifiers |= MOD_ALT
    if qt_modifiers & Qt.KeyboardModifier.ShiftModifier:
        modifiers |= MOD_SHIFT
    if qt_modifiers & Qt.KeyboardModifier.MetaModifier:
        modifiers |= MOD_WIN
    return normalize_hotkey_modifiers(modifiers)


class SettingsComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._dark = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setMinimumHeight(38)

    def set_dark(self, dark: bool) -> None:
        self._dark = dark
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        hint = super().sizeHint()
        hint.setHeight(max(hint.height(), 38))
        return hint

    def enterEvent(self, event) -> None:  # noqa: N802
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self.update()
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:  # noqa: N802
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:  # noqa: N802
        self.update()
        super().focusOutEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        enabled = self.isEnabled()
        focused = self.hasFocus()
        hovered = self.underMouse()

        if self._dark:
            colors = {
                "disabled_background": "#1b2226",
                "disabled_border": QColor(255, 255, 255, 20),
                "disabled_text": "#758187",
                "background": "#171f23",
                "active_background": "#1d282c",
                "border": QColor(255, 255, 255, 34),
                "hover_border": QColor(38, 184, 173, 112),
                "focus_border": "#26b8ad",
                "text": "#edf3f1",
                "arrow": "#b4c0c4",
            }
        else:
            colors = {
                "disabled_background": "#eef3f1",
                "disabled_border": QColor(34, 51, 59, 24),
                "disabled_text": "#8b969b",
                "background": "#f8fbfa",
                "active_background": "#ffffff",
                "border": QColor(34, 51, 59, 51),
                "hover_border": QColor(15, 143, 134, 92),
                "focus_border": "#0f8f86",
                "text": "#172026",
                "arrow": "#52646d",
            }

        if not enabled:
            background = QColor(colors["disabled_background"])
            border = colors["disabled_border"]
            text = QColor(colors["disabled_text"])
            arrow = QColor(colors["disabled_text"])
        else:
            background = QColor(
                colors["active_background"] if focused or hovered else colors["background"]
            )
            border = (
                QColor(colors["focus_border"])
                if focused
                else colors["hover_border"]
                if hovered
                else colors["border"]
            )
            text = QColor(colors["text"])
            arrow = QColor(colors["arrow"])

        control_rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.setBrush(background)
        painter.setPen(QPen(border, 1.0))
        painter.drawRoundedRect(control_rect, 10, 10)

        text_rect = self.rect().adjusted(12, 0, -42, 0)
        label = painter.fontMetrics().elidedText(
            self.currentText(),
            Qt.TextElideMode.ElideRight,
            text_rect.width(),
        )
        painter.setPen(text)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            label,
        )

        center_x = self.width() - 21
        center_y = self.height() / 2 + 1
        chevron_pen = QPen(arrow, 1.8)
        chevron_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        chevron_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(chevron_pen)
        painter.drawLine(
            QPointF(center_x - 4, center_y - 2),
            QPointF(center_x, center_y + 2),
        )
        painter.drawLine(
            QPointF(center_x, center_y + 2),
            QPointF(center_x + 4, center_y - 2),
        )


class HotkeyCaptureEdit(QLineEdit):
    hotkey_changed = Signal(int, int, str)

    def __init__(
        self,
        modifiers: int,
        virtual_key: int,
        translator: Translator,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._modifiers = DEFAULT_HOTKEY_MODIFIERS
        self._virtual_key = DEFAULT_HOTKEY_VIRTUAL_KEY
        self.translator = translator
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setPlaceholderText(self.translator.t("settings.hotkey_placeholder"))
        self.set_hotkey(modifiers, virtual_key)

    def hotkey(self) -> tuple[int, int]:
        return self._modifiers, self._virtual_key

    def set_hotkey(self, modifiers: int, virtual_key: int) -> None:
        self._modifiers = normalize_hotkey_modifiers(modifiers)
        self._virtual_key = int(virtual_key)
        label = format_hotkey_label(self._modifiers, self._virtual_key)
        self.setText(label)
        self.hotkey_changed.emit(self._modifiers, self._virtual_key, label)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if int(event.key()) in _MODIFIER_KEYS:
            event.accept()
            return

        virtual_key = _virtual_key_from_event(event)
        if not virtual_key:
            event.ignore()
            return

        modifiers = _modifiers_from_event(event)
        self.set_hotkey(modifiers, virtual_key)
        event.accept()


class SettingsDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        translator: Translator,
        phrases: list[Phrase] | None = None,
        parent: QWidget | None = None,
        initial_tab: str = "preferences",
        hotkey_checker: Callable[[int, int], bool] | None = None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.translator = translator
        self._phrases: list[Phrase] = list(phrases or [])
        self._current_index = -1
        self._loading = False
        self._dirty = False
        self._hotkey_checker = hotkey_checker or is_hotkey_available
        self._hotkey_ok = True
        self._initial_tab = initial_tab

        self.language_combo: SettingsComboBox
        self.theme_combo: SettingsComboBox
        self.hotkey_edit: HotkeyCaptureEdit
        self.hotkey_status: QLabel
        self.tabs: QTabWidget
        self.list_widget: QListWidget
        self.key_edit: QLineEdit
        self.text_edit: QTextEdit
        self.delete_button: QPushButton
        self.up_button: QPushButton
        self.down_button: QPushButton
        self.count_label: QLabel
        self.save_button: QPushButton | None = None

        self.setWindowTitle(self.translator.t("settings.window_title"))
        self.resize(780, 580)
        self.setMinimumSize(720, 520)
        self.setModal(False)
        self._build_ui()
        self._apply_style()
        self._refresh_hotkey_status()

    def selected_language(self) -> str:
        value = self.language_combo.currentData()
        return normalize_language(str(value) if value is not None else None)

    def selected_theme(self) -> str:
        value = self.theme_combo.currentData()
        return normalize_theme(str(value) if value is not None else None)

    def hotkey_settings(self) -> tuple[str, int, int]:
        modifiers, virtual_key = self.hotkey_edit.hotkey()
        label = format_hotkey_label(modifiers, virtual_key)
        return label, modifiers, virtual_key

    def updated_settings(self) -> AppSettings:
        label, modifiers, virtual_key = self.hotkey_settings()
        return replace(
            self.settings,
            hotkey_label=label,
            hotkey_modifiers=modifiers,
            hotkey_virtual_key=virtual_key,
            ui_language=self.selected_language(),
            ui_theme=self.selected_theme(),
        )

    def phrases(self) -> list[Phrase]:
        self._commit_current()
        return list(self._phrases)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 22)
        root.setSpacing(16)

        title = QLabel(self.translator.t("settings.title"))
        title.setObjectName("dialogTitle")
        subtitle = QLabel(self.translator.t("settings.subtitle"))
        subtitle.setObjectName("dialogSubtitle")

        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")
        self.tabs.addTab(self._build_preferences_tab(), self.translator.t("settings.preferences_tab"))
        self.tabs.addTab(self._build_phrases_tab(), self.translator.t("settings.phrases_tab"))
        if self._initial_tab == "phrases":
            self.tabs.setCurrentIndex(1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_save)
        buttons.rejected.connect(self.reject)
        self.save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if self.save_button:
            self.save_button.setObjectName("saveButton")
            self.save_button.setText(self.translator.t("settings.save"))
        if cancel_button:
            cancel_button.setObjectName("cancelButton")
            cancel_button.setText(self.translator.t("settings.cancel"))

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(self.tabs, 1)
        root.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

    def _build_preferences_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(14)

        panel = QFrame()
        panel.setObjectName("settingsPanel")
        panel_layout = QGridLayout(panel)
        panel_layout.setContentsMargins(16, 14, 16, 16)
        panel_layout.setHorizontalSpacing(14)
        panel_layout.setVerticalSpacing(10)
        panel_layout.setColumnStretch(1, 1)

        panel_title = QLabel(self.translator.t("settings.preferences_title"))
        panel_title.setObjectName("panelTitle")
        panel_layout.addWidget(panel_title, 0, 0, 1, 2)

        self.language_combo = SettingsComboBox()
        self.language_combo.setObjectName("languageCombo")
        for language in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(language_name(language), language)
        language_index = self.language_combo.findData(
            normalize_language(self.settings.ui_language)
        )
        if language_index >= 0:
            self.language_combo.setCurrentIndex(language_index)
        self._add_field(
            panel_layout,
            1,
            self.translator.t("settings.language_label"),
            self.language_combo,
            self.translator.t("settings.language_hint"),
        )

        self.theme_combo = SettingsComboBox()
        self.theme_combo.setObjectName("themeCombo")
        for theme in SUPPORTED_THEMES:
            self.theme_combo.addItem(
                self.translator.t(f"settings.theme_{theme}"),
                theme,
            )
        theme_index = self.theme_combo.findData(normalize_theme(self.settings.ui_theme))
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self._add_field(
            panel_layout,
            3,
            self.translator.t("settings.theme_label"),
            self.theme_combo,
            self.translator.t("settings.theme_hint"),
        )

        self.hotkey_edit = HotkeyCaptureEdit(
            self.settings.hotkey_modifiers,
            self.settings.hotkey_virtual_key,
            self.translator,
        )
        self.hotkey_edit.setObjectName("hotkeyEdit")
        self.hotkey_edit.hotkey_changed.connect(self._refresh_hotkey_status)
        reset_button = QPushButton(self.translator.t("settings.hotkey_reset"))
        reset_button.setObjectName("secondaryButton")
        reset_button.clicked.connect(
            lambda: self.hotkey_edit.set_hotkey(
                DEFAULT_HOTKEY_MODIFIERS,
                DEFAULT_HOTKEY_VIRTUAL_KEY,
            )
        )
        hotkey_row = QHBoxLayout()
        hotkey_row.setSpacing(8)
        hotkey_row.addWidget(self.hotkey_edit, 1)
        hotkey_row.addWidget(reset_button)

        hotkey_container = QWidget()
        hotkey_container.setLayout(hotkey_row)
        self._add_field(
            panel_layout,
            5,
            self.translator.t("settings.hotkey_label"),
            hotkey_container,
            self.translator.t("settings.hotkey_hint"),
        )

        self.hotkey_status = QLabel()
        self.hotkey_status.setObjectName("hotkeyStatus")
        panel_layout.addWidget(self.hotkey_status, 7, 1)

        layout.addWidget(panel)
        layout.addStretch(1)
        return page

    def _build_phrases_tab(self) -> QWidget:
        page = QWidget()
        body = QHBoxLayout(page)
        body.setContentsMargins(0, 12, 0, 0)
        body.setSpacing(14)

        left_panel = QFrame()
        left_panel.setObjectName("sidePanel")
        left_panel.setMinimumWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(12)

        heading = QHBoxLayout()
        heading.setSpacing(8)
        list_title = QLabel(self.translator.t("manager.list_title"))
        list_title.setObjectName("panelTitle")
        self.count_label = QLabel()
        self.count_label.setObjectName("countBadge")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.addWidget(list_title, 1)
        heading.addWidget(self.count_label)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("phraseList")
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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

        left_layout.addLayout(heading)
        left_layout.addWidget(self.list_widget, 1)
        left_layout.addLayout(row_buttons)

        right_panel = QFrame()
        right_panel.setObjectName("editPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 14, 16, 14)
        right_layout.setSpacing(12)

        editor_title = QLabel(self.translator.t("settings.phrases_title"))
        editor_title.setObjectName("panelTitle")
        editor_hint = QLabel(self.translator.t("settings.phrases_hint"))
        editor_hint.setObjectName("fieldHint")

        key_label = QLabel(self.translator.t("manager.key_label"))
        key_label.setObjectName("fieldLabel")
        self.key_edit = QLineEdit()
        self.key_edit.setObjectName("keyInput")
        self.key_edit.setMaxLength(8)
        self.key_edit.setPlaceholderText(self.translator.t("manager.key_placeholder"))
        self.key_edit.textChanged.connect(self._mark_dirty)

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

        right_layout.addWidget(editor_title)
        right_layout.addWidget(editor_hint)
        right_layout.addWidget(key_label)
        right_layout.addWidget(self.key_edit)
        right_layout.addWidget(text_label)
        right_layout.addWidget(self.text_edit, 1)

        body.addWidget(left_panel, 0)
        body.addWidget(right_panel, 1)

        self._refresh_list()
        if self._phrases:
            self.list_widget.setCurrentRow(0)
        else:
            self._set_editor_enabled(False)
        return page

    def _add_field(
        self,
        layout: QGridLayout,
        row: int,
        label_text: str,
        widget: QWidget,
        hint_text: str,
    ) -> None:
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        hint = QLabel(hint_text)
        hint.setObjectName("fieldHint")
        hint.setWordWrap(True)

        layout.addWidget(label, row, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(widget, row, 1)
        layout.addWidget(hint, row + 1, 1)

    def _on_theme_changed(self) -> None:
        self._apply_style()

    def _refresh_hotkey_status(self, *args: object) -> None:
        modifiers, virtual_key = self.hotkey_edit.hotkey()
        if not has_required_modifier(modifiers) or not virtual_key:
            text_key = "settings.hotkey_invalid"
            status = "error"
            self._hotkey_ok = False
        elif same_hotkey(
            modifiers,
            virtual_key,
            self.settings.hotkey_modifiers,
            self.settings.hotkey_virtual_key,
        ):
            text_key = "settings.hotkey_current"
            status = "ok"
            self._hotkey_ok = True
        else:
            try:
                available = self._hotkey_checker(modifiers, virtual_key)
            except Exception:
                available = False
            text_key = "settings.hotkey_available" if available else "settings.hotkey_conflict"
            status = "ok" if available else "error"
            self._hotkey_ok = available

        self.hotkey_status.setText(self.translator.t(text_key))
        self.hotkey_status.setProperty("status", status)
        self.hotkey_status.style().unpolish(self.hotkey_status)
        self.hotkey_status.style().polish(self.hotkey_status)
        self.hotkey_status.update()
        if self.save_button:
            self.save_button.setEnabled(self._hotkey_ok)

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

        self._refresh_hotkey_status()
        if not self._hotkey_ok:
            QMessageBox.warning(
                self,
                self.translator.t("app.hotkey_unavailable"),
                self.hotkey_status.text(),
            )
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

    def _apply_style(self) -> None:
        dark = effective_theme(self.selected_theme()) == "dark"
        for combo in (getattr(self, "language_combo", None), getattr(self, "theme_combo", None)):
            if combo is not None:
                combo.set_dark(dark)

        if dark:
            colors = {
                "window": "#14191c",
                "surface": "#20272b",
                "surface_alt": "#182024",
                "control": "#171f23",
                "control_hover": "#1d282c",
                "text": "#edf3f1",
                "muted": "#a8b4b9",
                "soft": "#88c9c3",
                "accent": "#26b8ad",
                "accent_hover": "#1da196",
                "danger": "#ff8d7d",
                "danger_bg": "#3b2220",
                "border": "rgba(255, 255, 255, 34)",
                "border_soft": "rgba(255, 255, 255, 22)",
                "selection": "#123f3d",
                "button": "#20272b",
                "button_hover": "#253136",
                "tab": "#1b2226",
                "tab_selected": "#20272b",
                "scroll": "rgba(255, 255, 255, 44)",
            }
        else:
            colors = {
                "window": "#eef3f1",
                "surface": "rgba(255, 255, 255, 222)",
                "surface_alt": "#f8fbfa",
                "control": "#f8fbfa",
                "control_hover": "#ffffff",
                "text": "#172026",
                "muted": "#4f5f68",
                "soft": "#08746d",
                "accent": "#0f8f86",
                "accent_hover": "#08746d",
                "danger": "#c45548",
                "danger_bg": "#fff0ed",
                "border": "rgba(34, 51, 59, 31)",
                "border_soft": "rgba(34, 51, 59, 51)",
                "selection": "#e1f5f2",
                "button": "#ffffff",
                "button_hover": "#f3fbfa",
                "tab": "#e4ece9",
                "tab_selected": "#ffffff",
                "scroll": "rgba(23, 32, 38, 42)",
            }

        self.setStyleSheet(
            f"""
            QDialog {{
                background: {colors["window"]};
                color: {colors["text"]};
                font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", Arial;
                font-size: 13px;
            }}
            QLabel#dialogTitle {{
                color: {colors["text"]};
                font-size: 24px;
                font-weight: 800;
            }}
            QLabel#dialogSubtitle,
            QLabel#fieldHint {{
                color: {colors["muted"]};
                font-size: 12px;
            }}
            QLabel#panelTitle {{
                color: {colors["text"]};
                font-size: 16px;
                font-weight: 800;
            }}
            QLabel#fieldLabel {{
                color: {colors["muted"]};
                font-size: 12px;
                font-weight: 700;
            }}
            QLabel#countBadge {{
                background: {colors["text"]};
                color: {colors["window"]};
                border-radius: 10px;
                font-weight: 800;
                padding: 6px 10px;
            }}
            QLabel#hotkeyStatus {{
                color: {colors["muted"]};
                font-size: 12px;
                font-weight: 700;
            }}
            QLabel#hotkeyStatus[status="ok"] {{
                color: {colors["soft"]};
            }}
            QLabel#hotkeyStatus[status="error"] {{
                color: {colors["danger"]};
            }}
            QTabWidget#settingsTabs::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {colors["tab"]};
                color: {colors["muted"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                min-width: 86px;
                min-height: 30px;
                margin-right: 7px;
                padding: 0 12px;
                font-weight: 700;
            }}
            QTabBar::tab:selected {{
                background: {colors["tab_selected"]};
                color: {colors["text"]};
                border-color: rgba(15, 143, 134, 92);
            }}
            QFrame#settingsPanel,
            QFrame#sidePanel,
            QFrame#editPanel {{
                background: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 14px;
            }}
            QLineEdit,
            QTextEdit,
            QListWidget#phraseList {{
                background: {colors["control"]};
                border: 1px solid {colors["border_soft"]};
                border-radius: 10px;
                color: {colors["text"]};
                selection-background-color: {colors["accent"]};
                selection-color: #ffffff;
                outline: 0;
            }}
            QLineEdit {{
                min-height: 36px;
                padding: 0 12px;
            }}
            QTextEdit {{
                padding: 10px 12px;
            }}
            QLineEdit:focus,
            QTextEdit:focus,
            QListWidget#phraseList:focus {{
                background: {colors["control_hover"]};
                border-color: {colors["accent"]};
            }}
            QLineEdit:disabled,
            QTextEdit:disabled {{
                color: {colors["muted"]};
                background: {colors["surface_alt"]};
                border-color: {colors["border"]};
            }}
            QComboBox#languageCombo,
            QComboBox#themeCombo {{
                selection-background-color: {colors["accent"]};
                selection-color: #ffffff;
                outline: 0;
            }}
            QComboBox#languageCombo::drop-down,
            QComboBox#themeCombo::drop-down {{
                border: none;
                width: 0;
            }}
            QComboBox#languageCombo::down-arrow,
            QComboBox#themeCombo::down-arrow {{
                image: none;
                width: 0;
                height: 0;
            }}
            QComboBox#languageCombo QAbstractItemView,
            QComboBox#themeCombo QAbstractItemView {{
                background: {colors["button"]};
                border: 1px solid {colors["border_soft"]};
                border-radius: 9px;
                color: {colors["text"]};
                outline: 0;
                padding: 4px;
                selection-background-color: {colors["selection"]};
                selection-color: {colors["text"]};
            }}
            QComboBox#languageCombo QAbstractItemView::item,
            QComboBox#themeCombo QAbstractItemView::item {{
                min-height: 28px;
                padding: 4px 9px;
            }}
            QListWidget#phraseList::item {{
                padding: 10px 9px;
                border-radius: 9px;
                margin: 3px;
                color: {colors["muted"]};
                outline: 0;
            }}
            QListWidget#phraseList::item:selected {{
                background: {colors["button"]};
                color: {colors["text"]};
                border-left: 4px solid {colors["accent"]};
                border-top: 1px solid rgba(15, 143, 134, 92);
                border-right: 1px solid rgba(15, 143, 134, 92);
                border-bottom: 1px solid rgba(15, 143, 134, 92);
            }}
            QListWidget#phraseList::item:hover {{
                background: {colors["button_hover"]};
            }}
            QPushButton {{
                background: {colors["button"]};
                border: 1px solid {colors["border"]};
                border-radius: 9px;
                color: {colors["text"]};
                min-height: 32px;
                padding: 0 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {colors["button_hover"]};
                border-color: rgba(15, 143, 134, 92);
            }}
            QPushButton:disabled {{
                color: {colors["muted"]};
                background: {colors["surface_alt"]};
                border-color: {colors["border"]};
            }}
            QPushButton#primaryButton,
            QPushButton#saveButton {{
                background: {colors["accent"]};
                border-color: {colors["accent"]};
                color: #ffffff;
                font-weight: 800;
            }}
            QPushButton#primaryButton:hover,
            QPushButton#saveButton:hover {{
                background: {colors["accent_hover"]};
                border-color: {colors["accent_hover"]};
            }}
            QPushButton#dangerButton {{
                color: {colors["danger"]};
            }}
            QPushButton#dangerButton:hover {{
                background: {colors["danger_bg"]};
                border-color: rgba(196, 85, 72, 92);
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 5px;
                margin: 4px 0 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {colors["scroll"]};
                border-radius: 2px;
                min-height: 28px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(15, 143, 134, 92);
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
                height: 0;
            }}
            """
        )
