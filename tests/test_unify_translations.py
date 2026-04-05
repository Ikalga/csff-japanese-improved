"""
unify_translations.py のユニットテスト。

find_inconsistencies と main() を対象とする。
main() は sys.argv・stdin・ファイル I/O をすべて mock/一時ファイルで差し替えて検証する。
"""

import csv
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from unify_translations import find_inconsistencies, main

from helpers import make_csv_file


def read_csv_simple(path: Path) -> list[list[str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


class TestFindInconsistencies(unittest.TestCase):
    """
    find_inconsistencies のテスト。
    entries 辞書を直接渡し、返却されるグループの内容・件数・順序を検証する。
    """

    def test_detects_inconsistency(self):
        """同じ英語で日本語が異なるキーがグループとして検出される。"""
        entries = {
            "KEY_A": ("hello", "こんにちは"),
            "KEY_B": ("hello", "やあ"),
        }
        result = find_inconsistencies(entries)
        self.assertEqual(len(result), 1)
        english, jp_map = result[0]
        self.assertEqual(english, "hello")
        self.assertIn("こんにちは", jp_map)
        self.assertIn("やあ", jp_map)

    def test_no_inconsistency_when_all_same(self):
        """すべてのキーで日本語が一致している場合は空リストを返す。"""
        entries = {
            "KEY_A": ("hello", "こんにちは"),
            "KEY_B": ("hello", "こんにちは"),
        }
        self.assertEqual(find_inconsistencies(entries), [])

    def test_single_key_per_english_not_detected(self):
        """英語が1キーにしか使われていない場合は検出しない。"""
        entries = {
            "KEY_A": ("hello", "こんにちは"),
            "KEY_B": ("goodbye", "さようなら"),
        }
        self.assertEqual(find_inconsistencies(entries), [])

    def test_empty_japanese_included(self):
        """未訳 (空文字) も日本語訳の一種として扱い、差異として検出する。"""
        entries = {
            "KEY_A": ("hello", "こんにちは"),
            "KEY_B": ("hello", ""),
        }
        result = find_inconsistencies(entries)
        self.assertEqual(len(result), 1)
        _, jp_map = result[0]
        self.assertIn("", jp_map)

    def test_case_sensitive_english(self):
        """英語の大文字小文字を区別するため、"Hello" と "hello" は別グループ。"""
        entries = {
            "KEY_A": ("Hello", "こんにちは"),
            "KEY_B": ("hello", "やあ"),
        }
        self.assertEqual(find_inconsistencies(entries), [])

    def test_sorted_by_variant_count(self):
        """日本語訳の種類が多いグループが先頭に来る。"""
        entries = {
            "KEY_A": ("foo", "訳1"),
            "KEY_B": ("foo", "訳2"),
            "KEY_C": ("foo", "訳3"),
            "KEY_D": ("bar", "訳X"),
            "KEY_E": ("bar", "訳Y"),
        }
        result = find_inconsistencies(entries)
        self.assertEqual(result[0][0], "foo")  # 3種 > 2種


class TestMain(unittest.TestCase):
    """
    main() のテスト。
    sys.argv・stdin を patch し、TemporaryDirectory の実ファイルで検証する。
    """

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _run(self, rows, user_inputs):
        """CSV ファイルを作成して main() を実行し、更新後のファイルを返す。"""
        csv_file = make_csv_file(self.tmp, "test.csv", rows)
        stdin_text = "\n".join(user_inputs) + "\n"
        with patch("sys.argv", ["unify_translations.py", str(csv_file)]):
            with patch("builtins.input", side_effect=user_inputs):
                with patch("sys.stdout", new_callable=StringIO):
                    main()
        return csv_file

    def test_select_existing_translation(self):
        """番号選択で既存の訳を選ぶと、全キーが同じ訳に書き換えられる。"""
        csv_file = self._run(
            rows=[
                ["KEY_A", "hello", "こんにちは"],
                ["KEY_B", "hello", "やあ"],
            ],
            user_inputs=["1"],  # "こんにちは" を選択
        )
        result = {row[0]: row[2] for row in read_csv_simple(csv_file)}
        self.assertEqual(result["KEY_A"], "こんにちは")
        self.assertEqual(result["KEY_B"], "こんにちは")

    def test_enter_new_translation(self):
        """新たな訳語を入力すると、全キーがその訳に書き換えられる。"""
        csv_file = self._run(
            rows=[
                ["KEY_A", "hello", "こんにちは"],
                ["KEY_B", "hello", "やあ"],
            ],
            user_inputs=["ハロー"],
        )
        result = {row[0]: row[2] for row in read_csv_simple(csv_file)}
        self.assertEqual(result["KEY_A"], "ハロー")
        self.assertEqual(result["KEY_B"], "ハロー")

    def test_skip_with_enter(self):
        """Enter のみ入力するとスキップされ、ファイルは変更されない。"""
        rows = [
            ["KEY_A", "hello", "こんにちは"],
            ["KEY_B", "hello", "やあ"],
        ]
        csv_file = self._run(rows, user_inputs=[""])
        result = {row[0]: row[2] for row in read_csv_simple(csv_file)}
        self.assertEqual(result["KEY_A"], "こんにちは")
        self.assertEqual(result["KEY_B"], "やあ")

    def test_no_inconsistency(self):
        """表記揺れがない場合はファイルを変更しない。"""
        rows = [
            ["KEY_A", "hello", "こんにちは"],
            ["KEY_B", "hello", "こんにちは"],
        ]
        csv_file = make_csv_file(self.tmp, "no_diff.csv", rows)
        with patch("sys.argv", ["unify_translations.py", str(csv_file)]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
        self.assertIn("見つかりませんでした", mock_out.getvalue())

    def test_out_of_range_number_skips(self):
        """範囲外の番号を入力するとスキップされ、ファイルは変更されない。"""
        rows = [
            ["KEY_A", "hello", "こんにちは"],
            ["KEY_B", "hello", "やあ"],
        ]
        csv_file = self._run(rows, user_inputs=["99"])
        result = {row[0]: row[2] for row in read_csv_simple(csv_file)}
        self.assertEqual(result["KEY_A"], "こんにちは")
        self.assertEqual(result["KEY_B"], "やあ")

    def test_missing_arg_exits(self):
        """引数なしで sys.exit が呼ばれる。"""
        with patch("sys.argv", ["unify_translations.py"]):
            with self.assertRaises(SystemExit):
                main()

    def test_output_preserves_key_order(self):
        """書き換え後もキーの順序が保たれる。"""
        rows = [
            ["KEY_C", "hello", "こんにちは"],
            ["KEY_A", "hello", "やあ"],
            ["KEY_B", "other", "その他"],
        ]
        csv_file = self._run(rows, user_inputs=["1"])
        written = read_csv_simple(csv_file)
        self.assertEqual([r[0] for r in written], ["KEY_C", "KEY_A", "KEY_B"])


if __name__ == "__main__":
    unittest.main()
