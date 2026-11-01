#!/usr/bin/env python3
"""Conservative provenance/scope gate for public-data case studies.

Usage: python3 scripts/audit_public_data.py manifest.json [--out report.json]

Validates against schemas/public-data-manifest.schema.json, then checks that
observed claims do not exceed the observed source granularity and cite a listed
source URL; that claims finer than the sources or of non-observed type are not
presented as confirmed actuals, firm orders or management plans; and that no
observed claim uses a dataset the manifest declares unavailable.
A structural safeguard, not an independent source-truth check. PASS exit 0, FAIL exit 1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, dumps, read_json, run, schema_errors, write_text

LEVELS = {'industry_aggregate': 0, 'company': 1, 'plant': 2, 'line': 3, 'sku': 4, 'customer_sku': 5, 'component': 6}
FACTUAL = {'confirmed_actual', 'firm_order', 'management_plan'}


def _url(u):
    return str(u or '').strip().rstrip('/').lower()


def validate(d):
    if not isinstance(d, dict):
        return ['manifest must be a JSON object']
    errors = ['schema: ' + e for e in schema_errors(d, 'public-data-manifest.schema.json')]
    if errors:
        return errors
    scope = d['observation_scope']
    source_urls = {_url(s['url']) for s in d['sources']}
    unavailable = {k for k, v in d.get('disclosures', {}).items() if v == 'unavailable'}
    for i, c in enumerate(d['claims']):
        label = f"claim[{i}]" + (f" {c['id']}" if c.get('id') else '')
        kind = str(c['type']).strip().lower()
        finer = LEVELS[c['scope']] > LEVELS[scope]
        shown_as = c.get('represented_as')
        if kind == 'observed':
            if finer:
                errors.append(f'{label}: observed granularity {c["scope"]} exceeds source granularity {scope}')
            if not c.get('source_url'):
                errors.append(f'{label}: observed fact lacks source_url')
            elif _url(c['source_url']) not in source_urls:
                errors.append(f'{label}: source_url is not one of the manifest sources')
            if c.get('dataset') in unavailable:
                errors.append(f'{label}: observed {c["dataset"]} contradicts unavailable disclosure')
        else:
            if shown_as in FACTUAL:
                errors.append(f'{label}: {kind} claim represented as {shown_as}')
            if finer and shown_as not in ('estimate', 'scenario', 'illustrative'):
                errors.append(f'{label}: {kind} claim at {c["scope"]} (finer than {scope}) must be represented as estimate, scenario or illustrative')
            if c.get('source_url') and _url(c['source_url']) not in source_urls:
                errors.append(f'{label}: source_url is not one of the manifest sources')
    return errors


def main(argv=None):
    ap = Parser(description=__doc__)
    ap.add_argument('manifest')
    ap.add_argument('--out')
    args = ap.parse_args(argv)
    errors = validate(read_json(args.manifest))
    out = dumps({'status': 'FAIL' if errors else 'PASS', 'passed': not errors, 'issues': errors})
    if args.out:
        write_text(args.out, out + '\n')
    print(out)
    return EXIT_FAIL if errors else EXIT_PASS


if __name__ == '__main__':
    run(main)
