#!/usr/bin/env python3
"""
表記揺れを統一するツール。

Usage:
    python tools/unify_translations.py <csv_file>

Arguments:
    csv_file : 対象の翻訳 CSV ファイル (例: Jp.csv)

動作:
    英語訳が同じで日本語訳が異なるキーのグループを順に表示し、
    統一する訳語を選択または入力すると翻訳ファイルを上書き更新する。
    Enter のみでスキップ、Ctrl+C で中断できる。
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

from utils import read_csv


def find_inconsistencies(entries: dict) -> list[tuple[str, dict]]:
    """
    英語訳が同じで日本語訳が異なるグループを返す。
    Returns:
        [(english, {japanese: [key, ...]}), ...]  日本語訳の種類が多い順
    """
    by_english: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for key, (english, japanese) in entries.items():
        by_english[english][japanese].append(key)

    result = [
        (english, dict(jp_map))
        for english, jp_map in by_english.items()
        if len(jp_map) > 1
    ]
    # 日本語訳の種類が多い順に並べる
    result.sort(key=lambda x: len(x[1]), reverse=True)
    return result


def prompt_choice(english: str, jp_map: dict[str, list], index: int, total: int) -> str | None:
    """
    ユーザーに訳語を選択または入力させ、選択された訳語を返す。
    スキップの場合は None を返す。
    """
    print(f"\n[{index}/{total}] 英語: {english!r}")
    options = list(jp_map.items())
    for i, (jp, keys) in enumerate(options, 1):
        label = repr(jp) if jp else '""  (未訳)'
        print(f"  {i}. {label}")
        for key in keys:
            print(f"       - {key}")

    print()
    print("番号を選択 / 新たな訳を直接入力 / Enter でスキップ")
    try:
        raw = input("> ").strip()
    except EOFError:
        return None

    if not raw:
        return None

    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= len(options):
            return options[n - 1][0]
        print(f"  [WARN] 1〜{len(options)} の番号を入力してください。スキップします。")
        return None

    return raw


def write_csv(filepath: str, entries: dict, order: list) -> None:
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        for key in order:
            english, japanese = entries[key]
            writer.writerow([key, english, japanese])


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print(__doc__)
        sys.exit(1)

    filepath = args[0]
    entries, order = read_csv(filepath)
    inconsistencies = find_inconsistencies(entries)

    if not inconsistencies:
        print("表記揺れは見つかりませんでした。")
        return

    total = len(inconsistencies)
    print(f"表記揺れが {total} 件見つかりました。")

    updated = 0
    try:
        for i, (english, jp_map) in enumerate(inconsistencies, 1):
            chosen = prompt_choice(english, jp_map, i, total)
            if chosen is None:
                continue

            # 該当するすべてのキーを書き換え
            for keys in jp_map.values():
                for key in keys:
                    en, _ = entries[key]
                    entries[key] = (en, chosen)
            updated += 1
    except KeyboardInterrupt:
        print("\n\n中断しました。")

    if updated > 0:
        write_csv(filepath, entries, order)
        print(f"\n{updated} 件を更新し、{filepath} を保存しました。")
    else:
        print("\n変更はありませんでした。")


if __name__ == "__main__":
    main()
