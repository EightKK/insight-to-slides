# insight-to-slides

[![test](https://github.com/EightKK/insight-to-slides/actions/workflows/test.yml/badge.svg)](https://github.com/EightKK/insight-to-slides/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

根拠に基づく日本語のビジネスプレゼン資料・報告書を設計し、検証するための [Agent Skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) です。

> An agent skill for designing and verifying evidence-grounded Japanese business decks and reports. The agent instructions (`SKILL.md`) are in English; all reader-facing output is Japanese by default.

決算分析、月次の工場会議資料、経営会議向けの意思決定資料など、「数字を読み違えず、結論が一目で伝わり、最後に判断できる」資料を作るための手順とチェックをまとめています。

## できること

- **論証を先に組み立てる。** 主要な問い、現時点の答え、対立仮説、撤回条件付きの意思決定の選択肢を整理してから、見出しとレイアウトに進みます。
- **数字を検証する。** 事実・解釈・仮説・予測を区別し、主要な比率・差分・構成比を再計算します。`%` と `pt` の混同、予測と実績の取り違え、合算できないセグメントの合算を検出します。
- **図表を問いから選ぶ。** 読み手の問いに合わせて図表パターンを選びます（`patterns/catalog.json`）。
- **自然な日本語で書く。** 根拠や限定条件を削らずに、定型的な言い回し（「重要なのは〜」など）を避けたビジネス文章にします。
- **描画結果を検査する。** 書き出した PDF のテキスト、配置、棒グラフの向きを機械的に確認し、エージェントに全ページの目視確認を求めます。
- **制作記録を成果物に混ぜない。** 監査結果、ログ、ツール名などが読み手向けの資料に入り込んでいないかを確認します。

### できないこと

- **スライドの描画はしません。** 描画はホスト環境の手段（Claude のスライド Artifact、PPTX スキル、python-pptx など）に任せます。このスキルは「何をどう伝えるか」の設計と、描画後の検証を担います。
- チェックが確認するのは構造と計算だけです。出典が正しいこと、因果が本当であること、読み手が理解できることまでは保証しません。

## 使い方の例

スキルを導入したら、エージェントに普段どおり依頼してください。内容に応じて自動で読み込まれます。

```text
添付した決算短信と説明資料から、取締役会向けに 10 枚程度の決算分析資料を作って。
```

```text
data/ にある販売・生産・在庫の CSV から、来週の工場月次会議の資料を作って。増産するかどうかを決めたい。
```

```text
この既存資料をレビューして、結論が伝わりにくいページと数字の誤りを指摘して。
```

依頼の重さに応じて、エージェントは 3 段階のティア（Light / Standard / Full）から手順を選び、どのティアで進めるかを最初に伝えます。

| ティア | 想定する依頼 | 主なチェック |
| --- | --- | --- |
| Light | 既存資料の整形・変換、短い報告 | ブリーフ検証、日本語スタイル、描画検査、制作記録の混入 |
| Standard | 手元データの分析、判断を求める資料 | Light ＋ 論証の質、再計算、図表の意味検査 |
| Full | Web 調査を伴う分析、取締役会・社外向け、投資判断 | Standard ＋ 調査ゲート（未解消の重要論点があれば保留） |

## インストール

### Claude Code

個人のスキルとして導入する場合：

```bash
# macOS / Linux
git clone https://github.com/EightKK/insight-to-slides.git ~/.claude/skills/insight-to-slides
```

```powershell
# Windows (PowerShell)
git clone https://github.com/EightKK/insight-to-slides.git "$HOME\.claude\skills\insight-to-slides"
```

特定のプロジェクトだけで使う場合は、プロジェクト直下の `.claude/skills/insight-to-slides` に置きます。

```bash
git clone https://github.com/EightKK/insight-to-slides.git .claude/skills/insight-to-slides
```

Claude Code はスキルのフォルダを監視しているため、再起動しなくても認識されます。ただし `skills` フォルダ自体を新しく作った場合は、`/reload-skills` を実行してください。

### Claude.ai / Claude デスクトップアプリ

1. このリポジトリを ZIP でダウンロードします（**Code → Download ZIP**）。
2. 展開すると `insight-to-slides-main` というフォルダになるので、`insight-to-slides` に名前を変えてから ZIP に圧縮し直します。フォルダ名がスキル名と一致しないとアップロードに失敗します。
3. **Customize → Skills** を開き、**+ → Create skill → Upload a skill** から ZIP をアップロードします。

スキルを使うには、**Settings → Capabilities** でコード実行（ファイルの作成と編集）を有効にしておく必要があります。Team / Enterprise プランでは、管理者がスキルの作成を許可している必要があります。

### その他のエージェント

`SKILL.md` と `references/` などのフォルダ一式をエージェントが読める場所に置き、`SKILL.md` を指示として読み込ませてください。

## 必要な環境

検証スクリプトを使うには次が必要です。

- Python 3.9 以上
- `pip install -r requirements.txt`（PyMuPDF、Pillow、jsonschema）
- LibreOffice（任意）：PPTX ファイルを直接検査するときだけ必要です。`soffice` を PATH に通すか、環境変数 `SOFFICE` に実行ファイルのパスを設定してください。PDF を入力にする場合は不要です。

スクリプトの終了コードは共通です：`0` = 合格、`1` = 不合格または入力エラー、`2` = 保留（要確認）。

## 構成

| パス | 内容 |
| --- | --- |
| `SKILL.md` | エージェント向け指示：常時適用ルール、モードとティアの選択、ワークフロー、スクリプト一覧、参照マップ |
| `references/` | 必要に応じて読み込む詳細ガイド |
| `patterns/catalog.json` | 図表パターンの定義 |
| `schemas/` | 各制作物の JSON Schema |
| `scripts/` | 決定的なチェック |
| `examples/` | 各制作ファイルのテンプレート（架空の事例と実在企業の事例1件） |
| `tests/` | 単体テストと回帰テスト（`tests/fixtures/` は回帰データ専用） |

## ライセンス

[MIT](LICENSE)。実在企業（トヨタ自動車、コマツ、ASML、Sandvik）の事例は、公開資料をもとにしたある時点の例示です。各社とは関係がなく、最新の数値は各社の開示資料で確認してください。
