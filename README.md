# QuickInput

[中文](#中文文档) | [English](#english-documentation)

## 中文文档

QuickInput 是一个 Windows 托盘快速输入工具。程序常驻后台，通过全局热键弹出短语选择窗口，按配置中的快捷键即可把文本粘贴到当前光标位置。

## 功能

- 默认全局热键 `Ctrl+[` 唤起或隐藏快捷输入弹窗，可在设置中自定义并自动检测全局冲突。
- 系统托盘常驻，支持显示窗口、设置、打开日志目录和退出。
- 设置窗口内置短语编辑，支持新增、删除、修改和调整顺序。
- 设置窗口支持简体中文 / 英文、浅色 / 深色 / 跟随系统主题切换。
- 弹窗内可用 `1-9` 等配置键快速选择，也可鼠标点击候选项。
- 长文本自动换行，候选项区域支持滚动。
- 粘贴后延迟恢复剪贴板；如果用户在恢复前复制了新内容，不会覆盖用户的新剪贴板内容。
- 使用 Windows 互斥锁防重复启动。
- 日志写入用户数据目录，便于排查热键、托盘和粘贴问题。

## 运行要求

- Windows
- Python 3.10+

开发运行：

```bash
python -m pip install -r requirements.txt
python main.py
```

快速启动烟测：

```bash
python main.py --smoke-test
```

## 项目结构

```text
quickinput/
  app.py                 # 应用生命周期、托盘/弹窗/热键/剪贴板协同
  paths.py               # 资源路径、用户数据目录、内置默认文本初始化
  settings.py            # settings.ini 读写和默认配置
  phrase_store.py        # text.csv 加载、保存和校验
  phrase_manager.py      # 旧版 PySide6 文本管理窗口
  popup.py               # PySide6 快捷输入弹窗
  tray.py                # 系统托盘菜单
  settings_dialog.py     # PySide6 统一设置窗口
  appearance.py          # 明暗主题解析
  i18n.py                # 中文/英文显示文案
  hotkey_config.py       # 热键常量、格式化和规范化
  hotkey_win.py          # Windows RegisterHotKey 全局热键服务
  clipboard_service.py   # pyperclip + SendInput 粘贴和剪贴板恢复
  single_instance.py     # Windows 单实例保护
  qt_bootstrap.py        # PySide6 / shiboken6 DLL 搜索路径初始化
  logging_setup.py       # 文件日志和控制台日志配置

tests/
  test_paths.py
  test_phrase_store.py
  test_phrase_manager.py
  test_settings.py
  test_settings_dialog.py
  test_hotkey_config.py
  test_tray.py
  test_popup.py
```

根目录的 `main.py` 是启动入口，实际逻辑位于 `quickinput.main` 和 `quickinput.app`。

## 技术架构

当前版本已从旧的 Tkinter / pystray / pynput 组合迁移到以下实现：

- `PySide6`：主事件循环、快捷输入弹窗、统一设置窗口和系统托盘。
- Windows `RegisterHotKey`：系统级全局热键，独立线程监听 `WM_HOTKEY`，设置保存前会用临时注册探测冲突。
- `pyperclip` + Win32 `SendInput`：写入剪贴板并模拟 `Ctrl+V`。
- `PyInstaller`：生成 Windows 单文件 exe。

## 用户数据

应用运行时会把可变数据写入用户目录：

```text
%APPDATA%\QuickInput\
  text.csv
  settings.ini
  logs\app.log
```

也可以用环境变量覆盖数据目录，方便测试或隔离运行：

```powershell
$env:QUICKINPUT_DATA_DIR="D:\tmp\quickinput-data"
python main.py
```

`%APPDATA%\QuickInput\text.csv` 是实际运行时使用的短语文件。首次启动且该文件不存在时，程序会直接写入代码内置的默认 CSV 内容。

源码目录和 `dist` 目录不再携带初始化用 `text.csv`。用户数据目录里的 `text.csv` 才是长期数据源。

## 文本管理

推荐通过托盘菜单进入“设置”，在设置窗口的“短语”页进行日常维护。保存后，快捷输入弹窗会立即使用新的文本列表。

CSV 文件格式如下：

```csv
key,text
1,Hello
2,"Long text with comma, newline, or other content"
```

规则：

- 必须包含 `key` 和 `text` 两列。
- 空行会被忽略。
- 加载时缺少 `key`、缺少 `text` 或重复 `key` 的行会被跳过并写入警告日志。
- 通过设置窗口保存时，会拒绝空快捷键、空文本和重复快捷键。

## 配置

首次运行会自动生成 `settings.ini`。当前可配置项包括：

```ini
[hotkey]
label = Ctrl+[
modifiers = 16386
virtual_key = 219

[popup]
width = 520
height = 560

[paste]
delay_ms = 120
clipboard_restore_delay_ms = 1000

[ui]
language = zh_CN
theme = system
```

说明：

- 推荐通过设置窗口修改热键；保存前会自动检测候选热键是否被其他程序占用。
- `label` 是托盘和弹窗里展示的热键文字，保存时会按 `modifiers` 和 `virtual_key` 生成。
- `modifiers` 和 `virtual_key` 对应 Windows `RegisterHotKey` 参数。
- `popup.width` / `popup.height` 最小值为 `360`。
- `paste.delay_ms` 控制选择短语后延迟粘贴的时间。
- `paste.clipboard_restore_delay_ms` 控制恢复原剪贴板内容的延迟。
- `ui.language` 控制界面显示语言，支持 `zh_CN` 和 `en_US`。
- `ui.theme` 控制外观主题，支持 `system`、`light` 和 `dark`。
- 语言、主题、短语和热键都可通过托盘菜单的“设置”窗口切换，保存后立即生效。

## 打包

推荐发布给普通用户的产物是安装包：

```bash
build_installer.bat
```

构建成功后生成：

```text
dist\QuickInput-1.1.0-setup.exe
```

安装器支持 English / 简体中文安装语言选择，并会把所选语言写入用户级 `settings.ini`，应用首次启动时使用对应显示语言。

如果只需要 portable 单文件 EXE，可以运行：

```bash
build.bat
```

构建入口固定为 `QuickInput.spec`。构建成功后生成：

```text
dist\QuickInput.exe
```

打包说明：

- `installer\QuickInput.iss` 是 Windows 安装器脚本，使用 Inno Setup 6 编译。
- `QuickInput.spec` 会打包 `icon.png`。
- `QuickInput.spec` 排除了 Tkinter、pystray、pynput、PyQt 等旧实现或未使用依赖。
- `build.bat` 会安装依赖、运行 PyInstaller，并把 `icon.png` 复制到 `dist`。
- `build_installer.bat` 会先构建 `QuickInput.exe`，再生成安装包。
- 默认短语由代码内置初始化，不依赖 `dist\text.csv`。

打包后可执行启动烟测：

```bash
dist\QuickInput.exe --smoke-test
```

## 开发验证

单元测试使用标准库 `unittest`：

```bash
python -m unittest discover -s tests
```

当前测试覆盖：

- 用户数据目录覆盖和默认短语文件初始化。
- `settings.ini` 默认生成与读写。
- 中文/英文显示语言和明暗主题配置。
- `text.csv` 加载、保存、必要列检查和重复快捷键处理。
- 设置窗口提交当前短语编辑内容、返回语言/主题选择并校验热键冲突。

如果在无桌面环境或 CI 中运行 Qt 相关测试，可设置：

```powershell
$env:QT_QPA_PLATFORM="offscreen"
python -m unittest discover -s tests
```

## 故障排查

- 热键无响应：在设置中换一个热键并查看冲突提示，或检查 `logs\app.log` 中的 Windows 错误码。
- 托盘图标不可见：先检查系统托盘隐藏区域；如果系统未报告可用托盘，日志会写入警告。
- 粘贴失败：确认目标窗口支持 `Ctrl+V`，并检查剪贴板读写是否被安全软件或目标应用限制。
- 文本列表为空：检查用户数据目录中的 `text.csv` 是否包含 `key,text` 表头和有效内容。
- 想重置短语：退出应用后删除 `%APPDATA%\QuickInput\text.csv`，下次启动会重新按初始化顺序生成。

## 维护注意

- 运行期数据以 `%APPDATA%\QuickInput` 为准，源码根目录和 `dist` 目录不再保存初始化模板 `text.csv`。
- 修改热键、语言或主题默认值时，需要同时更新 `quickinput/settings.py`、`quickinput/i18n.py` 和本文档的配置说明。
- 修改 CSV 校验规则时，需要同步 `quickinput/phrase_store.py`、管理窗口保存行为和测试用例。
- 修改打包资源时，需要同步 `QuickInput.spec`、`build.bat` 和本文档的打包说明。

## 许可证

本项目使用 GPL-3.0 许可证，详见 `LICENSE`。

## English Documentation

QuickInput is a Windows tray utility for fast text input. It stays in the background, opens a phrase picker with a global hotkey, and pastes the selected phrase into the current cursor position.

### Features

- Default global `Ctrl+[` hotkey to show or hide the quick input popup, with custom shortcuts and automatic global conflict checks in Settings.
- System tray menu for showing the popup, opening Settings, opening logs, and exiting.
- Settings includes phrase editing for adding, deleting, editing, and reordering phrases.
- Settings supports Simplified Chinese / English and light / dark / follow-system themes.
- Number-key phrase selection, mouse selection, wrapped long text, and a scrollable phrase list.
- Clipboard restore delay that avoids overwriting new clipboard content copied by the user.
- Windows single-instance guard and file logging under the user data directory.

### Requirements

- Windows
- Python 3.10+

Development run:

```bash
python -m pip install -r requirements.txt
python main.py
```

Smoke test:

```bash
python main.py --smoke-test
```

### User Data

Runtime data is stored outside the source and release folders:

```text
%APPDATA%\QuickInput\
  text.csv
  settings.ini
  logs\app.log
```

You can override the data directory for testing:

```powershell
$env:QUICKINPUT_DATA_DIR="D:\tmp\quickinput-data"
python main.py
```

`%APPDATA%\QuickInput\text.csv` is the active phrase file. On first launch, if it does not exist, QuickInput writes the built-in default CSV content. The source root and `dist` folder no longer carry an initialization `text.csv`.

### Phrase Management

Use the tray menu and open `Settings`, then edit phrases from the `Phrases` tab. Saved changes are applied to the popup immediately.

CSV format:

```csv
key,text
1,Hello
2,"Long text with comma, newline, or other content"
```

Rules:

- The file must contain `key` and `text` columns.
- Empty rows are ignored.
- Rows with missing keys, missing text, or duplicate keys are skipped during loading and written to the log.
- Settings rejects empty shortcuts, empty text, and duplicate shortcuts before saving.

### Configuration

`settings.ini` is created automatically on first launch:

```ini
[hotkey]
label = Ctrl+[
modifiers = 16386
virtual_key = 219

[popup]
width = 520
height = 560

[paste]
delay_ms = 120
clipboard_restore_delay_ms = 1000

[ui]
language = zh_CN
theme = system
```

Notes:

- Prefer changing the hotkey from Settings; candidate shortcuts are checked for global conflicts before saving.
- `label` is the hotkey text shown in the tray and popup, generated from `modifiers` and `virtual_key` when settings are saved.
- `modifiers` and `virtual_key` map to Windows `RegisterHotKey` parameters.
- `popup.width` and `popup.height` are clamped to at least `360`.
- `paste.delay_ms` controls the delay before pasting after a phrase is selected.
- `paste.clipboard_restore_delay_ms` controls when the previous clipboard content is restored.
- `ui.language` controls the display language. Supported values are `zh_CN` and `en_US`.
- `ui.theme` controls appearance. Supported values are `system`, `light`, and `dark`.
- Language, theme, phrases, and hotkey can be changed from the tray `Settings` dialog and apply immediately after saving.

### Build

The recommended asset for normal users is the installer:

```bash
build_installer.bat
```

A successful build creates:

```text
dist\QuickInput-1.1.0-setup.exe
```

The installer supports English and Simplified Chinese setup languages. It writes the selected language to the user-level `settings.ini`, so the app starts in the chosen display language.

For a portable single-file executable, run:

```bash
build.bat
```

The PyInstaller entrypoint is `QuickInput.spec`. A successful build creates:

```text
dist\QuickInput.exe
```

Build notes:

- `installer\QuickInput.iss` is the Windows installer script and is compiled with Inno Setup 6.
- `QuickInput.spec` packages `icon.png`.
- `QuickInput.spec` excludes old or unused UI/input dependencies such as Tkinter, pystray, pynput, and PyQt.
- `build.bat` installs dependencies, runs PyInstaller, and copies `icon.png` to `dist`.
- `build_installer.bat` builds `QuickInput.exe` first, then creates the setup package.
- Default phrases are initialized from built-in code, not from `dist\text.csv`.

Packaged smoke test:

```bash
dist\QuickInput.exe --smoke-test
```

### Testing

Unit tests use the standard `unittest` runner:

```bash
python -m unittest discover -s tests
```

Current tests cover settings persistence, phrase validation, settings-window phrase edits, hotkey formatting/conflict status, and popup language rendering.

For headless or CI environments:

```powershell
$env:QT_QPA_PLATFORM="offscreen"
python -m unittest discover -s tests
```

### Troubleshooting

- Hotkey does not work: choose another shortcut in Settings and check the conflict hint, or inspect `logs\app.log`.
- Tray icon is not visible: check the hidden tray area first; QuickInput logs a warning if the system tray is unavailable.
- Paste fails: confirm the target app accepts `Ctrl+V` and that clipboard access is not blocked by security software.
- Phrase list is empty: check whether `%APPDATA%\QuickInput\text.csv` has the `key,text` header and valid rows.
- Reset phrases: exit QuickInput, delete `%APPDATA%\QuickInput\text.csv`, then launch the app again.

### License

This project is licensed under GPL-3.0. See `LICENSE`.
