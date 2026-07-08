from __future__ import annotations

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

VK_OEM_4 = 0xDB

DEFAULT_HOTKEY_LABEL = "Ctrl+["
DEFAULT_HOTKEY_MODIFIERS = MOD_CONTROL | MOD_NOREPEAT
DEFAULT_HOTKEY_VIRTUAL_KEY = VK_OEM_4

_MODIFIER_MASK = MOD_ALT | MOD_CONTROL | MOD_SHIFT | MOD_WIN | MOD_NOREPEAT

_VK_NAMES = {
    0x08: "Backspace",
    0x09: "Tab",
    0x0D: "Enter",
    0x1B: "Esc",
    0x20: "Space",
    0x21: "PageUp",
    0x22: "PageDown",
    0x23: "End",
    0x24: "Home",
    0x25: "Left",
    0x26: "Up",
    0x27: "Right",
    0x28: "Down",
    0x2D: "Insert",
    0x2E: "Delete",
    0xBA: ";",
    0xBB: "=",
    0xBC: ",",
    0xBD: "-",
    0xBE: ".",
    0xBF: "/",
    0xC0: "`",
    0xDB: "[",
    0xDC: "\\",
    0xDD: "]",
    0xDE: "'",
}


def normalize_hotkey_modifiers(modifiers: int) -> int:
    normalized = int(modifiers) & _MODIFIER_MASK
    if normalized & (MOD_ALT | MOD_CONTROL | MOD_SHIFT | MOD_WIN):
        normalized |= MOD_NOREPEAT
    return normalized


def display_modifiers(modifiers: int) -> int:
    return normalize_hotkey_modifiers(modifiers) & ~MOD_NOREPEAT


def has_required_modifier(modifiers: int) -> bool:
    return bool(display_modifiers(modifiers))


def key_name(virtual_key: int) -> str:
    virtual_key = int(virtual_key)
    if 0x30 <= virtual_key <= 0x39:
        return chr(virtual_key)
    if 0x41 <= virtual_key <= 0x5A:
        return chr(virtual_key)
    if 0x70 <= virtual_key <= 0x87:
        return f"F{virtual_key - 0x6F}"
    return _VK_NAMES.get(virtual_key, f"VK{virtual_key}")


def format_hotkey_label(modifiers: int, virtual_key: int) -> str:
    parts: list[str] = []
    shown_modifiers = display_modifiers(modifiers)
    if shown_modifiers & MOD_CONTROL:
        parts.append("Ctrl")
    if shown_modifiers & MOD_ALT:
        parts.append("Alt")
    if shown_modifiers & MOD_SHIFT:
        parts.append("Shift")
    if shown_modifiers & MOD_WIN:
        parts.append("Win")
    if virtual_key:
        parts.append(key_name(virtual_key))
    return "+".join(parts)


def same_hotkey(
    first_modifiers: int,
    first_virtual_key: int,
    second_modifiers: int,
    second_virtual_key: int,
) -> bool:
    return (
        normalize_hotkey_modifiers(first_modifiers)
        == normalize_hotkey_modifiers(second_modifiers)
        and int(first_virtual_key) == int(second_virtual_key)
    )
