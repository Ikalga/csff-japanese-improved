import csv
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# tools/ ディレクトリをパスに追加してインポート
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from three_way_merge import classify, main

from helpers import make_csv_file


def read_output_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    """出力 CSV を読み込み (header, rows) を返す。"""
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows[0], rows[1:]


class TestClassify(unittest.TestCase):
    """
    classify のテスト。
    in_old・in_new の有無と old_jp/new_jp/mod_jp の値の組み合わせを網羅し、
    全ステータス（conflict / official_changed / mod_changed / added / deleted /
    mod_only / untranslated / unchanged）が正しく返ることを検証する。
    untranslated と unchanged の境界ケースも明示的に確認する。
    """

    def test_mod_only(self):
        self.assertEqual(classify(False, False, True, "", "", "訳"), "mod_only")

    def test_added(self):
        self.assertEqual(classify(False, True, False, "", "新訳", ""), "added")

    def test_deleted(self):
        self.assertEqual(classify(True, False, False, "旧訳", "", ""), "deleted")

    def test_conflict(self):
        self.assertEqual(classify(True, True, True, "旧訳", "新公式訳", "改善訳"), "conflict")

    def test_official_changed_mod_same_as_old(self):
        self.assertEqual(classify(True, True, True, "旧訳", "新公式訳", "旧訳"), "official_changed")

    def test_official_changed_only(self):
        """改善版が空文字の場合も新公式が変更されていれば official_changed。"""
        self.assertEqual(classify(True, True, False, "旧訳", "新公式訳", ""), "official_changed")

    def test_mod_changed_only(self):
        self.assertEqual(classify(True, True, True, "旧訳", "旧訳", "改善訳"), "mod_changed")

    def test_unchanged(self):
        self.assertEqual(classify(True, True, True, "旧訳", "旧訳", "旧訳"), "unchanged")

    def test_unchanged_mod_absent(self):
        """改善版にキーがない場合も unchanged。"""
        self.assertEqual(classify(True, True, False, "旧訳", "旧訳", ""), "unchanged")

    def test_untranslated(self):
        """新公式・改善版ともに空文字 → untranslated。"""
        self.assertEqual(classify(True, True, True, "", "", ""), "untranslated")

    def test_untranslated_mod_absent(self):
        """改善版にキーがない場合も untranslated。"""
        self.assertEqual(classify(True, True, False, "", "", ""), "untranslated")


