from __future__ import annotations

DEFAULT_LANGUAGE = "zh_CN"
SUPPORTED_LANGUAGES = ("zh_CN", "en_US")
LANGUAGE_NAMES = {
    "zh_CN": "简体中文",
    "en_US": "English",
}


TRANSLATIONS: dict[str, dict[str, str]] = {
    "zh_CN": {
        "tray.hotkey": "热键: {hotkey}",
        "tray.show_window": "显示窗口",
        "tray.settings": "设置",
        "tray.open_logs": "打开日志目录",
        "tray.quit": "退出",
        "popup.subtitle": "选择短语后自动粘贴到当前光标",
        "popup.ready": "就绪",
        "popup.empty_status": "空列表",
        "popup.empty_state": "没有可用文本。请通过设置的短语页管理文本。",
        "popup.footer": "数字键选择，Esc 关闭",
        "popup.key_hint": "1  2  3  Esc",
        "popup.count": "{count} 条文本",
        "popup.pasting": "正在粘贴",
        "manager.window_title": "管理文本",
        "manager.title": "短语管理",
        "manager.subtitle": "维护数字快捷键和对应文本，保存后立即同步到弹窗。",
        "manager.list_title": "短语列表",
        "manager.add": "新增",
        "manager.delete": "删除",
        "manager.up": "上移",
        "manager.down": "下移",
        "manager.edit_title": "编辑内容",
        "manager.edit_hint": "快捷键建议使用 1-9，文本会以纯文本保存。",
        "manager.key_label": "快捷键",
        "manager.key_placeholder": "例如：1",
        "manager.text_label": "文本内容",
        "manager.text_placeholder": "输入需要快速粘贴的文本",
        "manager.save": "保存",
        "manager.cancel": "取消",
        "manager.count": "{count} 条",
        "manager.cannot_save": "无法保存",
        "manager.discard_title": "放弃更改",
        "manager.discard_message": "放弃未保存的更改？",
        "settings.window_title": "设置",
        "settings.title": "设置",
        "settings.subtitle": "调整热键、短语和外观偏好。",
        "settings.preferences_tab": "偏好",
        "settings.phrases_tab": "短语",
        "settings.preferences_title": "基础偏好",
        "settings.language_label": "显示语言",
        "settings.language_hint": "保存后立即应用到托盘和窗口。",
        "settings.theme_label": "外观主题",
        "settings.theme_hint": "跟随系统会读取当前 Windows 明暗模式。",
        "settings.theme_system": "跟随系统",
        "settings.theme_light": "浅色",
        "settings.theme_dark": "深色",
        "settings.hotkey_label": "全局热键",
        "settings.hotkey_hint": "点击输入框后按下新的组合键；保存前会自动检测全局冲突。",
        "settings.hotkey_placeholder": "按下组合键",
        "settings.hotkey_current": "当前热键可继续使用。",
        "settings.hotkey_available": "热键可用。",
        "settings.hotkey_conflict": "该热键已被其他程序占用。",
        "settings.hotkey_invalid": "请至少包含 Ctrl、Alt、Shift 或 Win 中的一个修饰键。",
        "settings.hotkey_reset": "重置",
        "settings.phrases_title": "短语管理",
        "settings.phrases_hint": "保存后立即同步到弹窗。",
        "settings.save": "保存",
        "settings.cancel": "取消",
        "settings.saved": "设置已保存",
        "app.already_running": "QuickInput 已经在运行。",
        "app.loaded_count": "已加载 {count} 条文本",
        "app.saved_count": "已保存 {count} 条文本",
        "app.save_failed": "保存失败: {error}",
        "app.paste_failed": "粘贴失败: {error}",
        "app.hotkey_unavailable": "QuickInput 热键不可用",
        "app.open_failed": "打开失败: {path}",
    },
    "en_US": {
        "tray.hotkey": "Hotkey: {hotkey}",
        "tray.show_window": "Show Window",
        "tray.settings": "Settings",
        "tray.open_logs": "Open Log Folder",
        "tray.quit": "Exit",
        "popup.subtitle": "Select a phrase to paste at the active cursor",
        "popup.ready": "Ready",
        "popup.empty_status": "Empty",
        "popup.empty_state": "No phrases available. Use Settings > Phrases to manage them.",
        "popup.footer": "Press a number to paste, Esc to close",
        "popup.key_hint": "1  2  3  Esc",
        "popup.count": "{count} phrases",
        "popup.pasting": "Pasting",
        "manager.window_title": "Manage Phrases",
        "manager.title": "Phrase Manager",
        "manager.subtitle": "Edit shortcuts and text. Saved changes sync immediately.",
        "manager.list_title": "Phrase List",
        "manager.add": "Add",
        "manager.delete": "Delete",
        "manager.up": "Up",
        "manager.down": "Down",
        "manager.edit_title": "Edit Phrase",
        "manager.edit_hint": "Use 1-9 for quick access. Text is saved as plain text.",
        "manager.key_label": "Shortcut",
        "manager.key_placeholder": "Example: 1",
        "manager.text_label": "Text",
        "manager.text_placeholder": "Enter text to paste quickly",
        "manager.save": "Save",
        "manager.cancel": "Cancel",
        "manager.count": "{count} items",
        "manager.cannot_save": "Cannot Save",
        "manager.discard_title": "Discard Changes",
        "manager.discard_message": "Discard unsaved changes?",
        "settings.window_title": "Settings",
        "settings.title": "Settings",
        "settings.subtitle": "Adjust hotkey, phrase, and appearance preferences.",
        "settings.preferences_tab": "Preferences",
        "settings.phrases_tab": "Phrases",
        "settings.preferences_title": "Preferences",
        "settings.language_label": "Display Language",
        "settings.language_hint": "Saved changes apply to tray and windows immediately.",
        "settings.theme_label": "Appearance Theme",
        "settings.theme_hint": "Follow system uses the current Windows light or dark mode.",
        "settings.theme_system": "Follow System",
        "settings.theme_light": "Light",
        "settings.theme_dark": "Dark",
        "settings.hotkey_label": "Global Hotkey",
        "settings.hotkey_hint": "Focus the field and press a new shortcut. Global conflicts are checked before saving.",
        "settings.hotkey_placeholder": "Press shortcut",
        "settings.hotkey_current": "Current hotkey is available.",
        "settings.hotkey_available": "Hotkey is available.",
        "settings.hotkey_conflict": "This hotkey is already used by another app.",
        "settings.hotkey_invalid": "Use at least one modifier: Ctrl, Alt, Shift, or Win.",
        "settings.hotkey_reset": "Reset",
        "settings.phrases_title": "Phrase Manager",
        "settings.phrases_hint": "Saved changes sync to the popup immediately.",
        "settings.save": "Save",
        "settings.cancel": "Cancel",
        "settings.saved": "Settings saved",
        "app.already_running": "QuickInput is already running.",
        "app.loaded_count": "{count} phrases loaded",
        "app.saved_count": "{count} phrases saved",
        "app.save_failed": "Save failed: {error}",
        "app.paste_failed": "Paste failed: {error}",
        "app.hotkey_unavailable": "QuickInput Hotkey Unavailable",
        "app.open_failed": "Open failed: {path}",
    },
}


def normalize_language(value: str | None) -> str:
    if not value:
        return DEFAULT_LANGUAGE
    normalized = value.strip()
    if normalized in SUPPORTED_LANGUAGES:
        return normalized

    aliases = {
        "zh": "zh_CN",
        "zh-cn": "zh_CN",
        "zh_cn": "zh_CN",
        "cn": "zh_CN",
        "chinese": "zh_CN",
        "en": "en_US",
        "en-us": "en_US",
        "en_us": "en_US",
        "english": "en_US",
    }
    return aliases.get(normalized.lower(), DEFAULT_LANGUAGE)


def language_name(language: str) -> str:
    return LANGUAGE_NAMES.get(normalize_language(language), LANGUAGE_NAMES[DEFAULT_LANGUAGE])


class Translator:
    def __init__(self, language: str | None = None):
        self.language = normalize_language(language)

    def t(self, key: str, **kwargs: object) -> str:
        template = TRANSLATIONS.get(self.language, {}).get(key)
        if template is None:
            template = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
        return template.format(**kwargs) if kwargs else template
