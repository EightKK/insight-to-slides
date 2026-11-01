#!/usr/bin/env python3
"""Heuristic Japanese business-prose linter for text, Markdown and PPTX.

Usage: python3 scripts/lint_japanese_style.py draft.md|draft.txt|deck.pptx [--json] [--fail-on-high]

Reports possible style issues; it neither determines authorship nor edits content.
Exit 0 normally; with --fail-on-high, exit 2 (REVIEW REQUIRED) when a pattern repeats
across the deck; exit 1 for unreadable or unsupported input.
"""
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_HOLD, EXIT_PASS, Parser, run

NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PATTERNS = (
    ("importance_staging", re.compile(r"重要なのは|注目すべきは|本質は|改めて問われ|鍵となる|鍵を握る"), "State the concrete finding without announcing its importance."),
    ("empty_praise", re.compile(r"重要な示唆|本質的な価値|大きな進歩|極めて重要|非常に重要|新たな地平"), "Replace generic praise with evidence or omit it."),
    ("empty_closer", re.compile(r"今後(も|は)?(?:継続的に|引き続き)?(?:注視|注目)|引き続き注視|動向が注目される|注視していくことが重要"), "Specify a future measurement, owner or decision; do not merely promise to monitor."),
    ("abstract_slop", re.compile(r"構造的な課題|真の価値|本質的な課題|部門横断的な連携の高度化|解像度を高める"), "Prefer a concrete mechanism or observable business condition."),
    ("wordy_capability", re.compile(r"することができます|することが可能です|行うことができます"), "Use a direct verb where the ability qualifier adds no meaning."),
    ("performative_contrast", re.compile(r"単なる[^。\n]{0,35}ではなく|単に[^。\n]{0,35}ではなく"), "State the preferred claim directly, unless the contrast is analytically necessary."),
    ("rhetorical_warning", re.compile(r"外してはいけない\d*点|の裏で|課題が浮き彫り|逆説が浮き彫り"), "Check whether this rhetorical frame adds information; prefer the measured comparison or an explicit risk."),
)


def load_segments(path: Path):
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return [(n, line.strip()) for n, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1) if line.strip() and not line.startswith('```')]
    if suffix == ".pptx":
        with zipfile.ZipFile(path) as z:
            slides = sorted((s for s in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", s)), key=lambda s: int(re.search(r"slide(\d+)\.xml", s).group(1)))
            items=[]
            for slide in slides:
                idx=int(re.search(r"slide(\d+)\.xml", slide).group(1))
                root=ET.fromstring(z.read(slide))
                for shape in root.iter():
                    if shape.tag.endswith('}sp'):
                        parts=[]
                        for p in shape.iter(NS+'p'):
                            para=''.join(t.text or '' for t in p.iter(NS+'t')).strip()
                            if para: parts.append(para)
                        if parts: items.append((idx, ' '.join(parts)))
            return items
    raise ValueError(f"Unsupported file type: {suffix}. Use .md, .txt or .pptx.")


def inspect_segments(segments):
    findings=[]
    counts={}
    for location, text in segments:
        for kind, pattern, guidance in PATTERNS:
            for hit in pattern.finditer(text):
                findings.append({"location":location,"kind":kind,"matched":hit.group(0),"context":text[:170],"guidance":guidance,"severity":"review"})
                counts[kind]=counts.get(kind,0)+1
        if len(text)>135 and not text.startswith('|'):
            findings.append({"location":location,"kind":"long_segment","matched":str(len(text)),"context":text[:170],"guidance":"Check whether this sentence or slide block can be split without losing necessary qualifications.","severity":"review"})
    repeated={kind:cnt for kind,cnt in counts.items() if cnt>=3}
    if repeated:
        findings.append({"location":"document","kind":"repetitive_deck_voice","matched":repeated,"guidance":"Review repeated formulas across the whole deck, not just individual lines.","severity":"high"})
    return findings


def main(argv=None):
    ap=Parser(description=__doc__)
    ap.add_argument('file',type=Path)
    ap.add_argument('--json',action='store_true',help='Emit machine-readable findings')
    ap.add_argument('--fail-on-high',action='store_true',help='Return exit code 2 for repeated pattern warnings')
    args=ap.parse_args(argv)
    findings=inspect_segments(load_segments(args.file))
    if args.json:
        print(json.dumps({'file':str(args.file),'count':len(findings),'findings':findings},ensure_ascii=False,indent=2))
    else:
        print(f'Japanese style review: {args.file} — {len(findings)} finding(s)')
        for f in findings:
            print(f"[{f['location']}] {f['kind']}: {f['matched']!s} — {f['guidance']}")
    return EXIT_HOLD if args.fail_on_high and any(f['severity']=='high' for f in findings) else EXIT_PASS

if __name__=='__main__': run(main)
