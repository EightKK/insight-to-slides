#!/usr/bin/env python3
"""Write a page-by-page English editorial inspection packet from a rendered deck.

Usage: python3 scripts/make_review_packet.py pages_manifest.json --qa QA_DIR --pdf deck.pdf --out packet.md

Exit 0 when the packet is written, 1 on invalid input. Not a gate.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_PASS, Parser, read_json, run, write_text

def make(manifest: list, qa_dir: Path, *, pdf: str) -> str:
    lines=['# Visual & semantic QA packet','',f'Artifact: `{pdf}`','',
           'Inspect the **actual full-resolution image and its 25% thumbnail** for each slide.',
           'Distinguish numerical/structural checks from editorial judgments and a human two-second test.',
           'Do not mark a slide approved until its headline, marks, units, evidence and uncertainty agree.','']
    if isinstance(manifest, dict):
        manifest = manifest['slides']
    for idx, s in enumerate(manifest, 1):
        num=s.get('page_number', idx); image=qa_dir/f'page-{num:02d}.png'
        lines += [f"## {s['slide_id']} — {s['headline']}",'',
                  f"- Image: `{image}`",f"- Intended pattern: `{s.get('pattern_id')}`",
                  '- Expected prominent text: '+', '.join(s.get('visual_tokens',[])),
                  '- Check: first-glance focal point, visible denominators, direction of arrows, warnings, source line, language.',
                  '- Editorial observation: **not automatically assessed**.','']
    lines+=['## Completion statement','',
            '- Machine checks: link the JSON reports.',
            '- Editorial review: record inspected images and concrete corrections, not an invented comprehension score.',
            '- Human two-second test: NOT PERFORMED unless actual viewers were tested.']
    return '\n'.join(lines)+'\n'

def main(argv=None):
    p=Parser(description=__doc__);p.add_argument('manifest');p.add_argument('--qa',required=True);p.add_argument('--pdf',required=True);p.add_argument('--out',required=True);a=p.parse_args(argv)
    write_text(a.out, make(read_json(a.manifest),Path(a.qa),pdf=a.pdf))
    return EXIT_PASS

if __name__=='__main__':run(main)
