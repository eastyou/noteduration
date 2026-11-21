"""音符时值、拍号与小节补全题。"""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

NOTE_BEATS: Dict[str, float] = {
    "whole": 4.0,
    "half": 2.0,
    "quarter": 1.0,
    "eighth": 0.5,
    "sixteenth": 0.25,
}
NOTE_LABELS: Dict[str, str] = {
    "whole": "全音符",
    "half": "二分音符",
    "quarter": "四分音符",
    "eighth": "八分音符",
    "sixteenth": "十六分音符",
}
NOTE_ORDER = ("whole", "half", "quarter", "eighth", "sixteenth")
_ALIASES = {
    "whole": "whole",
    "全音符": "whole",
    "half": "half",
    "二分音符": "half",
    "quarter": "quarter",
    "四分音符": "quarter",
    "eighth": "eighth",
    "八分音符": "eighth",
    "sixteenth": "sixteenth",
    "十六分音符": "sixteenth",
}
_SIGNATURE = re.compile(r"^(\d{1,2})\s*/\s*(\d{1,2})$")


class RhythmError(ValueError):
    """音符、拍号或题目参数不合法。"""


@dataclass(frozen=True)
class RhythmNote:
    """一个音符，dotted 表示附点。"""

    kind: str
    dotted: bool = False

    def __post_init__(self) -> None:
        if self.kind not in NOTE_BEATS:
            raise RhythmError("未知音符类型：%r" % (self.kind,))

    @property
    def beats(self) -> float:
        value = NOTE_BEATS[self.kind]
        return value * 1.5 if self.dotted else value

    @property
    def label(self) -> str:
        return ("附点" if self.dotted else "") + NOTE_LABELS[self.kind]


def parse_note(text: str) -> RhythmNote:
    """解析 quarter、dotted half、附点二分音符等写法。"""
    if not isinstance(text, str):
        raise RhythmError("音符必须是字符串")
    cleaned = text.strip().lower().replace("-", " ")
    if not cleaned:
        raise RhythmError("音符不能为空")
    dotted = False
    if "附点" in cleaned:
        dotted = True
        cleaned = cleaned.replace("附点", "").strip()
    if cleaned.startswith("dotted "):
        dotted = True
        cleaned = cleaned[len("dotted "):].strip()
    if cleaned.endswith("."):
        dotted = True
        cleaned = cleaned[:-1].strip()
    cleaned = " ".join(cleaned.split())
    if cleaned not in _ALIASES:
        raise RhythmError("未知音符：%s" % text)
    return RhythmNote(_ALIASES[cleaned], dotted)


def format_note(note: RhythmNote) -> str:
    return note.label


@dataclass(frozen=True)
class TimeSignature:
    """拍号，measure_beats 统一换算成四分音符拍数。"""

    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if self.numerator < 1 or self.numerator > 16:
            raise RhythmError("拍号分子必须在 1 到 16 之间")
        if self.denominator not in (1, 2, 4, 8, 16):
            raise RhythmError("拍号分母必须是 1、2、4、8 或 16")

    @property
    def measure_beats(self) -> float:
        return self.numerator * 4.0 / self.denominator

    @property
    def label(self) -> str:
        return "%d/%d" % (self.numerator, self.denominator)


def parse_signature(text: str) -> TimeSignature:
    if not isinstance(text, str):
        raise RhythmError("拍号必须是字符串")
    match = _SIGNATURE.match(text.strip())
    if not match:
        raise RhythmError("拍号格式应为 4/4 或 6/8")
    return TimeSignature(int(match.group(1)), int(match.group(2)))


def measure_total(notes: Sequence[RhythmNote]) -> float:
    return sum(note.beats for note in notes)


def missing_beats(notes: Sequence[RhythmNote], signature: TimeSignature) -> float:
    """补满一小节还差多少拍；超出返回负数。"""
    return round(signature.measure_beats - measure_total(notes), 6)


def is_complete(notes: Sequence[RhythmNote], signature: TimeSignature) -> bool:
    return abs(missing_beats(notes, signature)) < 1e-9


@dataclass(frozen=True)
class RhythmItem:
    """一道“还差几拍”的题。"""

    notes: Tuple[RhythmNote, ...]
    signature: TimeSignature

    @property
    def total(self) -> float:
        return measure_total(self.notes)

    @property
    def answer(self) -> float:
        return round(self.signature.measure_beats - self.total, 6)

    @property
    def answer_text(self) -> str:
        return format_beats(self.answer)


def format_beats(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return "%d 拍" % int(round(value))
    return ("%s 拍" % ("%.2f" % value).rstrip("0").rstrip("."))


def _decompose(target: float, rng: random.Random) -> List[RhythmNote]:
    notes: List[RhythmNote] = []
    remaining = round(target, 6)
    while remaining > 1e-9:
        candidates = [
            kind for kind in NOTE_ORDER if NOTE_BEATS[kind] <= remaining + 1e-9
        ]
        if not candidates:
            return []
        kind = rng.choice(candidates)
        notes.append(RhythmNote(kind))
        remaining = round(remaining - NOTE_BEATS[kind], 6)
    return notes


def build_worksheet(
    count: int,
    signature: str = "4/4",
    seed: Optional[int] = None,
) -> List[RhythmItem]:
    """生成“补满小节”题，答案在 0.25 到 3.75 拍之间。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise RhythmError("题目数量必须是正整数")
    sig = parse_signature(signature)
    measure = sig.measure_beats
    if measure < 1:
        raise RhythmError("每小节至少要有 1 拍")
    rng = random.Random(seed)
    items: List[RhythmItem] = []
    seen = set()
    attempts = 0
    limit = count * 500 + 500
    possible_gaps = [round(value * 0.25, 2) for value in range(1, int(measure * 4))]
    while len(items) < count and attempts < limit:
        attempts += 1
        gap = rng.choice(possible_gaps)
        notes = _decompose(round(measure - gap, 6), rng)
        if not notes:
            continue
        key = (tuple((note.kind, note.dotted) for note in notes), gap)
        if key in seen:
            continue
        seen.add(key)
        items.append(RhythmItem(tuple(notes), sig))
    if len(items) < count:
        raise RhythmError("可用的不重复题目不足 %d 道" % count)
    return items


def parse_beats(text: str) -> float:
    """解析 1、0.5 或 1/2 这样的拍数。"""
    if not isinstance(text, str) or not text.strip():
        raise RhythmError("答案不能为空")
    cleaned = text.strip().replace("拍", "").strip()
    try:
        if "/" in cleaned:
            numerator, denominator = cleaned.split("/")
            value = Fraction(int(numerator), int(denominator))
            number = float(value)
        else:
            number = float(cleaned)
    except (ValueError, ZeroDivisionError):
        raise RhythmError("答案必须是数字或分数")
    if not math.isfinite(number) or number <= 0:
        raise RhythmError("答案必须是正数")
    return number


def check_answer(item: RhythmItem, text: str, tolerance: float = 1e-6) -> bool:
    try:
        value = parse_beats(text)
    except RhythmError:
        return False
    return abs(value - item.answer) <= tolerance


def note_table() -> List[Tuple[str, float]]:
    return [(NOTE_LABELS[kind], NOTE_BEATS[kind]) for kind in NOTE_ORDER]
