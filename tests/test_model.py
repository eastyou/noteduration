"""模型层测试。"""

import unittest

from noteduration.model import (
    RhythmError,
    RhythmItem,
    RhythmNote,
    TimeSignature,
    build_worksheet,
    check_answer,
    format_beats,
    is_complete,
    measure_total,
    missing_beats,
    note_table,
    parse_beats,
    parse_note,
    parse_signature,
)


class NoteValueTest(unittest.TestCase):
    def test_whole(self):
        self.assertEqual(RhythmNote("whole").beats, 4.0)

    def test_half(self):
        self.assertEqual(RhythmNote("half").beats, 2.0)

    def test_quarter(self):
        self.assertEqual(RhythmNote("quarter").beats, 1.0)

    def test_eighth(self):
        self.assertEqual(RhythmNote("eighth").beats, 0.5)

    def test_sixteenth(self):
        self.assertEqual(RhythmNote("sixteenth").beats, 0.25)

    def test_dotted_half(self):
        self.assertEqual(RhythmNote("half", True).beats, 3.0)

    def test_dotted_quarter(self):
        self.assertEqual(RhythmNote("quarter", True).beats, 1.5)

    def test_dotted_eighth(self):
        self.assertEqual(RhythmNote("eighth", True).beats, 0.75)

    def test_label(self):
        self.assertEqual(RhythmNote("half").label, "二分音符")
        self.assertEqual(RhythmNote("half", True).label, "附点二分音符")

    def test_invalid_kind(self):
        with self.assertRaises(RhythmError):
            RhythmNote("trill")

    def test_note_table(self):
        table = note_table()
        self.assertEqual(len(table), 5)
        self.assertEqual(table[0], ("全音符", 4.0))


class ParseNoteTest(unittest.TestCase):
    def test_english(self):
        self.assertEqual(parse_note("quarter").kind, "quarter")

    def test_chinese(self):
        self.assertEqual(parse_note("八分音符").kind, "eighth")

    def test_dotted_english(self):
        note = parse_note("dotted half")
        self.assertEqual(note.kind, "half")
        self.assertTrue(note.dotted)

    def test_trailing_dot(self):
        self.assertTrue(parse_note("quarter.").dotted)

    def test_chinese_dotted(self):
        note = parse_note("附点二分音符")
        self.assertEqual(note.kind, "half")
        self.assertTrue(note.dotted)

    def test_uppercase(self):
        self.assertEqual(parse_note("SIXTEENTH").kind, "sixteenth")

    def test_unknown(self):
        with self.assertRaises(RhythmError):
            parse_note("breve")

    def test_empty(self):
        with self.assertRaises(RhythmError):
            parse_note("  ")

    def test_non_string(self):
        with self.assertRaises(RhythmError):
            parse_note(1)


class SignatureTest(unittest.TestCase):
    def test_four_four(self):
        self.assertEqual(parse_signature("4/4").measure_beats, 4.0)

    def test_three_four(self):
        self.assertEqual(parse_signature("3/4").measure_beats, 3.0)

    def test_six_eight(self):
        self.assertEqual(parse_signature("6/8").measure_beats, 3.0)

    def test_two_two(self):
        self.assertEqual(parse_signature("2/2").measure_beats, 4.0)

    def test_label(self):
        self.assertEqual(parse_signature("6/8").label, "6/8")

    def test_spaces(self):
        self.assertEqual(parse_signature(" 4 / 4 ").numerator, 4)

    def test_bad_format(self):
        with self.assertRaises(RhythmError):
            parse_signature("4-4")

    def test_bad_numerator(self):
        with self.assertRaises(RhythmError):
            parse_signature("0/4")

    def test_bad_denominator(self):
        with self.assertRaises(RhythmError):
            parse_signature("4/3")


