import csv
import sys
from pathlib import Path


def read_csv(filepath: str) -> tuple[dict, list]:
    """
    CSV を読み込み、キーをインデックスとした辞書と、元の行順リストを返す。
    Returns:
        entries : {key: (english, japanese)}
        order   : [key, ...] 登場順
    """
    entries = {}
    order = []
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] ファイルが見つかりません: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            key = row[0].strip().lstrip('\ufeff')
            english = row[1].strip() if len(row) > 1 else ""
            japanese = row[2].strip() if len(row) > 2 else ""
            if key not in entries:
                order.append(key)
            entries[key] = (english, japanese)

    return entries, order
