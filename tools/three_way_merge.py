#!/usr/bin/env python3
"""
3-way merge tool for Japanese translation CSV files.

Usage:
    python three_way_merge.py <old_official> <new_official> <mod> <output>

Arguments:
    old_official : 旧公式 JP CSV
    new_official : 新公式 JP CSV
    mod          : 改善版 JP CSV
    output       : 出力 CSV ファイルパス

出力列:
    キー, 旧英語, 新英語, 旧日本語, 新日本語, 改善版日本語, 英語変更, 状態

状態の値:
    conflict         : 新公式・改善版の両方が別々に変更
    official_changed : 新公式のみ変更
    mod_changed      : 改善版のみ変更
    added            : 新公式で追加されたキー (旧公式に存在しない)
    deleted          : 新公式で削除されたキー (新公式に存在しない)
    mod_only         : 改善版にのみ存在するキー
    untranslated     : いずれのファイルにも日本語訳がない
    unchanged        : 変更なし
"""

import csv
import sys
from collections import Counter
from pathlib import Path

from utils import read_csv


def classify(in_old: bool, in_new: bool, in_mod: bool, old_jp: str, new_jp: str, mod_jp: str) -> str:
    """変更種別を返す。"""
    if not in_old and not in_new:
        return "mod_only"
    if not in_old and in_new:
        return "added"
    if in_old and not in_new:
        return "deleted"

    official_changed = new_jp != old_jp
    mod_changed = in_mod and mod_jp != old_jp

    if official_changed and mod_changed:
        return "conflict"
    elif official_changed:
        return "official_changed"
    elif mod_changed:
        return "mod_changed"
    elif not new_jp and (not in_mod or not mod_jp):
        return "untranslated"
    return "unchanged"


def main():
    args = sys.argv[1:]

    if len(args) != 4:
        print(__doc__)
        sys.exit(1)

    old_path, new_path, mod_path, out_path = args

    print(f"読み込み中: {old_path}")
    old, old_order = read_csv(old_path)
    print(f"読み込み中: {new_path}")
    new, new_order = read_csv(new_path)
    print(f"読み込み中: {mod_path}")
    mod, _ = read_csv(mod_path)

    # 出力行を新公式の順序で生成し、削除キー・mod のみのキーを末尾に追加
    deleted_keys = [k for k in old if k not in new]
    mod_only_keys = [k for k in mod if k not in old and k not in new]
    all_keys = new_order + deleted_keys + mod_only_keys

    rows = []
    for key in all_keys:
        old_entry = old.get(key)
        new_entry = new.get(key)
        mod_entry = mod.get(key)

        old_en = old_entry[0] if old_entry else ""
        old_jp = old_entry[1] if old_entry else ""
        new_en = new_entry[0] if new_entry else ""
        new_jp = new_entry[1] if new_entry else ""
        mod_jp = mod_entry[1] if mod_entry else ""

        english_changed = "○" if old_en != new_en else "-"
        status = classify(key in old, key in new, key in mod, old_jp, new_jp, mod_jp)

        rows.append([
            key,
            old_en,
            new_en,
            old_jp,
            new_jp,
            mod_jp,
            english_changed,
            status,
        ])

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(["キー", "旧英語", "新英語", "旧日本語", "新日本語", "改善版日本語", "英語変更", "状態"])
        writer.writerows(rows)

    # サマリー
    counter = Counter(r[7] for r in rows)
    status_order = ["conflict", "official_changed", "mod_changed", "added", "deleted", "mod_only", "untranslated", "unchanged"]
    print(f"\n出力完了: {out_path}  ({len(rows)} 行)")
    print("-" * 40)
    for status in status_order:
        if status in counter:
            print(f"  {status:<20}: {counter[status]:>6} 行")


if __name__ == "__main__":
    main()
