"""Decision gate: HOLD while blockers or material shortages remain; READY only when resolved by data."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_factory_decision_readiness import audit
from factory_fixture import FIXTURE, copy_fixture, edit, set_period

CONFIRMED = dict(eligible_stock_confirmed=True, supply_eta_confirmed=True, capacity_confirmed=True,
                 inventory_policy_confirmed=True)


def add_ic7_receipt(units):
    def fn(rows):
        for r in rows:
            if r['component'] == 'IC-7':
                r['next1_confirmed_receipt_units'] = str(int(r['next1_confirmed_receipt_units']) + units)
                r['next1_usable_units'] = str(int(r['next1_usable_units']) + units)
        return rows
    return fn


class DecisionReadinessTests(unittest.TestCase):
    def test_blocked_until_cross_period_confirmed(self):
        res = audit(FIXTURE)
        self.assertEqual(res['status'], 'HOLD')
        self.assertEqual(res['backlog']['total_units'], 195)
        self.assertTrue(any('membership' in v for v in res['decision_blockers']))

    def test_executive_profit_is_prominent(self):
        res = audit(FIXTURE)
        self.assertEqual(res['executive']['plan_contribution_mJPY'], 40.8)
        self.assertEqual(res['executive']['actual_contribution_mJPY'], 33.18)
        self.assertEqual(res['executive']['contribution_attainment_pct'], 81.3)

    def test_unknown_backlog_yields_two_cases(self):
        cases = audit(FIXTURE)['scenarios']
        self.assertEqual(cases['backlog_included']['material_shortages']['IC-7'], 540)
        self.assertEqual(cases['backlog_additional']['material_shortages']['IC-7'], 975)
        self.assertEqual(cases['backlog_included']['next1_net_production_units_by_sku']['CX-300'], 0)

    def test_two_month_stock_does_not_prove_excess(self):
        cx = next(x for x in audit(FIXTURE)['next_two_months_inventory'] if x['sku'] == 'CX-300')
        self.assertEqual(cx['fg_close_units'], 600)
        self.assertEqual(cx['two_month_forecast_units'], 610)

    def test_shortage_blocks_ready_even_when_all_conditions_confirmed(self):
        res = audit(FIXTURE, backlog_included=True, **CONFIRMED)
        self.assertEqual(res['status'], 'HOLD')
        self.assertEqual(res['decision_blockers'], ['material shortage in backlog_included: IC-7 short 540 units'])

    def test_confirmed_receipt_covering_shortage_releases_gate(self):
        with copy_fixture() as td:
            edit(td, 'component_supply.csv', add_ic7_receipt(540))
            self.assertEqual(audit(td, backlog_included=True, **CONFIRMED)['status'], 'READY')
            # the additional-backlog case still needs 975 more, so it stays on HOLD
            self.assertEqual(audit(td, backlog_included=False, **CONFIRMED)['status'], 'HOLD')

    def test_needed_component_without_supply_row_blocks(self):
        with copy_fixture() as td:
            edit(td, 'component_supply.csv', add_ic7_receipt(1000))
            edit(td, 'component_supply.csv', lambda rows: [r for r in rows if r['component'] != 'CAS-D'])
            res = audit(td, backlog_included=True, **CONFIRMED)
            self.assertEqual(res['status'], 'HOLD')
            self.assertIn('CAS-D', res['scenarios']['backlog_included']['components_without_supply_row'])
            self.assertEqual(res['scenarios']['backlog_included']['material_shortages']['CAS-D'], 360)

    def test_included_backlog_alone_does_not_release_gate(self):
        self.assertEqual(audit(FIXTURE, backlog_included=True)['status'], 'HOLD')

    def test_broken_bom_does_not_silently_pass(self):
        with copy_fixture() as td:
            edit(td, 'bom.csv', lambda rows: [r for r in rows if r['parent_sku'] != 'DX-400'])
            self.assertEqual(audit(td)['status'], 'FAIL')

    def test_other_month_works(self):
        with copy_fixture() as td:
            set_period(td, '2027-03')
            res = audit(td, period='2027-03')
            self.assertEqual(res['period'], '2027-03')
            self.assertEqual(res['scenarios']['backlog_included']['material_shortages']['IC-7'], 540)


if __name__ == '__main__':
    unittest.main()
