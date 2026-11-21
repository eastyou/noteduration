"""音符 SVG 与练习纸渲染。"""

from __future__ import annotations

import html
from typing import Sequence, Tuple

from .model import RhythmItem, RhythmNote, note_table

STYLE = """
@page { size: A4 portrait; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1b2430;
  font-size: 11pt;
  line-height: 1.5;
}
h1 { font-size: 20pt; margin: 0 0 2mm; }
.sub { color: #6b7280; font-size: 10pt; margin: 0 0 4mm; }
.table { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-bottom: 5mm; }
.table th, .table td { border: 0.4pt solid #d7dee6; padding: 1.4mm 2mm; text-align: left; }
.table th { background: #f1f5f9; }
ol.items { margin: 0; padding-left: 7mm; }
li.item { margin-bottom: 6mm; page-break-inside: avoid; }
.head { font-size: 12pt; margin-bottom: 1mm; }
.blank { display: inline-block; min-width: 24mm; border-bottom: 0.8pt solid #1b2430; height: 1.1em; }
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { columns: 2; column-gap: 10mm; padding-left: 8mm; }
.answers li { margin-bottom: 2.2mm; break-inside: avoid; }
.note { color: #6b7280; font-size: 9.5pt; }
svg { display: block; margin: 1mm 0 0 1mm; }
@media print { li.item, .answers li { break-inside: avoid; } }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def _note_shape(note: RhythmNote, x: float, y: float) -> str:
    filled = note.kind not in ("whole", "half")
    fill = "#111827" if filled else "#ffffff"
    parts = [
        '<ellipse cx="%.2f" cy="%.2f" rx="2.4" ry="1.7" transform="rotate(-18 %.2f %.2f)" '
        'fill="%s" stroke="#111827" stroke-width="0.5"/>' % (x, y, x, y, fill)
    ]
    if note.kind != "whole":
        parts.append(
            '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#111827" stroke-width="0.55"/>'
            % (x + 2.2, y - 0.4, x + 2.2, y - 11.0)
        )
    if note.kind in ("eighth", "sixteenth"):
        parts.append(
            '<path d="M %.2f %.2f q 3.6 1.2 2.8 4.6" fill="none" stroke="#111827" stroke-width="0.6"/>'
            % (x + 2.2, y - 11.0)
        )
    if note.kind == "sixteenth":
        parts.append(
            '<path d="M %.2f %.2f q 3.6 1.2 2.8 4.6" fill="none" stroke="#111827" stroke-width="0.6"/>'
            % (x + 2.2, y - 8.0)
        )
    if note.dotted:
        parts.append('<circle cx="%.2f" cy="%.2f" r="0.75" fill="#111827"/>' % (x + 5.2, y - 1.4))
    return "".join(parts)


def notes_svg(notes: Sequence[RhythmNote]) -> str:
    """把一串音符画成一行的 SVG，单位毫米。"""
    count = max(len(notes), 1)
    width = max(60.0, 12.0 * count + 10.0)
    height = 26.0
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.2fmm" height="%.2fmm" '
        'viewBox="0 0 %.2f %.2f" role="img" aria-label="节奏谱">' % (width, height, width, height)
    ]
    for index, note in enumerate(notes):
        x = 9.0 + index * 12.0
        parts.append(_note_shape(note, x, 18.0))
    parts.append("</svg>")
    return "".join(parts)


def _note_table_html() -> str:
    rows = "".join(
        "<tr><td>%s</td><td>%s 拍</td></tr>" % (_escape(label), _escape(str(beats).rstrip("0").rstrip(".")))
        for label, beats in note_table()
    )
    return (
        "<table class=\"table\"><thead><tr><th>音符</th><th>时值</th></tr></thead>"
        "<tbody>%s</tbody></table>" % rows
    )


def render_worksheet(
    items: Sequence[RhythmItem],
    title: str = "音符时值练习",
    include_answers: bool = False,
) -> str:
    """生成节奏练习纸；答案页给出缺少的拍数。"""
    safe_title = _escape(title)
    blocks = []
    for index, item in enumerate(items, start=1):
        blocks.append(
            '<li class="item"><div class="head">%d. 拍号 %s，补满这一小节还差 '
            '<span class="blank"></span></div>%s</li>'
            % (index, _escape(item.signature.label), notes_svg(item.notes))
        )
    body = "".join(blocks) or '<p class="note">暂无题目。</p>'
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % safe_title,
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % safe_title,
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        _note_table_html(),
        '<ol class="items">%s</ol>' % body,
        '<p class="note">提示：附点音符的时值是原音符的 1.5 倍。</p>',
    ]
    if include_answers:
        answers = "".join(
            "<li>%d. %s</li>" % (index, _escape(item.answer_text))
            for index, item in enumerate(items, start=1)
        )
        parts.extend(
            [
                '<section class="answers">',
                "<h2>参考答案</h2>",
                "<ol>%s</ol>" % answers,
                "</section>",
            ]
        )
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)
