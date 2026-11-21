"""渲染层测试。"""

import unittest

from noteduration.model import RhythmNote, build_worksheet
from noteduration.render import notes_svg, render_worksheet


class NotesSvgTest(unittest.TestCase):
    def test_svg_skeleton(self):
        svg = notes_svg([RhythmNote("quarter")])
        self.assertIn("<svg", svg)
        self.assertIn('role="img"', svg)

    def test_note_ellipses(self):
        svg = notes_svg([RhythmNote("quarter"), RhythmNote("half"), RhythmNote("whole")])
        self.assertEqual(svg.count("<ellipse"), 3)

    def test_stems(self):
        svg = notes_svg([RhythmNote("quarter")])
        self.assertIn("<line", svg)

    def test_whole_has_no_stem(self):
        self.assertNotIn("<line", notes_svg([RhythmNote("whole")]))

    def test_flagged_notes(self):
        self.assertIn("<path", notes_svg([RhythmNote("eighth")]))
        self.assertEqual(notes_svg([RhythmNote("sixteenth")]).count("<path"), 2)

    def test_dotted(self):
        self.assertIn("<circle", notes_svg([RhythmNote("half", True)]))

    def test_empty(self):
        self.assertIn("<svg", notes_svg([]))


class WorksheetTest(unittest.TestCase):
    def test_item_count(self):
        html = render_worksheet(build_worksheet(5, seed=1))
        self.assertEqual(html.count('class="item"'), 5)

    def test_skeleton(self):
        html = render_worksheet(build_worksheet(1, seed=1))
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('<meta charset="utf-8">', html)

    def test_signature_shown(self):
        html = render_worksheet(build_worksheet(2, "3/4", seed=2))
        self.assertIn("3/4", html)

    def test_note_table(self):
        html = render_worksheet(build_worksheet(1, seed=1))
        self.assertIn("全音符", html)
        self.assertIn("十六分音符", html)

    def test_answers_hidden(self):
        html = render_worksheet(build_worksheet(2, seed=3))
        self.assertNotIn("参考答案", html)

    def test_answers_included(self):
        items = build_worksheet(2, seed=3)
        html = render_worksheet(items, include_answers=True)
        self.assertIn("参考答案", html)
        for item in items:
            self.assertIn(item.answer_text, html)

    def test_title_escaped(self):
        html = render_worksheet([], title="<节奏> & 练习")
        self.assertIn("&lt;节奏&gt; &amp; 练习", html)

    def test_empty(self):
        self.assertIn("暂无题目", render_worksheet([]))

    def test_a4_style(self):
        html = render_worksheet(build_worksheet(1, seed=4))
        self.assertIn("size: A4", html)
        self.assertIn("@media print", html)


if __name__ == "__main__":
    unittest.main()