class TestMain(unittest.TestCase):
    """
    main のテスト。
    sys.argv を patch し、TemporaryDirectory に実ファイルを作成して main() に渡す。
    出力 CSV の内容・行順・エンコーディング・改行コードを検証する。
    """

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _run_main(self, old_rows, new_rows, mod_rows, out_name="out.csv"):
        old = make_csv_file(self.tmp, "old.csv", old_rows)
        new = make_csv_file(self.tmp, "new.csv", new_rows)
        mod = make_csv_file(self.tmp, "mod.csv", mod_rows)
        out = self.tmp / out_name
        with patch("sys.argv", ["three_way_merge.py", str(old), str(new), str(mod), str(out)]):
            main()
        return out

    def test_normal_run(self):
        """最小構成で main() を実行し、ヘッダーと行内容が正しい。"""
        out = self._run_main(
            old_rows=[["KEY", "English", "旧訳"]],
            new_rows=[["KEY", "English", "旧訳"]],
            mod_rows=[["KEY", "English", "改善訳"]],
        )
        header, rows = read_output_csv(out)
        self.assertEqual(header, ["キー", "旧英語", "新英語", "旧日本語", "新日本語", "改善版日本語", "英語変更", "状態"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], ["KEY", "English", "English", "旧訳", "旧訳", "改善訳", "-", "mod_changed"])

    def test_output_key_order_follows_new(self):
        """出力行の順序が新公式のキー順に一致する。"""
        out = self._run_main(
            old_rows=[["KEY_A", "ea", "ja"], ["KEY_B", "eb", "jb"], ["KEY_C", "ec", "jc"]],
            new_rows=[["KEY_C", "ec", "jc"], ["KEY_A", "ea", "ja"], ["KEY_B", "eb", "jb"]],
            mod_rows=[],
        )
        _, rows = read_output_csv(out)
        keys = [r[0] for r in rows]
        self.assertEqual(keys[:3], ["KEY_C", "KEY_A", "KEY_B"])

    def test_deleted_keys_appended(self):
        """旧公式にあり新公式にないキーが末尾に "deleted" として出力される。"""
        out = self._run_main(
            old_rows=[["KEY_A", "ea", "ja"], ["KEY_DEL", "ed", "jd"]],
            new_rows=[["KEY_A", "ea", "ja"]],
            mod_rows=[],
        )
        _, rows = read_output_csv(out)
        deleted = [r for r in rows if r[7] == "deleted"]
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0][0], "KEY_DEL")
        # deleted キーは新公式キーの後ろ
        keys = [r[0] for r in rows]
        self.assertGreater(keys.index("KEY_DEL"), keys.index("KEY_A"))

    def test_added_keys_included(self):
        """新公式にあり旧公式にないキーが "added" として出力される。"""
        out = self._run_main(
            old_rows=[["KEY_A", "ea", "ja"]],
            new_rows=[["KEY_A", "ea", "ja"], ["KEY_NEW", "en", "jn"]],
            mod_rows=[],
        )
        _, rows = read_output_csv(out)
        added = [r for r in rows if r[7] == "added"]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0][0], "KEY_NEW")

    def test_mod_only_keys_appended(self):
        """改善版にのみ存在するキーが末尾に "mod_only" として出力される。"""
        out = self._run_main(
            old_rows=[["KEY_A", "ea", "ja"]],
            new_rows=[["KEY_A", "ea", "ja"]],
            mod_rows=[["KEY_A", "ea", "改善訳"], ["KEY_MOD", "em", "jm"]],
        )
        _, rows = read_output_csv(out)
        mod_only = [r for r in rows if r[7] == "mod_only"]
        self.assertEqual(len(mod_only), 1)
        self.assertEqual(mod_only[0][0], "KEY_MOD")

    def test_english_changed_flag(self):
        """英語訳が変化したキーは英語変更列が ○、変化しないキーは - になる。"""
        out = self._run_main(
            old_rows=[["KEY_A", "old english", "ja"], ["KEY_B", "same", "jb"]],
            new_rows=[["KEY_A", "new english", "ja"], ["KEY_B", "same", "jb"]],
            mod_rows=[],
        )
        _, rows = read_output_csv(out)
        by_key = {r[0]: r for r in rows}
        self.assertEqual(by_key["KEY_A"][6], "○")
        self.assertEqual(by_key["KEY_B"][6], "-")

    def test_missing_arg_exits(self):
        """引数が 4つ未満のとき sys.exit が呼ばれる。"""
        with patch("sys.argv", ["three_way_merge.py", "only_one_arg"]):
            with self.assertRaises(SystemExit):
                main()

    def test_output_encoding_no_bom(self):
        """出力ファイルが BOM なし UTF-8 で書かれる（先頭バイト確認）。"""
        out = self._run_main(
            old_rows=[["KEY", "English", "旧訳"]],
            new_rows=[["KEY", "English", "旧訳"]],
            mod_rows=[],
        )
        with open(out, "rb") as f:
            head = f.read(3)
        self.assertNotEqual(head, b"\xef\xbb\xbf", "BOM が付いている")

    def test_output_line_ending_lf(self):
        """出力ファイルの改行コードが LF のみ（CR+LF でない）。"""
        out = self._run_main(
            old_rows=[["KEY_A", "ea", "ja"], ["KEY_B", "eb", "jb"]],
            new_rows=[["KEY_A", "ea", "ja"], ["KEY_B", "eb", "jb"]],
            mod_rows=[],
        )
        with open(out, "rb") as f:
            content = f.read()
        self.assertNotIn(b"\r\n", content)
        self.assertIn(b"\n", content)


if __name__ == "__main__":
    unittest.main()
