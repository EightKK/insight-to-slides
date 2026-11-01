#!/usr/bin/env python3
"""Flag internal production and revision language in audience-facing PDFs or text.

Usage: python3 scripts/audience_purity.py final.pdf|draft.md|draft.txt [--out report.json]

Conservative lexical lint, not a semantic judge. Status PASS (exit 0) when nothing
is flagged, REVIEW_REQUIRED (exit 2) otherwise; review flagged excerpts before
publication and avoid false positives when process is genuinely the topic.
PDF text is extracted with PyMuPDF.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_HOLD, EXIT_PASS, Parser, dumps, load_pymupdf, run, write_text

SIGNALS = [
    ("skill_branding", r"Communication\s+Architect|Insight[\s-]*to[\s-]*Slides|\b(?:agent\s+skill|model\s+evaluation)\b|スキル検証|エージェントスキル"),
    ("previous_version", r"旧版との比較|前回(?:の)?資料(?:と|から|を)|従来版(?:との差|との比較)|before\s*/\s*after|改訂(?:前後|版との比較)"),
    ("production_workflow", r"(?:制作|作業|調査)プロセスの自己検証|(?:制作|作業)過程|資料作成前に|研究計画\s*\d+\s*項目|調査方法を説明|(?:スライド|資料)制作の実験"),
    ("internal_quality", r"(?:単体テスト|自動テスト|回帰検証|レンダリング検査|品質ゲート|スキルのテスト)\s*(?:で|が|：|:)?.{0,20}(?:合格|成功|件)|QA\s*(?:レビュー|結果|スコア)"),
    ("version_banner", r"\bv(?:0\.[0-9]+(?:\.[0-9]+)?|[1-9]\.[0-9]+)\b\s*\|\s*(?:深掘り|業績|テスト)|(?:skill|スキル)\s*v[0-9]+\.[0-9]+"),
]


def lint_text(content: str) -> list[dict]:
    issues = []
    for key, pattern in SIGNALS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            start = max(0, match.start() - 30)
            end = min(len(content), match.end() + 35)
            issues.append({"code": key, "match": match.group(0), "context": content[start:end].replace("\n", " ")})
    return issues


def extract(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        pymupdf = load_pymupdf()
        with pymupdf.open(path) as doc:
            return "\n".join(page.get_text("text") for page in doc)
    return path.read_text(encoding="utf-8-sig")


def main(argv=None) -> int:
    parser = Parser(description=__doc__)
    parser.add_argument("file", type=Path, help="PDF or UTF-8 text/Markdown")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    issues = lint_text(extract(args.file))
    payload = {"file": str(args.file), "issues": issues, "issue_count": len(issues),
               "status": "PASS" if not issues else "REVIEW_REQUIRED"}
    if args.out:
        write_text(args.out, dumps(payload) + "\n")
    print(dumps(payload))
    return EXIT_PASS if not issues else EXIT_HOLD


if __name__ == "__main__":
    run(main)
