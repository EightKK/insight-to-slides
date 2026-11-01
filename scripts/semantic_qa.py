#!/usr/bin/env python3
"""Source-grounded and limited vector-geometry checks for slide deck semantics.

Usage: python3 scripts/semantic_qa.py source-values.json semantic-contract.json deck.pdf --out semantic-invariants.json

Check types: numeric_direction, reconcile, margin_points, required_text,
scope_caveat, forecast_label, signed_vector_bar. `page` is 1-based.
Numeric checks accept `tolerance` (absolute, default 0.02) and `relative_tolerance`
(fraction of the reference magnitude); the larger applies.
Text tokens are matched after NFKC normalisation (full-width digits, ％, ＋),
with ▲/△/− treated as a minus sign. Matching is sign-explicit: '12%' does not
match '-12%' or '▲12%', and '+12%' does not match '▲12%'.
signed_vector_bar with a flat change passes only if no bar of the declared colour
extends from the axis (and any `flat_tokens` are present on the page).
This is NOT a VLM or a human comprehension measurement.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, contains_token, dumps, load_pymupdf, normalize_text, read_json, run, write_text


def look(source, key):
    out = source
    for part in key.split('.'):
        if not isinstance(out, dict) or part not in out:
            raise ValueError(f'unknown numeric source key: {key}')
        out = out[part]
    if not isinstance(out, (int, float)) or isinstance(out, bool):
        raise ValueError(f'not numeric: {key}')
    return float(out)


def rgb_close(a, b, max_distance=.065):
    return len(a) == 3 and math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b))) <= max_distance


def tolerance(check, reference):
    return max(float(check.get('tolerance', .02)), float(check.get('relative_tolerance', 0)) * abs(reference))


def _page(check, pdf):
    if 'page' not in check:
        return None
    n = check['page']
    if not isinstance(n, int) or isinstance(n, bool) or n < 1 or n > len(pdf):
        raise ValueError(f'page must be an integer between 1 and {len(pdf)}, got {n!r}')
    return pdf[n - 1]


def check(check, values, pdf):
    kind = check['type']
    page = _page(check, pdf)
    text = normalize_text(page.get_text('text')) if page is not None else ''
    detail = {}
    if kind == 'numeric_direction':
        cur, prev = look(values, check['current']), look(values, check['previous'])
        delta, tol = cur - prev, tolerance(check, prev)
        actual = 'up' if delta > tol else 'down' if delta < -tol else 'flat'
        success = actual == check['expected']
        detail = {'delta': delta, 'actual': actual, 'expected': check['expected'], 'tolerance': tol}
    elif kind == 'reconcile':
        delta = look(values, check['current']) - look(values, check['previous'])
        components = sum(look(values, p) for p in check['components'])
        tol = tolerance(check, delta)
        success = abs(delta - components) <= tol
        detail = {'actual_delta': delta, 'components_total': components, 'tolerance': tol}
    elif kind == 'margin_points':
        before = 100 * look(values, check['profit_previous']) / look(values, check['sales_previous'])
        after = 100 * look(values, check['profit_current']) / look(values, check['sales_current'])
        actual = after - before
        tol = tolerance(check, float(check['expected_points']))
        success = abs(actual - float(check['expected_points'])) <= tol
        detail = {'margin_previous': before, 'margin_current': after, 'delta_points': actual, 'tolerance': tol}
    elif kind in ('required_text', 'scope_caveat', 'forecast_label'):
        if page is None:
            raise ValueError(f'{kind} needs a page')
        tokens = check.get('tokens', [])
        missing = [x for x in tokens if not contains_token(text, x)]
        success = bool(tokens) and not missing
        detail = {'missing_tokens': missing}
    elif kind == 'signed_vector_bar':
        if page is None:
            raise ValueError('signed_vector_bar needs a page')
        prev = look(values, check['previous'])
        signed_delta = look(values, check['current']) - prev
        tol = tolerance(check, prev)
        expected = 'right' if signed_delta > tol else 'left' if signed_delta < -tol else 'flat'
        page_width, page_height = page.rect.width, page.rect.height
        axis = float(check['axis_x_fraction']) * page_width
        lower, upper = [float(n) * page_height for n in check['y_fraction_range']]
        target_rgb = tuple(c / 255.0 for c in check['rgb'])
        candidates = []
        for d in page.get_drawings():
            r, color = d['rect'], d.get('fill')
            if not color or not rgb_close(color, target_rgb):
                continue
            if r.y0 < lower or r.y1 > upper or r.width < float(check.get('minimum_width_points', 20)):
                continue
            candidates.append([round(v, 2) for v in (r.x0, r.y0, r.x1, r.y1)])
        eps = float(check.get('axis_tolerance_points', 3))
        if expected == 'right':
            success = any(abs(r[0] - axis) <= eps and r[2] > axis + 10 for r in candidates)
        elif expected == 'left':
            success = any(abs(r[2] - axis) <= eps and r[0] < axis - 10 for r in candidates)
        else:
            extends = [r for r in candidates if r[0] < axis - 10 or r[2] > axis + 10]
            flat_tokens = check.get('flat_tokens', [])
            success = not extends and all(contains_token(text, t) for t in flat_tokens)
        detail = {'expected_visual_direction': expected, 'axis_x_points': axis, 'matching_shapes': candidates,
                  'note': 'PDF vector-geometry heuristic; not full chart comprehension'}
    else:
        raise ValueError(f'unsupported QA check: {kind}')
    return {'id': check['id'], 'type': kind, 'page': check.get('page'), 'passed': bool(success), 'details': detail}


def audit(source, contract, pdf_path):
    pymupdf = load_pymupdf()
    values = read_json(source)
    rules = read_json(contract)
    results = []
    with pymupdf.open(pdf_path) as doc:
        for entry in rules['checks']:
            try:
                results.append(check(entry, values, doc))
            except (ValueError, KeyError, ZeroDivisionError, TypeError, IndexError) as exc:
                results.append({'id': entry.get('id', 'unknown'), 'passed': False, 'error': str(exc)})
    passed = sum(x['passed'] for x in results)
    return {'status': 'PASS' if results and passed == len(results) else 'FAIL',
            'contract': str(contract), 'pdf': str(pdf_path),
            'scope': 'numeric source consistency, required PDF text, and selected vector directions only',
            'ai_vision_review': 'NOT AUTOMATED', 'human_two_second_test': 'NOT PERFORMED',
            'total': len(results), 'passed': passed, 'results': results}


def main(argv=None):
    p = Parser(description=__doc__)
    p.add_argument('source')
    p.add_argument('contract')
    p.add_argument('pdf')
    p.add_argument('--out', required=True)
    a = p.parse_args(argv)
    result = audit(a.source, a.contract, a.pdf)
    write_text(a.out, dumps(result) + '\n')
    print(dumps({'status': result['status'], 'checks': result['total'], 'passed': result['passed']}))
    return EXIT_PASS if result['status'] == 'PASS' else EXIT_FAIL


if __name__ == '__main__':
    run(main)
