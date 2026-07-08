# Changelog

## v1.1.0 - 2026-07-08

### 中文

- 设置窗口整合语言、明暗主题、全局热键和短语编辑，托盘右键菜单不再保留独立的“管理文本”入口。
- 新增自定义全局热键捕获，保存前会自动检测系统级快捷键冲突。
- 新增 `system` / `light` / `dark` 外观主题，弹窗和设置窗口会同步应用主题。
- 优化语言下拉控件外观，移除 Windows 原生下拉按钮造成的突兀视觉。
- 更新图标资源、README 和测试覆盖，新增托盘菜单、热键配置、主题持久化和设置页短语编辑测试。

### English

- Consolidates language, theme, global hotkey, and phrase editing into Settings; the tray menu no longer exposes a separate Manage Phrases entry.
- Adds custom global hotkey capture with automatic system-wide conflict checks before saving.
- Adds `system`, `light`, and `dark` appearance themes for both the popup and Settings window.
- Refines the language dropdown visual treatment by replacing the native Windows dropdown button.
- Updates icon assets, README documentation, and tests for tray menu behavior, hotkey configuration, theme persistence, and Settings-based phrase editing.

### Release Assets

- `QuickInput-1.1.0-setup.exe`: recommended installer for normal users.
- `QuickInput.exe`: portable single-file executable for users who do not want installation.

## v1.0.1 - 2026-07-08

### 中文

- 修复 `settings.ini` 带 UTF-8 BOM 时启动崩溃的问题。
- 新增回归测试，覆盖带 BOM 的设置文件读取。

### English

- Fixed startup crash when `settings.ini` contains a UTF-8 BOM.
- Added a regression test for reading BOM-prefixed settings files.

## v1.0.0 - 2026-07-08

### 中文

- 发布 QuickInput 首个公开安装版本。
- 提供 Windows 安装器 `QuickInput-1.0.0-setup.exe`，安装时可选择 English 或简体中文。
- 安装器会把所选语言写入用户级 `settings.ini`，应用启动后默认使用对应语言。
- 支持系统托盘、全局热键 `Ctrl+[`, 快捷短语弹窗、应用内短语管理和语言设置。
- 使用 `%APPDATA%\QuickInput` 保存用户短语、设置和日志，源码目录和安装目录不再保存初始化 CSV。
- 提供中英文 GitHub README、源码 smoke test、打包 EXE smoke test 和单元测试覆盖。

### English

- First public installable release of QuickInput.
- Adds a Windows installer, `QuickInput-1.0.0-setup.exe`, with English and Simplified Chinese setup languages.
- The installer writes the selected language into the user-level `settings.ini`, so the app starts in the chosen display language.
- Includes system tray integration, the global `Ctrl+[` hotkey, quick phrase popup, in-app phrase management, and UI language settings.
- Stores user phrases, settings, and logs under `%APPDATA%\QuickInput`; the source and install folders no longer carry initialization CSV files.
- Includes bilingual GitHub README documentation, source smoke test, packaged EXE smoke test, and unit test coverage.

### Release Assets

- `QuickInput-1.0.0-setup.exe`: recommended installer for normal users.
- `QuickInput.exe`: portable single-file executable for users who do not want installation.
