"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    NOTE_LABELS,
    RhythmError,
    build_worksheet,
    note_table,
    parse_note,
    parse_signature,
)
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="noteduration",
        description="音符时值与小节：计算拍数、补全小节并生成 A4 练习",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("notes", help="列出常用音符时值")

    note_parser = subparsers.add_parser("note", help="查看单个音符")
    note_parser.add_argument("name", help="例如 quarter、dotted half、附点二分音符")

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--signature", default="4/4", help="拍号，默认 4/4")
    sheet_parser.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument("--title", default="音符时值练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加答案页")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "notes":
            for label, beats in note_table():
                print("%-6s %.2f 拍" % (label, beats))
            return 0
        if args.command == "note":
            note = parse_note(args.name)
            print("%s：%.2f 拍" % (note.label, note.beats))
            return 0
        signature = parse_signature(args.signature)
        items = build_worksheet(args.count, signature.label, args.seed)
        _write_output(
            render_worksheet(items, args.title, include_answers=args.answers),
            args.output,
        )
        return 0
    except RhythmError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
