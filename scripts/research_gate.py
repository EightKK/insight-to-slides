#!/usr/bin/env python3
"""Deterministic evidence-coverage gate. No search or network requests.

Usage: python3 scripts/research_gate.py research-plan.json evidence-ledger.json
         [--analysis analysis-brief.json] [--allow-open-gaps] [--out gap-report.json]

Validates all inputs against their schemas, then classifies each gap as
covered / pending / unavailable / excluded (the plan's resolution vocabulary).
FAIL: schema errors, false coverage, orphan or unverified evidence behind a conclusion,
future-dated sources, missing rationale for unavailable/excluded gaps.
HOLD: a gap with decision_impact >= 4 is still pending (use --allow-open-gaps to
downgrade this to a warning). Unavailable/excluded high-impact gaps are warnings
that the conclusions must be qualified.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_HOLD, EXIT_PASS, Parser, dumps, parse_date, read_json, run, schema_errors, write_text

HIGH_IMPACT = 4
STATUSES = ['covered', 'pending', 'unavailable', 'excluded']


def validate(plan, ledger, analysis=None, *, allow_open_gaps=False):
    failures, holds, warnings, gaps, conclusions = [], [], [], [], []
    for label, doc, schema in [('plan', plan, 'research-plan.schema.json'), ('ledger', ledger, 'evidence-ledger.schema.json')] + \
            ([('analysis', analysis, 'analysis-brief.schema.json')] if analysis is not None else []):
        failures += [f'schema ({label}): {e}' for e in schema_errors(doc, schema)]
    if failures:
        return _result('FAIL', plan, failures, holds, warnings, gaps, conclusions)

    try:
        as_of = parse_date(plan['as_of'])
    except ValueError:
        failures.append(f"as_of is not a date: {plan['as_of']}")
        as_of = None
    sources = {x['id']: x for x in ledger['sources']}
    if len(sources) != len(ledger['sources']):
        failures.append('Duplicate source IDs')
    obs = {x['id']: x for x in ledger['observations']}
    if len(obs) != len(ledger['observations']):
        failures.append('Duplicate observation IDs')
    for src in ledger['sources']:
        if src.get('published_at'):
            try:
                published = parse_date(src['published_at'])
                if as_of and published > as_of:
                    failures.append(f"Future source relative to as_of: {src['id']}")
            except ValueError:
                failures.append(f"Unparseable published_at for {src['id']}: {src['published_at']}")
    for item in ledger['observations']:
        if item['source_id'] not in sources:
            failures.append(f"Orphan observation: {item['id']}")

    def verified(eid):
        return eid in obs and obs[eid]['status'] == 'verified'

    ids = [g['id'] for g in plan['gaps']]
    if len(ids) != len(set(ids)):
        failures.append('Duplicate gap IDs')
    for gap in plan['gaps']:
        missing = [x for x in gap['required_evidence_ids'] if not verified(x)]
        declared = gap['resolution']
        status = 'covered' if not missing else ('pending' if declared == 'covered' else declared)
        if declared == 'covered' and missing:
            failures.append(f"False coverage: {gap['id']}, missing {missing}")
        if declared in ('unavailable', 'excluded') and not (gap.get('limitation') or '').strip():
            failures.append(f"{declared.capitalize()} gap requires an explicit limitation: {gap['id']}")
        if status != 'covered' and gap['decision_impact'] >= HIGH_IMPACT:
            msg = f"HIGH-IMPACT GAP: {gap['id']} {status}"
            if status == 'pending' and not allow_open_gaps:
                holds.append(msg + ' - retrieve evidence, weaken the claim, or declare it unavailable/excluded with a limitation')
            else:
                warnings.append(msg + ' - must qualify decision conclusions')
        gaps.append({'id': gap['id'], 'status': status, 'declared_resolution': declared,
                     'missing_evidence_ids': missing, 'decision_impact': gap['decision_impact'],
                     'retrieval_priority': round(gap['decision_impact'] / max(1, gap['retrieval_cost']), 2),
                     'limitation': gap.get('limitation', '')})
    if analysis is not None:
        for c in analysis['conclusions']:
            misses = [x for x in c['evidence_ids'] if not verified(x)]
            if not c['evidence_ids']:
                failures.append(f"Conclusion without evidence: {c['id']}")
            if misses:
                failures.append(f"Unverified conclusion {c['id']}: {misses}")
            conclusions.append({'id': c['id'], 'supported_by_verified': bool(c['evidence_ids']) and not misses})
        for h in analysis['hypotheses']:
            for eid in h['evidence_ids'] + h['counterevidence_ids']:
                if eid not in obs:
                    failures.append(f"Unknown hypothesis observation: {h['id']}/{eid}")
            if h['status'] == 'supported' and h['confidence'] == 'high' and not h['counterevidence_ids']:
                warnings.append(f"Unchallenged high-confidence hypothesis: {h['id']}")
    status = 'FAIL' if failures else ('HOLD' if holds else 'PASS')
    return _result(status, plan, failures, holds, warnings, gaps, conclusions)


def _result(status, plan, failures, holds, warnings, gaps, conclusions):
    return {'status': status, 'ok': status == 'PASS', 'mode': plan.get('mode') if isinstance(plan, dict) else None,
            'as_of': plan.get('as_of') if isinstance(plan, dict) else None,
            'gap_counts': {s: sum(g['status'] == s for g in gaps) for s in STATUSES},
            'gaps': gaps, 'conclusions': conclusions, 'failures': failures, 'holds': holds, 'warnings': warnings,
            'human_comprehension_test': 'NOT PERFORMED'}


def main(argv=None):
    ap = Parser(description=__doc__)
    ap.add_argument('plan')
    ap.add_argument('ledger')
    ap.add_argument('--analysis')
    ap.add_argument('--allow-open-gaps', action='store_true', help='report pending high-impact gaps as warnings instead of HOLD')
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    result = validate(read_json(a.plan), read_json(a.ledger), read_json(a.analysis) if a.analysis else None,
                      allow_open_gaps=a.allow_open_gaps)
    payload = dumps(result) + '\n'
    if a.out:
        write_text(a.out, payload)
    print(payload)
    return {'PASS': EXIT_PASS, 'HOLD': EXIT_HOLD}.get(result['status'], EXIT_FAIL)


if __name__ == '__main__':
    run(main)
