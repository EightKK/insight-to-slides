#!/usr/bin/env python3
"""Deterministic operations-case guardrails (WIP flow, constraint capacity, scenarios); not a simulation or causal proof.

Usage: python3 scripts/audit_operational_case.py case.json [--out report.json]

Validates against schemas/operational-decision.schema.json, then checks inventory
conservation, stage/aging balances, the constraint loss-time model (tolerance:
constraint_capacity_model.model_tolerance_units_per_day, default 1.0; the proposed
capacity is a rounded value, so +/-0.5 is added), scenario arithmetic, consistency of the
recommended scenario with the pilot, and service feasibility. PASS exit 0, FAIL exit 1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, dumps, read_json, run, schema_errors, write_text


def audit(c):
    errors, warnings, details = [], [], {}

    def eq(label, observed, expected, tol=1e-6):
        if abs(observed - expected) > tol:
            errors.append(f'{label}: observed {observed:g} != expected {expected:g}')

    days = c['period_workdays']
    start, end = c['starting_wip_units'], c['ending_wip_units']
    release = c['average_release_units_per_day']
    finish = c['average_completion_units_per_day']
    demand = c['average_customer_demand_units_per_day']
    eq('historical inventory conservation', end, start + days * (release - finish))
    eq('stage snapshot sums to ending WIP', sum(s['wip_units'] for s in c['stages']), end)
    for s in c['stages']:
        eq(f'{s["id"]} aging bands sum to process stock', sum(s['aging'].values()), s['wip_units'])
    constraint = min(c['stages'], key=lambda s: s['effective_capacity_per_day'])
    details['constraint_stage'] = constraint['name']
    details['historical_daily_inventory_increase'] = release - finish
    details['historical_customer_deficit_per_day'] = max(0, demand - finish)
    if release <= finish:
        warnings.append('no historical accumulation: explain why this is a WIP reduction case')

    model = c['constraint_capacity_model']
    declared = model.get('constraint_stage_id')
    if declared and declared != constraint['id']:
        errors.append(f'declared constraint stage {declared} is not the lowest-capacity stage {constraint["id"]}')
    minutes, nominal = model['available_minutes_per_day'], model['theoretical_units_per_day']
    lost = sum(model['baseline_lost_minutes_per_day'].values())
    rec = sum(model['pilot_minutes_recovered_per_day'].values())
    if lost >= minutes:
        errors.append('lost minutes must be below available minutes')
    if rec > lost:
        errors.append('recovered time exceeds lost time')
    for k, v in model['pilot_minutes_recovered_per_day'].items():
        if v > model['baseline_lost_minutes_per_day'].get(k, 0):
            errors.append(f'recovered {k} time exceeds baseline')
    tol = float(model.get('model_tolerance_units_per_day', 1.0))
    predicted_base = nominal * (minutes - lost) / minutes
    predicted_pilot = nominal * (minutes - lost + rec) / minutes
    if abs(predicted_base - model['baseline_realized_output_units_per_day']) > tol:
        errors.append('baseline constraint loss-time model inconsistent with actual output')
    if abs(predicted_pilot - model['proposed_effective_capacity_rounded_per_day']) > tol + 0.5:
        errors.append('capacity recovery arithmetic inconsistent with proposed output')
    details['constraint_baseline_theoretical_units_per_day'] = round(predicted_base, 2)
    details['constraint_pilot_theoretical_units_per_day'] = round(predicted_pilot, 2)

    horizon = c['days_for_scenario']
    scenarios, ids = [], set()
    for s in c['scenarios']:
        if s['id'] in ids:
            errors.append(f'duplicate scenario id {s["id"]}')
        ids.add(s['id'])
        if s['completed_per_day'] > s['capacity_per_day'] + 1e-9:
            errors.append(f'{s["id"]}: completion > capacity')
        projected = end + horizon * (s['release_per_day'] - s['completed_per_day'])
        if projected < 0:
            errors.append(f'{s["id"]}: WIP projected below zero')
        deficit = horizon * max(0, s['customer_demand_per_day'] - s['completed_per_day'])
        fg_excess = horizon * max(0, s['completed_per_day'] - s['customer_demand_per_day'])
        scenarios.append({'id': s['id'], 'name': s['name'], 'end_wip_units': projected, 'change_wip_units': projected - end,
                          'delivery_deficit_units': deficit, 'finished_goods_excess_units_if_no_other_demand': fg_excess,
                          'service_feasible': deficit == 0})
    details['scenarios'] = scenarios

    pilot = c['pilot']
    rid = pilot['recommended_scenario_id']
    selected = next((s for s in scenarios if s['id'] == rid), None)
    selected_input = next((s for s in c['scenarios'] if s['id'] == rid), None)
    if not selected:
        errors.append(f'recommended scenario {rid} is missing from comparison')
    else:
        eq('pilot target vs scenario model', pilot['target_end_wip_units'], selected['end_wip_units'])
        eq('pilot release vs recommended scenario release', pilot['release_per_day'], selected_input['release_per_day'])
        eq('pilot completion target vs recommended scenario completion', pilot['completion_target_per_day'], selected_input['completed_per_day'])
        if selected['delivery_deficit_units'] > 0:
            errors.append(f'recommended scenario {rid} causes a delivery deficit')
        details['selected_book_value_reduction_yen'] = (end - selected['end_wip_units']) * pilot['average_wip_valuation_yen_per_unit']
    if pilot['completion_target_per_day'] > pilot['maximum_assumed_capacity_per_day']:
        errors.append('pilot completion target exceeds pilot capacity')
    if pilot['post_pilot_release_per_day'] > pilot['maximum_assumed_capacity_per_day']:
        errors.append('post-pilot release exceeds recovered capacity')
    if pilot['completion_target_per_day'] < demand:
        errors.append('pilot does not meet customer demand')
    if pilot['post_pilot_release_per_day'] < demand:
        errors.append('post-pilot steady release below demand')
    if c['source_classification'] == 'synthetic_fictional':
        warnings.append('fictional example: publish prominent provenance on cover and source/notes slide')
    return {'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'warnings': warnings, 'metrics': details}


def main(argv=None):
    p = Parser(description=__doc__)
    p.add_argument('case')
    p.add_argument('--out')
    args = p.parse_args(argv)
    data = read_json(args.case)
    se = schema_errors(data, 'operational-decision.schema.json')
    result = {'status': 'FAIL', 'errors': ['schema: ' + x for x in se], 'warnings': [], 'metrics': {}} if se else audit(data)
    rendered = dumps(result)
    if args.out:
        write_text(args.out, rendered + '\n')
    print(rendered)
    return EXIT_PASS if result['status'] == 'PASS' else EXIT_FAIL


if __name__ == '__main__':
    run(main)
