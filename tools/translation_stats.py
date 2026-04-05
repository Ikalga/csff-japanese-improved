#!/usr/bin/env python3
"""
翻訳進捗を集計するツール。

Usage:
    python tools/translation_stats.py <improved> <original>

Arguments:
    improved : 改善版 CSV (例: Jp.csv)
    original : 公式オリジナル CSV (例: Jp-original.csv)

出力:
    - 全体の翻訳率        : improved の日本語列が空でない数 / キー数
    - プロジェクト改善率  : improved と original で日本語列が異なる数 / improved の日本語列が空でない数
    - 公式版の翻訳率      : original の日本語列が空でない数 / キー数
    - キー不整合チェック  : original にあって improved にないキー、およびその逆
"""

import sys

from utils import read_csv


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print(__doc__)
        sys.exit(1)

    improved_path, original_path = args
    improved, _ = read_csv(improved_path)
    original, _ = read_csv(original_path)

    # --- キー不整合チェック ---
    missing_in_improved = sorted(set(original) - set(improved))
    missing_in_original = sorted(set(improved) - set(original))

    if missing_in_improved:
        print(f"[WARNING] original にあって improved にないキー: {len(missing_in_improved)} 件")
        for key in missing_in_improved:
            print(f"  - {key}")
    if missing_in_original:
        print(f"[WARNING] improved にあって original にないキー: {len(missing_in_original)} 件")
        for key in missing_in_original:
            print(f"  - {key}")
    if missing_in_improved or missing_in_original:
        print()

    # --- 翻訳率の算出 ---
    total_keys = len(improved)
    translated = sum(1 for _, jp in improved.values() if jp)
    translation_rate = translated / total_keys if total_keys else 0.0

    # --- プロジェクト改善率の算出 ---
    improved_count = sum(
        1 for key, (_, jp) in improved.items()
        if jp and original.get(key, ("", ""))[1] != jp
    )
    improvement_rate = improved_count / translated if translated else 0.0

    # --- 公式版翻訳率の算出 ---
    original_total = len(original)
    original_translated = sum(1 for _, jp in original.values() if jp)
    original_rate = original_translated / original_total if original_total else 0.0

    # --- 結果表示 ---
    print(f"全体の翻訳率         : {translated:>6} / {total_keys} ({translation_rate:.1%})")
    print(f"プロジェクト改善率   : {improved_count:>6} / {translated} ({improvement_rate:.1%})")
    print(f"公式版の翻訳率       : {original_translated:>6} / {original_total} ({original_rate:.1%})")


if __name__ == "__main__":
    main()
