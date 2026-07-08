# QuickInput 优雅 UI 设计规范

Figma 文件已创建，但本次写入被 Figma Starter 计划 MCP 调用额度拦截，无法继续向画布生成节点。

- Figma 文件：https://www.figma.com/design/AjhaRFVWwcIcuc2XqE2PBF
- 可交互本地原型：`design/quickinput-elegant-ui.html`

## 设计目标

QuickInput 是常驻托盘的快速输入工具，界面不应像大型后台系统，也不应像营销页。设计基调是轻、快、可靠：

- 弹窗第一眼要像一个高级的系统浮层，而不是普通表单。
- 数字快捷键必须比装饰更突出，用户可以扫一眼直接按键。
- 显示和消失要短、干净、有方向感，不能拖慢粘贴动作。
- 短语管理窗口保持高信息密度，但用更清晰的面板层级和编辑区焦点。

## 视觉系统

| Token | Value | 用途 |
| --- | --- | --- |
| `surface` | `rgba(255,255,255,0.78)` | 浮层主表面 |
| `surface-strong` | `#ffffff` | 行项目、输入框、按钮 |
| `text` | `#172026` | 主标题和正文 |
| `text-soft` | `#4f5f68` | 副标题、说明、辅助信息 |
| `line` | `rgba(34,51,59,0.12)` | 默认边框 |
| `accent` | `#0f8f86` | 选中、主按钮、键帽激活 |
| `danger` | `#c45548` | 删除操作 |
| `success` | `#2f8d58` | 保存/粘贴反馈 |
| `radius-window` | `18px` | 弹窗和管理窗口 |
| `radius-panel` | `12px` | 列表行、管理面板 |

字体沿用当前代码基线：

```css
"Microsoft YaHei UI", "Segoe UI", system-ui, Arial, sans-serif
```

## 弹窗布局

- 默认尺寸：`520 x 560`，沿用现有 `settings.popup_width` / `popup_height`。
- 外边距：`22px 22px 18px`。
- Header：左侧 `QuickInput + 副标题`，右侧 `Ctrl+[` 热键徽标。
- 状态条：显示 `就绪 / 正在粘贴 / 没有可用文本` 等即时状态。
- 短语行：`56px` 最小高度，三列布局：键帽、文本、右侧箭头。
- 选中行：左侧 `3px` accent 指示条，键帽反白。
- Hover：轻微上浮 `-1px`，边框变 accent 半透明，不做大面积高亮。
- Footer：保留 `数字键选择，Esc 关闭` 和小键帽提示。

## 管理窗口布局

- 默认尺寸：`860 x 560`，保留当前功能结构。
- Header：标题、副标题、右侧条数徽标。
- Body：左侧 `292px` 列表面板，右侧自适应编辑面板。
- 列表项：数字键帽 + 文本预览，选中态使用同一 accent 指示条。
- 操作按钮：新增为主按钮，删除为 danger 文本按钮，上移/下移为普通按钮。
- 编辑区：快捷键输入框、纯文本编辑器、底部提示和保存/取消按钮。

## 显示与消失动效

### 显示

- 起点：`opacity 0`，`translateY(18px)`，`scale(0.965)`，`blur(4px)`。
- 终点：`opacity 1`，`translateY(0)`，`scale(1)`，`blur(0)`。
- 时长：`160ms`。
- 曲线：`OutCubic`，CSS 原型中为 `cubic-bezier(.16, 1, .3, 1)`。
- 行项目错峰：每行延迟 `22ms`，整体不超过 `180ms`。

### 消失

- 起点：当前可见状态。
- 终点：`opacity 0`，`translateY(-8px)`，`scale(0.985)`，`blur(2px)`。
- 时长：`120ms`。
- 曲线：`InCubic`，CSS 原型中为 `cubic-bezier(.45, 0, 1, 1)`。
- 交互：选择短语后先切换状态条为 `正在粘贴`，约 `180ms` 后开始收起。

## PySide6 实现建议

弹窗可以继续用 `QDialog`，但建议增加以下实现点：

1. 使用 `QGraphicsOpacityEffect` 控制透明度。
2. 使用两个 `QPropertyAnimation` 分别控制 `windowOpacity` 或 opacity effect、以及 `pos`。
3. 位置动画以 `show_centered()` 计算出的中心点为基准：
   - show 起点：中心点下移 `18px`。
   - hide 终点：中心点上移 `8px`。
4. `hide()` 不要立即调用，先播放隐藏动画，动画结束后再真正隐藏窗口。
5. 行项目进入可以用 `QTimer.singleShot(index * 22, ...)` 做轻量错峰，也可以只在 CSS/QSS 上保持静态样式，优先保证弹窗整体动效。
6. 遵循系统减少动画偏好时，只保留淡入淡出或直接显示。

## 实施优先级

1. 先实现弹窗外观和 show/hide 动效。
2. 再同步短语管理窗口视觉 token。
3. 最后补充空状态、错误状态和保存成功的托盘/窗口反馈一致性。
