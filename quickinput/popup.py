from __future__ import annotations

import ctypes
import os

from .qt_bootstrap import bootstrap_qt_dlls

bootstrap_qt_dlls()

from PySide6.QtCore import (  # noqa: E402
    QEasingCurve,
    QPoint,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QCursor, QGuiApplication, QKeyEvent  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .phrase_store import Phrase
from .i18n import Translator
from .settings import AppSettings


class PhraseRow(QFrame):
    clicked = Signal(str)

    def __init__(self, phrase: Phrase, parent: QWidget | None = None):
        super().__init__(parent)
        self.phrase = phrase
        self.setObjectName("phraseRow")
        self.setProperty("selected", False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 12, 10)
        layout.setSpacing(13)

        key_label = QLabel(phrase.key)
        key_label.setObjectName("keyBadge")
        key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_label.setFixedSize(38, 34)

        text_label = QLabel(phrase.text)
        text_label.setObjectName("phraseText")
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        text_label.setToolTip(phrase.text)

        arrow_label = QLabel("›")
        arrow_label.setObjectName("rowArrow")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_label.setFixedWidth(18)

        layout.addWidget(key_label)
        layout.addWidget(text_label, 1)
        layout.addWidget(arrow_label)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.phrase.text)
        super().mousePressEvent(event)


