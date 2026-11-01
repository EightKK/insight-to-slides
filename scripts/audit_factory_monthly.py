#!/usr/bin/env python3
"""Cross-ledger audit for a customer-SKU plant monthly-review CSV bundle.

Usage: python3 scripts/audit_factory_monthly.py DATA_DIR [--period YYYY-MM] [--out report.json]

Checks conservation, aggregation and BOM/supply consistency for one reporting period,
and reports next-month material need vs usable supply as findings (not ledger errors).
Status PASS when all ledger checks reconcile, FAIL otherwise. Material shortages do
not change the ledger status; audit_factory_decision_readiness.py turns them into HOLD.
Not an ERP connector or a financial statement audit.
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, dumps, run, write_text
from factory_bundle import bom_map, component_needs, load_bundle, matches_reported, shortages


def check(cond, msg, checks, errors):
    checks.append({'check': msg, 'passed': bool(cond)})
    if not cond:
        errors.append(msg)


def audit(data_dir, period=None):
    t, period = load_bundle(data_dir, period)
    S, P, M, I, B, Supply = (t[k] for k in ['sales', 'profit', 'manufacturing', 'inventory', 'bom', 'supply'])
    issues, checks = [], []

    def key(r):
        return (r['sku'], r['customer'])
    smap = {key(r): r for r in S}
    pmap = {key(r): r for r in P}
    check(len(smap) == len(S), 'sales customer/SKU keys unique', checks, issues)
    check(len(pmap) == len(P) and set(smap) == set(pmap), 'profit lines match sales customer/SKU keys', checks, issues)
    for k, r in smap.items():
        check(int(r['confirmed_orders_units']) - int(r['shipped_units']) == int(r['overdue_units']), f'{k} overdue order balance', checks, issues)
        check(int(r['overdue_units']) >= 0, f'{k} overdue not negative', checks, issues)
        if k in pmap:
            p = pmap[k]
            q = int(r['shipped_units'])
            price = float(r['unit_price_kJPY'])
            cost = float(r['unit_customer_cost_kJPY'])
            check(matches_reported(q * price / 1000, p['revenue_mJPY']), f'{k} revenue from price x shipments', checks, issues)
            check(matches_reported(q * (price - cost) / 1000, p['contribution_mJPY']), f'{k} contribution from customer-item cost', checks, issues)
            check(int(p['shipped_units']) == q, f'{k} profit quantity matches sales', checks, issues)
    inv = {r['sku']: r for r in I}
    man = {r['sku']: r for r in M}
    check(set(inv) == set(man), 'product inventory and manufacture keys', checks, issues)
    check(set(r['sku'] for r in S) <= set(inv), 'every sales SKU has an inventory row', checks, issues)
    for sku, r in inv.items():
        shipped = sum(int(x['shipped_units']) for x in S if x['sku'] == sku)
        check(int(r['shipped_units']) == shipped, f'{sku} sales-to-inventory shipment reconciliation', checks, issues)
        check(int(r['fg_open_units']) + int(r['produced_good_units']) - shipped == int(r['fg_close_units']), f'{sku} finished-goods conservation', checks, issues)
        check(matches_reported(int(r['fg_close_units']) * float(r['fg_unit_manufacturing_cost_kJPY']) / 1000, r['fg_close_value_mJPY']), f'{sku} FG valuation at manufacturing cost', checks, issues)
        if sku in man:
            m = man[sku]
            check(int(m['actual_good_units']) == int(r['produced_good_units']), f'{sku} manufacturing/inventory completions', checks, issues)
            check(int(m['wip_open_units']) + int(m['wip_starts_units']) - int(m['actual_good_units']) - int(m['scrap_units']) == int(m['wip_close_units']), f'{sku} WIP balance', checks, issues)
            check(int(m['wip_close_units']) == int(r['wip_close_units']), f'{sku} WIP cross-ledger closings', checks, issues)
    rev_total = sum(float(x['revenue_mJPY']) for x in P)
    rev_recalc = sum(int(x['shipped_units']) * float(x['unit_price_kJPY']) / 1000 for x in S)
    rev_tol = sum(0.5 * 10 ** -len(x['revenue_mJPY'].split('.', 1)[1]) if '.' in x['revenue_mJPY'] else 0.5 for x in P) + 1e-9
    check(abs(rev_total - rev_recalc) <= rev_tol, 'customer-SKU revenue totals', checks, issues)

    bom = bom_map(B)
    sales_by_sku = defaultdict(int)
    for x in S:
        sales_by_sku[x['sku']] += int(x['next1_forecast_units'])
    need = {sku: max(0, n - int(inv[sku]['fg_close_units'])) if sku in inv else n for sku, n in sales_by_sku.items()}
    for sku in need:
        check(sku in bom, f'{sku} appears in BOM', checks, issues)
    material_need = component_needs(need, bom)
    usable = {}
    for x in Supply:
        comp = x['component']
        u = int(x['onhand_start_units']) + int(x['next1_confirmed_receipt_units']) - int(x['reserve_units'])
        check(u == int(x['next1_usable_units']), f'{comp} stock + confirmed receipt - reserve', checks, issues)
        check(comp in material_need, f'{comp} appears in netted BOM', checks, issues)
        usable[comp] = usable.get(comp, 0) + int(x['next1_usable_units'])
    short = shortages(material_need, usable)
    findings = []
    for comp, qty in short.items():
        if qty > 0:
            src = 'no supply row' if comp not in usable else f'usable {usable[comp]}'
            findings.append(f'material shortage {comp}: need {material_need.get(comp, 0):g} vs {src} -> short {qty:g} (backlog not added)')

    plan_rev = sum(int(r['plan_units']) * float(r['unit_price_kJPY']) for r in S) / 1000
    contrib = sum(float(x['contribution_mJPY']) for x in P)
    next1_rev = sum(int(r['next1_forecast_units']) * float(r['unit_price_kJPY']) for r in S) / 1000
    next1_contrib = sum(int(r['next1_forecast_units']) * (float(r['unit_price_kJPY']) - float(r['unit_customer_cost_kJPY'])) for r in S) / 1000
    return {
        'status': 'PASS' if not issues else 'FAIL', 'period': period,
        'checks_count': len(checks), 'checks_passed': sum(x['passed'] for x in checks),
        'errors': issues, 'material_findings': findings, 'checks': checks,
        'recomputed': {
            'sales_plan_mJPY': round(plan_rev, 3), 'sales_actual_mJPY': round(rev_recalc, 3),
            'customer_contribution_mJPY': round(contrib, 3),
            'next1_unconstrained_revenue_mJPY': round(next1_rev, 3),
            'next1_unconstrained_contribution_mJPY': round(next1_contrib, 3),
            'next1_required_production': need, 'component_needs': material_need,
            'component_usable_next1': usable, 'material_shortages': short,
            'negative_customer_item_contributions': [
                {'customer': x['customer'], 'sku': x['sku'], 'value_mJPY': float(x['contribution_mJPY'])}
                for x in P if float(x['contribution_mJPY']) < 0]},
        'limitations': ['Forecast is not firm orders', 'Only BOM components provided are checked',
                        'Material need nets next1 forecast against FG close; overdue backlog is not added (see the readiness gate)',
                        'No work-center capacity, yield or alternative-component certification',
                        'Fixed cost and cash-flow effects are excluded']}


def main(argv=None):
    p = Parser(description=__doc__)
    p.add_argument('data_dir')
    p.add_argument('--period', help='reporting month YYYY-MM; required when the CSVs hold several periods')
    p.add_argument('--out')
    args = p.parse_args(argv)
    out = audit(args.data_dir, args.period)
    if args.out:
        write_text(args.out, dumps(out) + '\n')
    print(dumps({k: out[k] for k in ('status', 'period', 'checks_count', 'checks_passed', 'errors', 'material_findings', 'recomputed')}))
    return EXIT_PASS if out['status'] == 'PASS' else EXIT_FAIL


if __name__ == '__main__':
    run(main)
