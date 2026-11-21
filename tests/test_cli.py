"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from noteduration.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class NotesCommandTest(unittest.TestCase):
    def test_lists_five(self):
        code, out, _ = run_cli(["notes"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 5)

    def test_note_quarter(self):
        code, out, _ = run_cli(["note", "quarter"])
        self.assertEqual(code, 0)
        self.assertIn("四分音符", out)
        self.assertIn("1.00", out)

    def test_note_dotted(self):
        code, out, _ = run_cli(["note", "dotted half"])
        self.assertEqual(code, 0)
        self.assertIn("附点二分音符", out)
        self.assertIn("3.00", out)

    def test_invalid_note(self):
        code, _, err = run_cli(["note", "breve"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class SheetCommandTest(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "6", "--seed", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                html = handle.read()
            self.assertEqual(html.count('class="item"'), 6)

    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_answers(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "3", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_signature(self):
        code, out, _ = run_cli(["sheet", "--signature", "3/4", "--count", "3", "--seed", "4"])
        self.assertEqual(code, 0)
        self.assertIn("3/4", out)

    def test_invalid_signature(self):
        code, _, err = run_cli(["sheet", "--signature", "4/3"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "5", "--seed", "7"])
        _, second, _ = run_cli(["sheet", "--count", "5", "--seed", "7"])
        self.assertEqual(first, second)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "sheet.html")
            code, _, _ = run_cli(["sheet", "--count", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
