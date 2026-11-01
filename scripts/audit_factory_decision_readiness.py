#!/usr/bin/env python3
"""Cross-period decision gate for factory monthly operating reviews.

Usage: python3 scripts/audit_factory_decision_readiness.py DATA_DIR [--period YYYY-MM]
         [--backlog included|additional|unknown] [--eligible-stock-confirmed]
         [--supply-eta-confirmed] [--capacity-confirmed] [--inventory-policy-confirmed] [--out report.json]

Status: FAIL (exit 1) on arithmetic/data errors; HOLD (exit 2) while any decision
blocker remains, including any material shortage in the applicable backlog scenario
(with --backlog unknown, both scenarios apply); READY (exit 0) otherwise.
A shortage is resolved only by updated supply data (e.g. a confirmed receipt in
component_supply.csv) or a changed plan, never by a flag. Run after audit_factory_monthly.py.
Does not impute backlog inclusion, stock availability, lead time or customer obligations.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_HOLD, EXIT_PASS, Parser, dumps, run, write_text
from factory_bundle import bom_map, component_needs, load_bundle, shortages

SCENARIOS = {'backlog_included': True, 'backlog_additional': False}


def audit(folder, *, period=None, backlog_included=None, eligible_stock_confirmed=False,
          supply_eta_confirmed=False, capacity_confirmed=False, inventory_policy_confirmed=False):
    t, period = load_bundle(folder, period)
    s, i, b, sup, p = t['sales'], t['inventory'], t['bom'], t['supply'], t['profit']
    issues = []
    inv = {r['sku']: r for r in i}
    qty = defaultdict(lambda: [0, 0])
    carry = defaultdict(int)
    for r in s:
        qty[r['sku']][0] += int(r['next1_forecast_units'])
        qty[r['sku']][1] += int(r['next2_forecast_units'])
        carry[r['sku']] += int(r['overdue_units'])
    missing_inv = sorted(k for k in qty if k not in inv)
    if missing_inv:
        issues.append(f'forecast SKU missing inventory: {missing_inv}')
    fg = {k: int(inv[k]['fg_close_units']) if k in inv else 0 for k in qty}
    bom = bom_map(b)
    for k in qty:
        if not bom.get(k):
            issues.append(f'BOM missing for {k}')
    usable = defaultdict(float)
    for r in sup:
        usable[r['component']] += float(r['next1_usable_units'])
    if not usable:
        issues.append('no material supply rows')

    scenario = {}
    for name, include in SCENARIOS.items():
        needed = {k: max(0, v[0] + (0 if include else carry[k]) - fg[k]) for k, v in qty.items()}
        needs = component_needs(needed, bom)
        short = shortages(needs, usable)
        scenario[name] = {'next1_total_demand_units': sum(v[0] for v in qty.values()) + (0 if include else sum(carry.values())),
                          'next1_net_production_units_by_sku': needed, 'material_needs': needs,
                          'material_shortages': short,
                          'components_without_supply_row': sorted(c for c in needs if c not in usable and needs[c] > 0)}

    stock_cover = []
    for k, v in qty.items():
        m2 = v[0] + v[1]
        stock_cover.append({'sku': k, 'fg_close_units': fg[k], 'next1_forecast_units': v[0],
                            'next2_forecast_units': v[1], 'two_month_forecast_units': m2,
                            'stock_to_two_month_demand_pct': round(fg[k] / m2 * 100, 1) if m2 else None})
    plan_contrib = sum(float(r['plan_contribution_mJPY']) for r in p)
    actual_contrib = sum(float(r['contribution_mJPY']) for r in p)
    if plan_contrib <= 0:
        issues.append('plan contribution not positive')

    backlog_status = 'UNRESOLVED' if backlog_included is None else ('INCLUDED' if backlog_included else 'ADDITIONAL')
    applicable = list(SCENARIOS) if backlog_included is None else ['backlog_included' if backlog_included else 'backlog_additional']
    blockers = []
    if backlog_included is None:
        blockers.append('backlog membership in next-month forecast unverified')
    for name in applicable:
        for comp, q in scenario[name]['material_shortages'].items():
            if q > 0:
                blockers.append(f'material shortage in {name}: {comp} short {q:g} units')
    if not eligible_stock_confirmed:
        blockers.append('FG allocation and quality availability unverified')
    if not supply_eta_confirmed:
        blockers.append('expedited component ETA and acceptance unconfirmed')
    if not capacity_confirmed:
        blockers.append('work-center capacity and yield not verified')
    if not inventory_policy_confirmed:
        blockers.append('stock target / replenishment policy not supplied')
    return {
        'status': 'FAIL' if issues else ('HOLD' if blockers else 'READY'), 'period': period,
        'arithmetic_errors': issues, 'decision_blockers': blockers, 'applicable_scenarios': applicable,
        'executive': {'plan_contribution_mJPY': round(plan_contrib, 2), 'actual_contribution_mJPY': round(actual_contrib, 2),
                      'contribution_gap_mJPY': round(actual_contrib - plan_contrib, 2),
                      'contribution_attainment_pct': round(100 * actual_contrib / plan_contrib, 1) if plan_contrib > 0 else None},
        'backlog': {'total_units': sum(carry.values()), 'by_sku': dict(carry), 'status': backlog_status},
        'next_two_months_inventory': stock_cover, 'scenarios': scenario,
        'warning': 'backlog_additional assumes valid overdue orders carry into next1 without inclusion in the next1 forecast. '
                   'No assertion that this is the actual accounting treatment.'}


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('data_dir')
    parser.add_argument('--period', help='reporting month YYYY-MM; required when the CSVs hold several periods')
    parser.add_argument('--out')
    parser.add_argument('--backlog', choices=['included', 'additional', 'unknown'], default='unknown')
    parser.add_argument('--eligible-stock-confirmed', action='store_true')
    parser.add_argument('--supply-eta-confirmed', action='store_true')
    parser.add_argument('--capacity-confirmed', action='store_true')
    parser.add_argument('--inventory-policy-confirmed', action='store_true')
    args = parser.parse_args(argv)
    x = audit(args.data_dir, period=args.period,
              backlog_included={'included': True, 'additional': False, 'unknown': None}[args.backlog],
              eligible_stock_confirmed=args.eligible_stock_confirmed, supply_eta_confirmed=args.supply_eta_confirmed,
              capacity_confirmed=args.capacity_confirmed, inventory_policy_confirmed=args.inventory_policy_confirmed)
    if args.out:
        write_text(args.out, dumps(x) + '\n')
    print(dumps({k: x[k] for k in ('status', 'period', 'arithmetic_errors', 'decision_blockers', 'executive', 'backlog', 'scenarios')}))
    return {'READY': EXIT_PASS, 'HOLD': EXIT_HOLD}.get(x['status'], EXIT_FAIL)


if __name__ == '__main__':
    run(main)
