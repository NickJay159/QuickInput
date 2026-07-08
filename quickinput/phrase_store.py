from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Phrase:
    key: str
    text: str


@dataclass(frozen=True)
class PhraseLoadResult:
    phrases: list[Phrase]
    warnings: list[str]


class PhraseStoreError(Exception):
    pass


def validate_phrases(phrases: list[Phrase]) -> list[Phrase]:
    normalized: list[Phrase] = []
    seen_keys: set[str] = set()

    for index, phrase in enumerate(phrases, start=1):
        key = phrase.key.strip()
        text = phrase.text.strip()
        if not key:
            raise PhraseStoreError(f"第 {index} 条缺少快捷键")
        if not text:
            raise PhraseStoreError(f"第 {index} 条缺少文本内容")
        if key in seen_keys:
            raise PhraseStoreError(f"快捷键重复: {key}")
        seen_keys.add(key)
        normalized.append(Phrase(key=key, text=text))

    return normalized


class PhraseStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> PhraseLoadResult:
        if not self.path.exists():
            raise PhraseStoreError(f"配置文件不存在: {self.path}")

        warnings: list[str] = []
        phrases: list[Phrase] = []
        seen_keys: set[str] = set()

        with self.path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                raise PhraseStoreError("CSV 文件为空")
            required = {"key", "text"}
            missing = required.difference(reader.fieldnames)
            if missing:
                missing_text = ", ".join(sorted(missing))
                raise PhraseStoreError(f"CSV 缺少必要列: {missing_text}")

            for line_no, row in enumerate(reader, start=2):
                key = (row.get("key") or "").strip()
                text = (row.get("text") or "").strip()
                if not key and not text:
                    continue
                if not key:
                    warnings.append(f"第 {line_no} 行缺少 key，已跳过")
                    continue
                if not text:
                    warnings.append(f"第 {line_no} 行缺少 text，已跳过")
                    continue
                if key in seen_keys:
                    warnings.append(f"第 {line_no} 行 key 重复: {key}，已跳过")
                    continue
                seen_keys.add(key)
                phrases.append(Phrase(key=key, text=text))

        return PhraseLoadResult(phrases=phrases, warnings=warnings)

    def save(self, phrases: list[Phrase]) -> None:
        normalized = validate_phrases(phrases)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["key", "text"])
            writer.writeheader()
            for phrase in normalized:
                writer.writerow({"key": phrase.key, "text": phrase.text})
