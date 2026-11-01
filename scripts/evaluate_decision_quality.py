#!/usr/bin/env python3
"""Deterministic evidence-to-decision structural QA for an argumentation contract.

Usage: python3 scripts/evaluate_decision_quality.py argumentation-contract.json [--out decision-review.json]

Validates against schemas/argumentation-contract.schema.json, then checks answer
coverage, evidence links, competing hypotheses, placeholder text and decision options.
Does not verify source truth or causal validity.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, dumps, read_json, run, schema_errors, write_text

PLACEHOLDER_WORD = re.compile(r'\b(?:TBD|TBA|TODO|FIXME|XXX+|lorem ipsum)\b', re.IGNORECASE)
PLACEHOLDER_WHOLE = re.compile(r'^(?:x+|\?+|-+|…+|\.+|n/?a|none|null|未定|未記入|検討中|調整中|要確認|なし|同上)$', re.IGNORECASE)


def placeholder_reason(text, min_len):
    """Return why `text` looks like a placeholder, or None."""
    if not isinstance(text, str) or not text.strip():
        return 'empty'
    s = text.strip()
    if PLACEHOLDER_WORD.search(s):
        return 'placeholder token'
    if PLACEHOLDER_WHOLE.match(s):
        return 'placeholder value'
    if len(s) < min_len:
        return f'shorter than {min_len} characters'
    return None


def evaluate(data: dict) -> dict:
    errors, warnings = [], []

    def err(code, msg):
        errors.append({'code': code, 'detail': msg})

    def warn(code, msg):
        warnings.append({'code': code, 'detail': msg})

    def text_check(value, where, min_len):
        reason = placeholder_reason(value, min_len)
        if reason:
            err('PLACEHOLDER_TEXT', f'{where}: {reason}')

    if not isinstance(data, dict):
        err('SCHEMA', 'top-level value must be an object')
        return _result(errors, warnings, {})
    for e in schema_errors(data, 'argumentation-contract.schema.json'):
        err('SCHEMA', e)
    if errors:  # structure is unreliable; semantic checks would only add noise or crash
        return _result(errors, warnings, data)

    text_check(data['governing_question'], 'governing_question', 10)
    text_check(data['current_answer'], 'current_answer', 15)
    evidence_ids = [x['id'] for x in data['evidence']]
    claim_ids = [x['id'] for x in data['claims']]
    hypothesis_ids = [x['id'] for x in data['hypotheses']]
    for what, ids in [('EVIDENCE', evidence_ids), ('CLAIM', claim_ids), ('HYPOTHESIS', hypothesis_ids),
                      ('QUESTION', [q['id'] for q in data['questions']])]:
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if dup:
            err('DUPLICATE_' + what, f'Duplicate IDs: {dup}')
    evid, claims = set(evidence_ids), set(claim_ids)
    for e in data['evidence']:
        text_check(e['source'], f'evidence {e["id"]}.source', 3)
        text_check(e['summary'], f'evidence {e["id"]}.summary', 8)
    for c in data['claims']:
        text_check(c['text'], f'claim {c["id"]}.text', 8)
        refs = c['evidence_ids']
        if c['kind'] in ('fact', 'interpretation', 'recommendation') and not refs:
            err('UNSUPPORTED_CLAIM', c['id'])
        for ref in refs:
            if ref not in evid:
                err('UNKNOWN_EVIDENCE', f'{c["id"]}: {ref}')
        if c['causal_basis'] in ('hypothesis', 'association_only') and c['kind'] == 'fact':
            err('CAUSAL_OVERCLAIM', f'{c["id"]}: factual assertion with non-causal basis')
        if c['causal_basis'] == 'hypothesis' and not (c.get('qualification') or '').strip():
            err('UNQUALIFIED_CAUSAL_HYPOTHESIS', c['id'])

    questions = data['questions']
    if not any(q.get('governing', False) for q in questions):
        err('GOVERNING_NOT_COVERED', 'No question marked as governing')
    for q in questions:
        text_check(q['answer'], f'question {q["id"]}.answer', 8)
        if q['status'] in ('conditional', 'unanswerable') and not (q.get('limitation') or '').strip():
            err('UNCERTAINTY_NOT_DECLARED', q['id'])
        if q['status'] != 'unanswerable' and not q['supporting_claim_ids']:
            err('NO_SUPPORTING_CLAIMS', q['id'])
        for cid in q['supporting_claim_ids']:
            if cid not in claims:
                err('UNKNOWN_CLAIM', f'{q["id"]}: {cid}')

    for h in data['hypotheses']:
        text_check(h['text'], f'hypothesis {h["id"]}.text', 8)
        text_check(h['falsifier'], f'hypothesis {h["id"]}.falsifier', 8)
        for kind in ('supporting_evidence_ids', 'counter_evidence_ids'):
            for ref in h[kind]:
                if ref not in evid:
                    err('UNKNOWN_HYPOTHESIS_EVIDENCE', f'{h["id"]}: {ref}')
        if not h['supporting_evidence_ids']:
            err('UNTESTED_HYPOTHESIS', h['id'])
        overlap = sorted(set(h['supporting_evidence_ids']) & set(h['counter_evidence_ids']))
        if overlap:
            err('SUPPORT_COUNTER_OVERLAP', f'{h["id"]}: {overlap} cited as both support and counter-evidence')
        if not h['counter_evidence_ids']:
            warn('NO_COUNTER_EVIDENCE', f'{h["id"]}: no observed counter-evidence; do not equate this with confirmation')
    texts = [h['text'].strip() for h in data['hypotheses']]
    if len(set(texts)) < len(texts):
        err('DUPLICATE_HYPOTHESIS_TEXT', 'Competing hypotheses must differ')

    decision = data['decision']
    text_check(decision['question'], 'decision.question', 10)
    text_check(decision['working_assessment'], 'decision.working_assessment', 10)
    names = [o['name'].strip().casefold() for o in decision['options']]
    if len(set(names)) < len(names):
        err('DUPLICATE_OPTION', 'Option names must be distinct alternatives')
    for i, o in enumerate(decision['options']):
        if placeholder_reason(o['merit'], 6) or placeholder_reason(o['tradeoff'], 6):
            err('HOLLOW_OPTION', f'{i}: {o["name"]}')
        text_check(o['name'], f'decision.options[{i}].name', 2)
    reversal = [r for r in decision['reversal_conditions'] if not placeholder_reason(r, 8)]
    if not reversal:
        err('NO_REVERSAL_CONDITION', 'Must state what evidence could change judgment')

    used = set()
    for sl in data.get('slides', []):
        for cid in sl['claim_ids']:
            if cid not in claims:
                err('SLIDE_UNKNOWN_CLAIM', f'{sl["id"]}: {cid}')
            used.add(cid)
    key = [c['id'] for c in data['claims'] if c.get('prominence') == 'key']
    if not key:
        warn('NO_KEY_CLAIM', 'No claim is marked prominence=key; slide coverage of the main message is unchecked')
    unshown = [c for c in key if c not in used]
    if unshown:
        err('KEY_CLAIM_NOT_SHOWN', str(unshown))
    return _result(errors, warnings, data)


def _result(errors, warnings, data):
    def n(k):
        v = data.get(k, []) if isinstance(data, dict) else []
        return len(v) if isinstance(v, list) else 0
    return {'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'warnings': warnings,
            'summary': {k: n(k) for k in ('evidence', 'claims', 'questions', 'hypotheses', 'slides')},
            'limitation': 'Structural consistency only; source validity and causal interpretation require independent editorial review.'}


def main(argv=None):
    ap = Parser(description=__doc__)
    ap.add_argument('contract')
    ap.add_argument('--out')
    args = ap.parse_args(argv)
    result = evaluate(read_json(args.contract))
    output = dumps(result)
    if args.out:
        write_text(args.out, output + '\n')
    print(output)
    return EXIT_PASS if result['status'] == 'PASS' else EXIT_FAIL


if __name__ == '__main__':
    run(main)
