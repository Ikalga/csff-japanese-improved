import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from translation_stats import main

from helpers import make_csv_file


class TestTranslationStats(unittest.TestCase):
    """
    translation_stats の main() のテスト。
    sys.argv を patch し、TemporaryDirectory に実ファイルを作成して渡す。
    stdout をキャプチャして出力内容を検証する。
    """

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _run(self, improved_rows, original_rows):
        improved = make_csv_file(self.tmp, "improved.csv", improved_rows)
        original = make_csv_file(self.tmp, "original.csv", original_rows)
        with patch("sys.argv", ["translation_stats.py", str(improved), str(original)]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                return mock_out.getvalue()

    def test_translation_rate(self):
        """日本語列が空でない割合が全体の翻訳率として表示される。"""
        output = self._run(
            improved_rows=[
                ["KEY_A", "English A", "日本語A"],
                ["KEY_B", "English B", ""],
                ["KEY_C", "English C", "日本語C"],
                ["KEY_D", "English D", ""],
            ],
            original_rows=[
                ["KEY_A", "English A", "旧訳A"],
                ["KEY_B", "English B", ""],
                ["KEY_C", "English C", "旧訳C"],
                ["KEY_D", "English D", ""],
            ],
        )
        # 4キー中2つが翻訳済み → 50.0%
        self.assertIn("2 / 4", output)
        self.assertIn("50.0%", output)

    def test_improvement_rate(self):
        """original と異なる翻訳済みキーの割合がプロジェクト改善率として表示される。"""
        output = self._run(
            improved_rows=[
                ["KEY_A", "English A", "改善訳A"],  # 変更あり
                ["KEY_B", "English B", "旧訳B"],    # 変更なし
                ["KEY_C", "English C", "改善訳C"],  # 変更あり
                ["KEY_D", "English D", ""],          # 未翻訳
            ],
            original_rows=[
                ["KEY_A", "English A", "旧訳A"],
                ["KEY_B", "English B", "旧訳B"],
                ["KEY_C", "English C", "旧訳C"],
                ["KEY_D", "English D", ""],
            ],
        )
        # 翻訳済み3件中2件を改善 → 66.7%
        self.assertIn("2 / 3", output)
        self.assertIn("66.7%", output)

    def test_no_missing_keys_no_warning(self):
        """キーが完全に一致する場合は WARNING が出ない。"""
        output = self._run(
            improved_rows=[["KEY_A", "e", "j"], ["KEY_B", "e", "j"]],
            original_rows=[["KEY_A", "e", "j"], ["KEY_B", "e", "j"]],
        )
        self.assertNotIn("WARNING", output)

    def test_missing_in_improved_shows_warning(self):
        """original にあって improved にないキーが WARNING 表示される。"""
        output = self._run(
            improved_rows=[["KEY_A", "e", "j"]],
            original_rows=[["KEY_A", "e", "j"], ["KEY_MISSING", "e", "j"]],
        )
        self.assertIn("WARNING", output)
        self.assertIn("KEY_MISSING", output)

    def test_missing_in_original_shows_warning(self):
        """improved にあって original にないキーが WARNING 表示される。"""
        output = self._run(
            improved_rows=[["KEY_A", "e", "j"], ["KEY_EXTRA", "e", "j"]],
            original_rows=[["KEY_A", "e", "j"]],
        )
        self.assertIn("WARNING", output)
        self.assertIn("KEY_EXTRA", output)

    def test_all_untranslated(self):
        """全キーが未翻訳のとき翻訳率 0.0%、改善率も 0.0% になる。"""
        output = self._run(
            improved_rows=[["KEY_A", "e", ""], ["KEY_B", "e", ""]],
            original_rows=[["KEY_A", "e", ""], ["KEY_B", "e", ""]],
        )
        self.assertIn("0.0%", output)

    def test_original_translation_rate(self):
        """original の日本語訳が空でない割合が公式版の翻訳率として表示される。"""
        output = self._run(
            improved_rows=[
                ["KEY_A", "English A", "改善訳A"],
                ["KEY_B", "English B", "改善訳B"],
                ["KEY_C", "English C", "改善訳C"],
            ],
            original_rows=[
                ["KEY_A", "English A", "旧訳A"],
                ["KEY_B", "English B", ""],
                ["KEY_C", "English C", ""],
            ],
        )
        # original は3キー中1つが翻訳済み → 33.3%
        self.assertIn("1 / 3", output)
        self.assertIn("33.3%", output)

    def test_missing_arg_exits(self):
        """引数が 2つ未満のとき sys.exit が呼ばれる。"""
        with patch("sys.argv", ["translation_stats.py", "only_one"]):
            with self.assertRaises(SystemExit):
                main()


if __name__ == "__main__":
    unittest.main()
