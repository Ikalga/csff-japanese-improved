import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from utils import read_csv

from helpers import make_csv_file


class TestReadCsv(unittest.TestCase):
    """
    read_csv のテスト。
    setUp で TemporaryDirectory を作成し、make_csv_file でテスト用ファイルを用意する。
    BOM・空白・列数不足・空行・行順・重複キーなどの入力バリエーションを検証する。
    """

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_basic(self):
        """3列の通常行が辞書と順序リストに正しく格納される。"""
        f = make_csv_file(self.tmp, "test.csv", [
            ["KEY_A", "English A", "日本語A"],
            ["KEY_B", "English B", "日本語B"],
        ])
        entries, order = read_csv(str(f))
        self.assertEqual(entries["KEY_A"], ("English A", "日本語A"))
        self.assertEqual(entries["KEY_B"], ("English B", "日本語B"))
        self.assertEqual(order, ["KEY_A", "KEY_B"])

    def test_bom_stripped(self):
        """ファイル先頭 BOM および埋め込み U+FEFF がキーから除去される。"""
        p = self.tmp / "bom.csv"
        with open(p, "w", encoding="utf-8-sig", newline="") as f:
            f.write("\ufeffKEY_BOM,English,日本語\n")
        entries, order = read_csv(str(p))
        self.assertIn("KEY_BOM", entries)
        self.assertNotIn("\ufeffKEY_BOM", entries)
        self.assertEqual(order, ["KEY_BOM"])

    def test_whitespace_stripped(self):
        """各フィールドの前後空白が strip される。"""
        p = self.tmp / "ws.csv"
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("  KEY  ,  English  ,  日本語  \n")
        entries, _ = read_csv(str(p))
        self.assertIn("KEY", entries)
        self.assertEqual(entries["KEY"], ("English", "日本語"))

    def test_missing_columns(self):
        """列数が 2 のとき japanese が空文字、列数が 1 のとき両方空文字。"""
        p = self.tmp / "cols.csv"
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("KEY_TWO,English only\nKEY_ONE\n")
        entries, _ = read_csv(str(p))
        self.assertEqual(entries["KEY_TWO"], ("English only", ""))
        self.assertEqual(entries["KEY_ONE"], ("", ""))

    def test_empty_lines_skipped(self):
        """空行がスキップされる。"""
        f = make_csv_file(self.tmp, "test.csv", [
            ["KEY_A", "English A", "日本語A"],
            [],
            ["KEY_B", "English B", "日本語B"],
        ])
        entries, order = read_csv(str(f))
        self.assertEqual(len(entries), 2)
        self.assertEqual(order, ["KEY_A", "KEY_B"])

    def test_order_preserved(self):
        """行順リストがファイルの登場順に一致する。"""
        f = make_csv_file(self.tmp, "test.csv", [
            ["KEY_C", "ec", "jc"],
            ["KEY_A", "ea", "ja"],
            ["KEY_B", "eb", "jb"],
        ])
        _, order = read_csv(str(f))
        self.assertEqual(order, ["KEY_C", "KEY_A", "KEY_B"])

    def test_duplicate_key_last_wins(self):
        """重複キーは後の行で上書きされ、順序リストへの追加は初回のみ。"""
        f = make_csv_file(self.tmp, "test.csv", [
            ["KEY_A", "English 1", "日本語1"],
            ["KEY_A", "English 2", "日本語2"],
        ])
        entries, order = read_csv(str(f))
        self.assertEqual(entries["KEY_A"], ("English 2", "日本語2"))
        self.assertEqual(order.count("KEY_A"), 1)


if __name__ == "__main__":
    unittest.main()