class PhrasePopup(QDialog):
    phrase_selected = Signal(str)

    SHOW_OFFSET_Y = 18
    HIDE_OFFSET_Y = -8

    def __init__(
        self,
        phrases: list[Phrase],
        settings: AppSettings,
        translator: Translator,
    ):
        super().__init__()
        self.settings = settings
        self.translator = translator
        self._phrases: list[Phrase] = []
        self._row_widgets: list[PhraseRow] = []
        self._rows_layout: QVBoxLayout | None = None
        self._empty_label: QLabel | None = None
        self._status_label: QLabel | None = None
        self._count_label: QLabel | None = None
        self._subtitle_label: QLabel | None = None
        self._hotkey_label: QLabel | None = None
        self._footer_label: QLabel | None = None
        self._key_hint_label: QLabel | None = None
        self._show_animation: QParallelAnimationGroup | None = None
        self._hide_animation: QParallelAnimationGroup | None = None
        self._hide_target_pos = QPoint()
        self._force_hidden = False
        self._hiding = False
        self._pending_selected_text: str | None = None
        self._previous_foreground_window: int | None = None

        self.setWindowTitle("QuickInput")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(False)
        self.resize(settings.popup_width, settings.popup_height)
        self._build_ui()
        self.set_phrases(phrases)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("popupSurface")
        shadow = QGraphicsDropShadowEffect(surface)
        shadow.setBlurRadius(44)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(20, 35, 42, 56))
        surface.setGraphicsEffect(shadow)

        surface_layout = QVBoxLayout(surface)
        surface_layout.setContentsMargins(22, 22, 22, 18)
        surface_layout.setSpacing(14)

        header = QHBoxLayout()
        header.setSpacing(12)

        title_block = QVBoxLayout()
        title_block.setSpacing(3)

        title = QLabel("QuickInput")
        title.setObjectName("title")

        self._subtitle_label = QLabel(self.translator.t("popup.subtitle"))
        self._subtitle_label.setObjectName("subtitle")

        title_block.addWidget(title)
        title_block.addWidget(self._subtitle_label)

        self._hotkey_label = QLabel(self.settings.hotkey_label)
        self._hotkey_label.setObjectName("hotkeyBadge")
        self._hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addLayout(title_block, 1)
        header.addWidget(self._hotkey_label, 0, Qt.AlignmentFlag.AlignTop)

        status = QFrame()
        status.setObjectName("statusStrip")
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(12, 0, 10, 0)
        status_layout.setSpacing(10)
        self._status_label = QLabel(self.translator.t("popup.ready"))
        self._status_label.setObjectName("statusText")
        self._count_label = QLabel()
        self._count_label.setObjectName("countText")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(self._status_label, 1)
        status_layout.addWidget(self._count_label)

        scroll = QScrollArea()
        scroll.setObjectName("phraseScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("phraseContainer")
        self._rows_layout = QVBoxLayout(container)
        self._rows_layout.setContentsMargins(0, 0, 2, 0)
        self._rows_layout.setSpacing(9)
        self._rows_layout.addStretch(1)
        scroll.setWidget(container)

        self._empty_label = QLabel(self.translator.t("popup.empty_state"))
        self._empty_label.setObjectName("emptyState")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        self._footer_label = QLabel(self.translator.t("popup.footer"))
        self._footer_label.setObjectName("footer")
        self._key_hint_label = QLabel(self.translator.t("popup.key_hint"))
        self._key_hint_label.setObjectName("keyHint")
        self._key_hint_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        footer.addWidget(self._footer_label, 1)
        footer.addWidget(self._key_hint_label)

        surface_layout.addLayout(header)
        surface_layout.addWidget(status)
        surface_layout.addWidget(scroll, 1)
        surface_layout.addWidget(self._empty_label)
        surface_layout.addLayout(footer)
        root.addWidget(surface)

        self.setStyleSheet(
            """
            QDialog {
                background: transparent;
                color: #172026;
                font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", Arial;
                font-size: 13px;
            }
            QFrame#popupSurface {
                background: rgba(255, 255, 255, 232);
                border: 1px solid rgba(255, 255, 255, 236);
                border-radius: 18px;
            }
            QLabel#title {
                color: #172026;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#subtitle {
                color: #4f5f68;
                font-size: 12px;
            }
            QLabel#hotkeyBadge {
                background: #172026;
                color: #ffffff;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                padding: 8px 12px;
            }
            QFrame#statusStrip {
                min-height: 38px;
                max-height: 38px;
                background: #e1f5f2;
                border: 1px solid rgba(15, 143, 134, 46);
                border-radius: 11px;
            }
            QLabel#statusText {
                color: #08746d;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#countText {
                color: #4f5f68;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#footer,
            QLabel#keyHint {
                color: #4f5f68;
                font-size: 12px;
                padding-top: 2px;
            }
            QLabel#keyHint {
                color: #82909a;
                font-weight: 700;
            }
            QLabel#emptyState {
                color: #4f5f68;
                padding: 18px;
            }
            QWidget#phraseContainer {
                background: transparent;
            }
            QFrame#phraseRow {
                min-height: 56px;
                background: rgba(255, 255, 255, 206);
                border: 1px solid rgba(34, 51, 59, 31);
                border-radius: 12px;
            }
            QFrame#phraseRow:hover {
                background: #f3fbfa;
                border-color: rgba(15, 143, 134, 92);
            }
            QFrame#phraseRow[selected="true"] {
                background: #ffffff;
                border-left: 4px solid #0f8f86;
                border-top: 1px solid rgba(15, 143, 134, 118);
                border-right: 1px solid rgba(15, 143, 134, 118);
                border-bottom: 1px solid rgba(15, 143, 134, 118);
            }
            QFrame#phraseRow[selected="true"] QLabel#keyBadge {
                background: #0f8f86;
                color: #ffffff;
                border-color: #0f8f86;
            }
            QLabel#keyBadge {
                background: #e1f5f2;
                color: #08746d;
                border: 1px solid rgba(15, 143, 134, 46);
                border-radius: 10px;
                font-size: 14px;
                font-weight: 800;
            }
            QLabel#phraseText {
                color: #172026;
                line-height: 20px;
            }
            QLabel#rowArrow {
                color: #82909a;
                font-size: 22px;
                font-weight: 400;
            }
            QScrollArea#phraseScroll {
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 9px;
                margin: 2px 0 2px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(23, 32, 38, 52);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(23, 32, 38, 82);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )

    def set_phrases(self, phrases: list[Phrase]) -> None:
        self._phrases = phrases
        if self._rows_layout is None or self._empty_label is None:
            return

        self._row_widgets = []
        while self._rows_layout.count() > 0:
            item = self._rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for index, phrase in enumerate(phrases):
            row = PhraseRow(phrase)
            row.set_selected(index == 0)
            row.clicked.connect(lambda text, current=row: self._select_phrase_from_row(current, text))
            self._rows_layout.addWidget(row)
            self._row_widgets.append(row)
        self._rows_layout.addStretch(1)
        self._empty_label.setVisible(not phrases)
        if self._count_label:
            self._count_label.setText(
                self.translator.t("popup.count", count=len(phrases))
            )
        if self._status_label:
            self._status_label.setText(
                self.translator.t("popup.ready" if phrases else "popup.empty_status")
            )

    def apply_language(
        self,
        translator: Translator,
        settings: AppSettings | None = None,
    ) -> None:
        self.translator = translator
        if settings is not None:
            self.settings = settings
        if self._subtitle_label:
            self._subtitle_label.setText(self.translator.t("popup.subtitle"))
        if self._hotkey_label:
            self._hotkey_label.setText(self.settings.hotkey_label)
        if self._empty_label:
            self._empty_label.setText(self.translator.t("popup.empty_state"))
        if self._footer_label:
            self._footer_label.setText(self.translator.t("popup.footer"))
        if self._key_hint_label:
            self._key_hint_label.setText(self.translator.t("popup.key_hint"))
        self.set_phrases(self._phrases)

    def show_centered(self) -> None:
        screen = QGuiApplication.screenAt(QCursor.pos())
        screen = screen or QGuiApplication.primaryScreen()
        if screen is None:
            self.show()
            return
        self._remember_foreground_window()
        available = screen.availableGeometry()
        width = min(self.settings.popup_width, max(360, available.width() - 80))
        height = min(self.settings.popup_height, max(360, available.height() - 80))
        self.resize(width + 32, height + 32)
        target_pos = QPoint(
            available.x() + (available.width() - self.width()) // 2,
            available.y() + (available.height() - self.height()) // 2,
        )
        self.move(target_pos + QPoint(0, self.SHOW_OFFSET_Y))
        self.setWindowOpacity(0.0)
        self._hiding = False
        self._pending_selected_text = None
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._animate_show(target_pos)

    def hide(self) -> None:
        if self._force_hidden or not self.isVisible():
            super().hide()
            return
        if self._hiding:
            return
        self._animate_hide()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return

        text = event.text()
        if text:
            for row in self._row_widgets:
                if row.phrase.key == text:
                    self._select_phrase_from_row(row, row.phrase.text)
                    return
        super().keyPressEvent(event)

    def _select_phrase_from_row(self, row: PhraseRow, text: str) -> None:
        self._mark_selected(row)
        if self._status_label:
            self._status_label.setText(self.translator.t("popup.pasting"))
        self._pending_selected_text = text
        self.hide()

    def _mark_selected(self, selected_row: PhraseRow) -> None:
        for row in self._row_widgets:
            row.set_selected(row is selected_row)

    def _animate_show(self, target_pos: QPoint) -> None:
        if self._hide_animation:
            self._hide_animation.stop()
        self._show_animation = QParallelAnimationGroup(self)

        opacity = QPropertyAnimation(self, b"windowOpacity", self)
        opacity.setDuration(160)
        opacity.setStartValue(0.0)
        opacity.setEndValue(1.0)
        opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        position = QPropertyAnimation(self, b"pos", self)
        position.setDuration(160)
        position.setStartValue(self.pos())
        position.setEndValue(target_pos)
        position.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._show_animation.addAnimation(opacity)
        self._show_animation.addAnimation(position)
        self._show_animation.start()

    def _animate_hide(self) -> None:
        if self._show_animation:
            self._show_animation.stop()
        self._hiding = True
        self._hide_target_pos = self.pos() + QPoint(0, self.HIDE_OFFSET_Y)
        self._hide_animation = QParallelAnimationGroup(self)

        opacity = QPropertyAnimation(self, b"windowOpacity", self)
        opacity.setDuration(120)
        opacity.setStartValue(self.windowOpacity())
        opacity.setEndValue(0.0)
        opacity.setEasingCurve(QEasingCurve.Type.InCubic)

        position = QPropertyAnimation(self, b"pos", self)
        position.setDuration(120)
        position.setStartValue(self.pos())
        position.setEndValue(self._hide_target_pos)
        position.setEasingCurve(QEasingCurve.Type.InCubic)

        self._hide_animation.addAnimation(opacity)
        self._hide_animation.addAnimation(position)
        self._hide_animation.finished.connect(self._hide_after_animation)
        self._hide_animation.start()

    def _hide_after_animation(self) -> None:
        selected_text = self._pending_selected_text
        self._pending_selected_text = None
        self._force_hidden = True
        try:
            super().hide()
            self.setWindowOpacity(1.0)
        finally:
            self._force_hidden = False
            self._hiding = False
        self._restore_foreground_window()
        if selected_text is not None:
            self.phrase_selected.emit(selected_text)

    def _remember_foreground_window(self) -> None:
        if os.name != "nt":
            self._previous_foreground_window = None
            return
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            self._previous_foreground_window = int(hwnd) if hwnd else None
        except Exception:
            self._previous_foreground_window = None

    def _restore_foreground_window(self) -> None:
        if os.name != "nt" or not self._previous_foreground_window:
            return
        try:
            current_hwnd = int(self.winId())
            if self._previous_foreground_window != current_hwnd:
                ctypes.windll.user32.SetForegroundWindow(self._previous_foreground_window)
        except Exception:
            return
