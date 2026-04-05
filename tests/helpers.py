import csv
from pathlib import Path


def make_csv_file(tmp_path: Path, filename: str, rows: list[list[str]]) -> Path:
    """テスト用 CSV ファイルを tmp_path に作成して返す。"""
    p = tmp_path / filename
    with open(p, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)
    return p