class MeasureTest(unittest.TestCase):
    def test_total(self):
        notes = [RhythmNote("half"), RhythmNote("quarter"), RhythmNote("eighth")]
        self.assertEqual(measure_total(notes), 3.5)

    def test_missing(self):
        signature = parse_signature("4/4")
        notes = [RhythmNote("half"), RhythmNote("quarter")]
        self.assertAlmostEqual(missing_beats(notes, signature), 1.0)

    def test_complete(self):
        signature = parse_signature("4/4")
        notes = [RhythmNote("whole")]
        self.assertTrue(is_complete(notes, signature))

    def test_incomplete(self):
        signature = parse_signature("4/4")
        notes = [RhythmNote("half")]
        self.assertFalse(is_complete(notes, signature))

    def test_overflow_negative(self):
        signature = parse_signature("3/4")
        notes = [RhythmNote("whole")]
        self.assertAlmostEqual(missing_beats(notes, signature), -1.0)


class WorksheetTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_worksheet(6, seed=1)), 6)

    def test_gap_positive(self):
        for item in build_worksheet(10, seed=2):
            self.assertGreater(item.answer, 0)

    def test_gap_completes_measure(self):
        signature = parse_signature("4/4")
        for item in build_worksheet(10, seed=3):
            self.assertAlmostEqual(item.total + item.answer, signature.measure_beats, places=6)

    def test_notes_not_empty(self):
        for item in build_worksheet(10, seed=4):
            self.assertGreaterEqual(len(item.notes), 1)

    def test_deterministic(self):
        first = [(i.notes, i.answer) for i in build_worksheet(6, seed=5)]
        second = [(i.notes, i.answer) for i in build_worksheet(6, seed=5)]
        self.assertEqual(first, second)

    def test_different_seed(self):
        first = [(i.notes, i.answer) for i in build_worksheet(6, seed=5)]
        second = [(i.notes, i.answer) for i in build_worksheet(6, seed=6)]
        self.assertNotEqual(first, second)

    def test_six_eight(self):
        for item in build_worksheet(6, "6/8", seed=7):
            self.assertAlmostEqual(item.total + item.answer, 3.0, places=6)

    def test_invalid_count(self):
        with self.assertRaises(RhythmError):
            build_worksheet(0)

    def test_invalid_signature(self):
        with self.assertRaises(RhythmError):
            build_worksheet(3, "4/3")

    def test_unique(self):
        items = build_worksheet(8, seed=8)
        keys = [(item.notes, item.answer) for item in items]
        self.assertEqual(len(set(keys)), 8)

    def test_item_answer_text(self):
        item = RhythmItem((RhythmNote("half"),), parse_signature("4/4"))
        self.assertEqual(item.answer_text, "2 拍")


class BeatsTest(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(parse_beats("2"), 2.0)

    def test_decimal(self):
        self.assertEqual(parse_beats("1.5"), 1.5)

    def test_fraction(self):
        self.assertEqual(parse_beats("1/2"), 0.5)

    def test_with_unit(self):
        self.assertEqual(parse_beats("3 拍"), 3.0)

    def test_zero_rejected(self):
        with self.assertRaises(RhythmError):
            parse_beats("0")

    def test_negative_rejected(self):
        with self.assertRaises(RhythmError):
            parse_beats("-1")

    def test_text_rejected(self):
        with self.assertRaises(RhythmError):
            parse_beats("two")

    def test_format_integer(self):
        self.assertEqual(format_beats(2.0), "2 拍")

    def test_format_decimal(self):
        self.assertEqual(format_beats(1.5), "1.5 拍")

    def test_check_correct(self):
        item = RhythmItem((RhythmNote("half"),), parse_signature("4/4"))
        self.assertTrue(check_answer(item, "2"))

    def test_check_fraction(self):
        item = RhythmItem((RhythmNote("quarter"), RhythmNote("quarter"), RhythmNote("quarter")), parse_signature("4/4"))
        self.assertTrue(check_answer(item, "1"))

    def test_check_wrong(self):
        item = RhythmItem((RhythmNote("half"),), parse_signature("4/4"))
        self.assertFalse(check_answer(item, "1"))

    def test_check_invalid(self):
        item = RhythmItem((RhythmNote("half"),), parse_signature("4/4"))
        self.assertFalse(check_answer(item, "abc"))

    def test_check_empty(self):
        item = RhythmItem((RhythmNote("half"),), parse_signature("4/4"))
        self.assertFalse(check_answer(item, " "))


if __name__ == "__main__":
    unittest.main()
