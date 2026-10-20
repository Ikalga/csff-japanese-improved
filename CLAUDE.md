# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

ゲーム「Card Survival: Fantasy Forest」の日本語訳を改善する非公式プロジェクト。成果物はゲームの `StreamingAssets/Localization/Jp.csv` を置き換える CSV ファイルで、`tools/` 配下の Python スクリプトはその翻訳作業を補助するためのもの。

## コマンド

Python 3.10 以上・標準ライブラリのみ（依存パッケージなし）。Windows のシェルでは日本語の出力が文字化けするため、`PYTHONIOENCODING=utf-8` を付けて実行する。

```bash
# 全テスト
python -m unittest discover -s tests -p "test_*.py" -v

# 単一テストファイル / 単一テスト（tests/ をカレントにして実行）
cd tests && python -m unittest test_three_way_merge -v
cd tests && python -m unittest test_three_way_merge.TestClassify.test_conflict -v

# 公式アップデートと改善版の3ウェイマージ（差分を output/ に出力）
python tools/three_way_merge.py Jp-original.csv Jp-new.csv Jp.csv output/diff.csv

# 表記揺れの対話的統一（Jp.csv を上書き）
python tools/unify_translations.py Jp.csv

# 翻訳進捗率の算出（README の「翻訳進捗」欄の更新に使う）
python tools/translation_stats.py Jp.csv Jp-original.csv

# 他言語版 CSV にあって日本語版にないキーを英語のみで末尾に追記
python tools/fill_missing_keys.py Jp-beta.csv Cn.csv
```

## ファイル構成と役割

- `Jp.csv` — 安定版ブランチ向けの成果物。`Jp-beta.csv` — βブランチ向け（動作保証なし）。この2つがリポジトリで管理される主データ。
- `Jp-original.csv` / `Jp-new.csv` / `Jp-beta-original.csv` / `diff.csv` / `output/` — ゲームから取り出した公式ファイルや作業用中間ファイル。`.gitignore` 対象でコミットしない。
- `tools/utils.py` の `read_csv` が全ツール共通の CSV 読み込み処理。`{key: (english, japanese)}` と出現順のキーリストを返す（BOM 除去・前後空白の strip・重複キーは後勝ち）。
- 各ツールは `from utils import read_csv` で同階層 import しているため、`tools/` をパッケージ化せずスクリプトとして直接実行する前提。テストは `sys.path` に `tools/` を挿入して import し、`tests/helpers.py` の `make_csv_file` で一時 CSV を作る。

## CSV 形式

- ヘッダなし、3列 `キー,英語,日本語`。改行 LF。ツールの書き出しは `csv.writer(..., lineterminator="\n")` で統一されている。
- 文字コードは UTF-8。ゲーム同梱の公式 CSV は BOM 付きだが、成果物（`Jp.csv` / `Jp-beta.csv`）は意図的に BOM なしにしている（BOM なしでもゲームは問題なく読み込み、作成も楽なため）。`read_csv` は `utf-8-sig` で読むのでどちらも扱える。成果物に BOM を付け直す必要はない。
- 行順はゲーム同梱ファイルの順序を維持する。`three_way_merge` は新公式の順序 → 削除キー → 改善版のみのキーの順で出力する。
- 約2万行あるため、CSV を丸ごと読み込まず、キーや英語文で grep して該当行だけ扱うこと。

## 翻訳作業の流れ（バージョンアップ対応）

ゲームのアップデートに合わせた `feat/supports-<version>` ブランチにて作業する。

1. 旧公式・新公式の `Jp.csv` をゲームから取り出し、`three_way_merge` で改善版と比較する。
2. 出力の `状態` 列を `conflict` → `official_changed` の優先順で確認し、`Jp.csv` に反映する。`英語変更` が `○` の行は原文が変わっているので訳も見直す。
3. `unify_translations` で表記揺れ（同じ英語に異なる日本語訳）を統一する。
4. `translation_stats` の結果で README の「翻訳進捗」欄と本体バージョン表記を更新する。

方針として、ゲーム内で未使用に見えるキーも「未使用だから訳さない」という判断はしない。未訳の穴埋めより明らかな誤訳の修正を優先している。

## git操作について

- commit / push / ブランチ作成等、リポジトリの状態を変更する git の操作は、ユーザに明示的に指示された場合のみ行う。特に指示がない場合、ユーザが実施するので Claude 側では操作しない。
- git status / git diff / git log 他、参照するだけの操作については自由に使用して構わない。