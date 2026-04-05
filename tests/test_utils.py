import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from utils import read_csv


class TestReadCsv(unittest.TestCase):
    """
    read_csv のテスト。
    実ファイルを NamedTemporaryFile で作成して渡し、
    BOM・空白・列数不足・空行・行順・重複キーなどの入力バリエーションを検証する。
    """

    def test_basic(self, tmp_path=None):
        """3列の通常行が辞書と順序リストに正しく格納される。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv",
                                         delete=False, newline="") as f:
            f.write("KEY_A,English A,日本語A\nKEY_B,English B,日本語B\n")
            name = f.name
        try:
            entries, order = read_csv(name)
            self.assertEqual(entries["KEY_A"], ("English A", "日本語A"))
            self.assertEqual(entries["KEY_B"], ("English B", "日本語B"))
            self.assertEqual(order, ["KEY_A", "KEY_B"])
        finally:
            os.unlink(name)

    def test_bom_stripped(self):
        """ファイル先頭 BOM および埋め込み U+FEFF がキーから除去される。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8-sig", suffix=".csv",
                                         delete=False, newline="") as f:
            f.write("\ufeffKEY_BOM,English,日本語\n")
            name = f.name
        try:
            entries, order = read_csv(name)
            self.assertIn("KEY_BOM", entries)
            self.assertNotIn("\ufeffKEY_BOM", entries)
            self.assertEqual(order, ["KEY_BOM"])
        finally:
            os.unlink(name)

    def test_whitespace_stripped(self):
        """各フィールドの前後空白が strip される。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv",
                                         delete=False, newline="") as f:
            f.write("  KEY  ,  English  ,  日本語  \n")
            name = f.name
        try:
            entries, order = read_csv(name)
            self.assertIn("KEY", entries)
            self.assertEqual(entries["KEY"], ("English", "日本語"))
        finally:
            os.unlink(name)

    def test_missing_columns(self):
        """列数が 2 のとき japanese が空文字、列数が 1 のとき両方空文字。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv",
                                         delete=False, newline="") as f:
            f.write("KEY_TWO,English only\nKEY_ONE\n")
            name = f.name
        try:
            entries, _ = read_csv(name)
            self.assertEqual(entries["KEY_TWO"], ("English only", ""))
            self.assertEqual(entries["KEY_ONE"], ("", ""))
        finally:
            os.unlink(name)

    def test_empty_lines_skipped(self):
        """空行がスキップされる。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv",
                                         delete=False, newline="") as f:
            f.write("KEY_A,English A,日本語A\n\nKEY_B,English B,日本語B\n")
            name = f.name
        try:
            entries, order = read_csv(name)
            self.assertEqual(len(entries), 2)
            self.assertEqual(order, ["KEY_A", "KEY_B"])
        finally:
            os.unlink(name)

    def test_order_preserved(self):
        """行順リストがファイルの登場順に一致する。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv",
                                         delete=False, newline="") as f:
            f.write("KEY_C,ec,jc\nKEY_A,ea,ja\nKEY_B,eb,jb\n")
            name = f.name
        try:
            _, order = read_csv(name)
            self.assertEqual(order, ["KEY_C", "KEY_A", "KEY_B"])
        finally:
            os.unlink(name)

    def test_duplicate_key_last_wins(self):
        """重複キーは後の行で上書きされ、順序リストへの追加は初回のみ。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv",
                                         delete=False, newline="") as f:
            f.write("KEY_A,English 1,日本語1\nKEY_A,English 2,日本語2\n")
            name = f.name
        try:
            entries, order = read_csv(name)
            self.assertEqual(entries["KEY_A"], ("English 2", "日本語2"))
            self.assertEqual(order.count("KEY_A"), 1)
        finally:
            os.unlink(name)


if __name__ == "__main__":
    unittest.main()
