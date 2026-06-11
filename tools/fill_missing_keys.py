#!/usr/bin/env python3
"""
不足キー補完ツール。

参照ファイル (他言語版) に存在し、対象ファイル (日本語版) に存在しないキーを
英語訳のみで対象ファイル末尾に追記する。

Usage:
    python tools/fill_missing_keys.py <target_csv> <reference_csv>

Arguments:
    target_csv    : 補完対象の翻訳 CSV (例: Jp-beta.csv)
    reference_csv : 参照する他言語版 CSV (例: Cn.csv)
"""

import csv
import sys
from pathlib import Path

from utils import read_csv


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print(__doc__)
        sys.exit(1)

    target_path, ref_path = args

    print(f"読み込み中: {target_path}")
    target_entries, target_order = read_csv(target_path)
    print(f"  キー数: {len(target_entries)}")

    print(f"読み込み中: {ref_path}")
    ref_entries, ref_order = read_csv(ref_path)
    print(f"  キー数: {len(ref_entries)}")

    missing_keys = [k for k in ref_order if k not in target_entries]
    print(f"\n不足キー数: {len(missing_keys)}")

    if not missing_keys:
        print("不足キーはありません。")
        return

    out = Path(target_path)
    with open(out, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        for key in missing_keys:
            english, _ = ref_entries[key]
            writer.writerow([key, english, ""])

    print(f"\n{len(missing_keys)} 件のキーを {target_path} に追記しました。")
    print("\n追加されたキー (先頭20件):")
    for key in missing_keys[:20]:
        english, _ = ref_entries[key]
        print(f"  {key}: {english}")
    if len(missing_keys) > 20:
        print(f"  ... 他 {len(missing_keys) - 20} 件")


if __name__ == "__main__":
    main()
