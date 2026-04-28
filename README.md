# csff-japanese-improved
ゲーム [Card Survival: Fantasy Forest](https://store.steampowered.com/app/2868860/Card_Survival_Fantasy_Forest/) の日本語訳改善プロジェクト (非公式) です。

## 翻訳進捗
現在の翻訳完了率は全体の約 77% です。  
うち、当プロジェクトでの改善寄与率は約 37% です。  
参考: 公式版の日本語翻訳率は約 57% です。  
(本体のバージョン: EA_0.60c)

Jp-beta.csv はバージョン EA_beta_0.63b に対応しています。

---

## 導入方法
### 通常
1. 当リポジトリの [Jp.csv](https://github.com/Ikalga/csff-japanese-improved/blob/main/Jp.csv) をダウンロードする
2. `(ゲームインストールフォルダ)/Card Survival - Fantasy Forest_Data/StreamingAssets/Localization/`を開き、`Jp.csv`ファイルを`Jp_bk.csv`等にリネームする
3. ダウンロードしたCSVファイルを同フォルダに上書きコピーする
4. ゲームを起動する

### ベータブランチの場合
当リポジトリの Jp.csv ではなく、Jp-beta.csv をダウンロードし、Jp.csvにリネームした上で上書きコピーしてください。  
ただし、ベータ版については正常動作しない可能性があります。

### Mod Core を使用している場合
> ⚠️ 以下の手順は未検証です。動作しない場合は通常の導入手順をお試しください。

Nexus Mods で公開されている [Mod Core](https://www.nexusmods.com/cardsurvivalfantasyforest/mods/1) を導入済みの場合、ゲームファイルを直接書き換えずに導入できるはずです。

1. 当リポジトリの [Jp.csv](https://github.com/Ikalga/csff-japanese-improved/blob/main/Jp.csv) をダウンロードする
2. `(ゲームインストールフォルダ)/BepInEx/plugins/` の中に `csff-japanese-improved/Localization/` フォルダを作成する
3. ダウンロードした `Jp.csv` を上記フォルダに配置する
4. ゲームを起動する

## 連絡先等
対応状況等は以下blueskyでも発信しています。
https://bsky.app/profile/ikalga.bsky.social

## Q&A

**Q. ××の翻訳、間違ってませんか？**  
A. ぜひ[Issue](../../issues)あるいは[Pull Request](../../pulls)で指摘してください！ Issueであっても修正案まで書いてくれると、とても助かります。

**Q. ××と○○で用語が食い違っているような？**  
A. 指摘ありがとうございます！ 良ければ[Issue](../../issues)に記載お願いします！

**Q. ゲームが起動しなくなった / 文字化けした！**  
A. 環境等を添えて[Issue](../../issues)で報告してもらえると助かります。  
文字化けについてはどこが化けたのかスクリーンショット等もあると嬉しいです。

**Q. △△って項目、ゲームで使われてないのでは？**  
A. 本当に未使用であるかの検証に工数がかかることと、今後のアップデートのために予約された語である可能性を考慮して、「未使用なので訳さない」という判断はしないことにしています。

**Q. 翻訳完了率低くない？**  
A. 2万行のCSVに対して単語の整合性を確認しながらやってるので…… 作業効率を上げる手段について知見があればぜひ教えてください。  
あと今のところ、明らかな誤訳をチェックするのが優先になっていて、未訳の部分を埋めるのは後回しにしています。

---

## 開発者向け
### ツール一覧

| ツール名 | 機能 | 実行コマンドの例 |
|---|---|---|
| three_way_merge | 公式アップデートと翻訳改善の比較・整理 | `python tools/three_way_merge.py Jp-original.csv Jp-new.csv Jp-improved.csv output/diff.csv` |
| unify_translations | 翻訳ファイル内の表記揺れ統一 | `python tools/unify_translations.py Jp.csv` |
| translation_stats | 翻訳進捗率の算出 | `python tools/translation_stats.py Jp.csv Jp-original.csv` |

#### 動作条件

- Python 3.10 以上
- ライブラリ導入等の環境構築はいまのところ不要です

### ツール: three_way_merge

ゲームの公式アップデートと、こちらで行った翻訳改善を比較・整理するために３ウェイマージを実施するツールです。

#### ⚠️注意事項
本ツールの出力内容は 2026/04/17 に変更されました。
英語文の変更について追跡可能にするために、出力列が増えています。ご注意ください。

#### 使い方
「アップデート前の公式日本語化ファイル (旧公式)」「アップデート後の公式日本語化ファイル (新公式)」「翻訳改善版の日本語化ファイル (改善版)」の3つのCSVファイルが必要です。  
公式日本語化ファイルについては、ゲームのインストールフォルダ内にある `jp.csv` をコピーして使用してください。

```bash
python tools/three_way_merge.py <旧公式> <新公式> <改善版> <出力ファイル>
```

**引数**

| 引数 | 説明 | 例 |
|---|---|---|
| 旧公式 | アップデート前のゲーム同梱 `jp.csv` | `Jp-original.csv` |
| 新公式 | アップデート後のゲーム同梱 `jp.csv` | `Jp-new.csv` |
| 改善版 | 翻訳改善済みの `jp.csv` | `Jp-improved.csv` |
| 出力ファイル | 結果を書き出すファイルパス | `output/diff.csv` |

**実行例**

```bash
python tools/three_way_merge.py Jp-original.csv Jp-new.csv Jp-improved.csv output/diff.csv
```

#### 出力ファイルの見方

出力される CSV は以下の列構成です：

| 列 | 内容 |
|---|---|
| キー | ゲーム内のテキスト識別子 |
| 旧英語 | アップデート前の英語原文 |
| 新英語 | アップデート後の英語原文 |
| 旧日本語 | アップデート前の公式日本語訳 |
| 新日本語 | アップデート後の公式日本語訳 |
| 改善版日本語 | こちらで改善した日本語訳 |
| 英語変更 | 英語原文が変化した場合 `○`、変化なしは `-` |
| 状態 | 変更の種別（下表） |

**状態の値**

| 状態 | 意味 |
|---|---|
| `conflict` | 新公式・改善版の両方が、それぞれ異なる内容に変更されている（要確認） |
| `official_changed` | 新公式のみ変更されている（公式アップデートの反映候補） |
| `mod_changed` | 改善版のみ変更されている |
| `added` | 新公式で追加された新しいキー |
| `deleted` | 新公式で削除されたキー |
| `mod_only` | 改善版にのみ存在するキー（旧バージョンの遺物など） |
| `untranslated` | いずれのファイルにも日本語訳がない |
| `unchanged` | 変更なし |

作業の優先度としては、`conflict` → `official_changed` の順に確認することをおすすめします。

---

### ツール: unify_translations

翻訳ファイル内の表記揺れを対話的に統一するツールです。
同じ英語に対して複数の日本語訳が混在しているケースを順に提示し、統一する訳語を選択・入力します。

#### 使い方

```bash
python tools/unify_translations.py <csv_file>
```

**実行例**

```bash
python tools/unify_translations.py Jp.csv
```

**操作方法**

表記揺れが見つかった英語ごとに、以下のように選択肢が表示されます：

```
[1/42] 英語: 'Attack'
  1. "攻撃"
       - ATTACK_ACTION
       - ATTACK_BUTTON
  2. "アタック"
       - ATTACK_LABEL

番号を選択 / 新たな訳を直接入力 / Enter でスキップ
>
```

| 入力 | 動作 |
|---|---|
| 番号（例: `1`） | 対応する既存の訳で全キーを統一 |
| 任意の文字列 | 入力した訳で全キーを統一 |
| Enter（空のまま） | このグループをスキップ |
| Ctrl+C | 中断（それまでの変更は保存される） |

---

### ツール: translation_stats

翻訳進捗率を算出するツールです。README の「翻訳進捗」欄を更新する際に使用します。

#### 使い方

```bash
python tools/translation_stats.py <改善版> <公式オリジナル>
```

**実行例**

```bash
python tools/translation_stats.py Jp.csv Jp-original.csv
```

**出力例**

```
全体の翻訳率         :  11749 / 20453 (57.4%)
プロジェクト改善率   :    786 / 11749 (6.7%)
公式版の翻訳率       :  11571 / 20453 (56.6%)
```

キーの過不足がある場合は `[WARNING]` として件数とキー名が先頭に表示されます。

---

### テストの実行

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## 謝辞
公式の素晴らしい翻訳を作成してくれた[サム・クロノ氏](https://x.com/kurono_studios)と[豊田アレキサンダー氏](https://x.com/AlexanderT78541)に感謝します。  
また、公式日本語訳の発表前に日本語化プロジェクトを進めていた[hirmiura氏](https://github.com/hirmiura/csff-mod-ja-deprecated)に。(当プロジェクトは、hirmiura氏の成果物を一部下敷きに作成されました)  
なにより、素晴らしいゲームを開発してくれた[WinterSpring Games](https://x.com/WinterSpringGm)に。

## 免責
当リポジトリ内のファイル、スクリプト、データを利用することにより生じたいかなる損害についても、当リポジトリの管理者は一切の責任を負いません。
