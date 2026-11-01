#!/usr/bin/env python3
"""Check a rendered PDF against its page manifest (headlines, visual tokens, sources).

Usage: python3 scripts/review_deck.py deck.pdf pages_manifest.json [--observations editorial.json] --out report.json

Manifest: a list (or {"slides": [...]}) of {slide_id, headline, visual_tokens[], evidence_class?}
in page order. Errors (gate fails): page-count mismatch, headline not in the text layer,
any expected visual token missing (tokens are matched sign-explicitly after NFKC
normalisation, so a wrong or unsigned number does not match), contradictory revision
arrows, open editorial issues with severity "error". Missing source footer is a warning.
Does not call a vision model and cannot certify two-second human comprehension.
"""
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, contains_token, dumps, load_pymupdf, normalize_text, read_json, run, write_text

normal = normalize_text  # public alias kept for callers


def upward_revision_direction_conflict(normalized_text: str) -> bool:
    return '上方修正' in normalized_text and ('↓' in normalized_text or '▼' in normalized_text)


def report(pdf_file: Path, manifest_file: Path, *, observation_file: Path = None) -> dict[str, Any]:
    pymupdf = load_pymupdf()
    manifest = read_json(manifest_file)
    if isinstance(manifest, dict):
        manifest = manifest['slides']
    issues, pages = [], []
    with pymupdf.open(pdf_file) as doc:
        page_count = len(doc)
        if page_count != len(manifest):
            issues.append({'severity': 'error', 'type': 'page_count', 'slide': 'DECK',
                           'description': f'{page_count} rendered pages vs {len(manifest)} expected'})
        for idx, p in enumerate(doc):
            if idx >= len(manifest):
                break
            spec = manifest[idx]
            sid = spec['slide_id']
            text = normal(p.get_text('text'))
            headline = normal(spec.get('headline', ''))
            headline_ok = bool(headline) and headline in text
            if not headline_ok:
                issues.append({'severity': 'error', 'type': 'missing_headline', 'slide': sid, 'description': spec.get('headline', '')})
            missing = [str(t) for t in spec.get('visual_tokens', []) if not contains_token(text, t)]
            if missing:
                issues.append({'severity': 'error', 'type': 'missing_visual_tokens', 'slide': sid, 'description': ', '.join(missing)})
            if upward_revision_direction_conflict(text):
                issues.append({'severity': 'error', 'type': 'direction_semantics', 'slide': sid,
                               'description': 'Upward-revision headline conflicts with downward-arrow glyph'})
            if idx > 0 and '出典' not in text and 'Source' not in text and not (
                    spec.get('evidence_class') == 'synthetic_fictional' and '架空' in text):
                issues.append({'severity': 'warning', 'type': 'missing_source_footer', 'slide': sid,
                               'description': 'No explicit source text in the rendered text layer'})
            pages.append({'slide': sid, 'page': idx + 1, 'headline_visible_in_text': headline_ok,
                          'visual_tokens_not_found': missing, 'text_characters': len(text)})
    if observation_file and Path(observation_file).exists():
        observed = read_json(observation_file)
        for o in observed.get('issues', []):
            if o.get('status') not in ('verified_fixed', 'accepted_with_rationale'):
                issues.append({'severity': o.get('severity', 'warning'), 'type': 'editorial_open',
                               'slide': o.get('slide', 'UNKNOWN'), 'description': o.get('observation', '')})
    else:
        observed = {'review_method': 'NOT PERFORMED', 'issues': []}
    counts = {level: sum(i['severity'] == level for i in issues) for level in ('error', 'warning')}
    return {'status': 'PASS' if counts['error'] == 0 else 'FAIL', 'pdf': str(pdf_file), 'manifest': str(manifest_file),
            'page_count': page_count,
            'checks': {'headline_and_label_evidence': 'machine text-layer check; not semantic understanding',
                       'directionality': 'rule-based conflict check for revision arrows',
                       'human_two_second_test': 'NOT PERFORMED',
                       'editorial_visual_review': observed.get('review_method', 'NOT PERFORMED')},
            'pages': pages, 'issues': issues, 'counts': counts, 'pass_machine_gates': counts['error'] == 0}


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('pdf')
    parser.add_argument('manifest')
    parser.add_argument('--observations')
    parser.add_argument('--out', required=True)
    a = parser.parse_args(argv)
    r = report(Path(a.pdf), Path(a.manifest), observation_file=Path(a.observations) if a.observations else None)
    write_text(a.out, dumps(r) + '\n')
    print(dumps({'status': r['status'], 'pages': r['page_count'], 'errors': r['counts']['error'], 'warnings': r['counts']['warning']}))
    return EXIT_PASS if r['status'] == 'PASS' else EXIT_FAIL


if __name__ == '__main__':
    run(main)
