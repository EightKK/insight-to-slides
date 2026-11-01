"""Synthetic factory bundle: ledger reconciliation, period handling and corrupted-ledger regressions."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_factory_monthly import audit
from factory_fixture import FIXTURE, append_period, copy_fixture, edit, set_period


class AuditFactoryMonthlyTests(unittest.TestCase):
    def test_fixture_passes(self):
        x = audit(FIXTURE)
        self.assertEqual(x['status'], 'PASS', x['errors'])
        self.assertEqual(x['period'], '2026-10')
        self.assertGreaterEqual(x['checks_count'], 60)
        self.assertEqual(x['recomputed']['next1_required_production']['CX-300'], 0)
        self.assertEqual(x['recomputed']['component_needs']['IC-7'], 3540)

    def test_material_shortage_reported_as_finding(self):
        x = audit(FIXTURE)
        self.assertEqual(x['recomputed']['material_shortages']['IC-7'], 540)
        self.assertTrue(any('IC-7' in f for f in x['material_findings']))
        self.assertEqual(len(x['material_findings']), 1)

    def test_missing_supply_row_is_a_shortage_finding(self):
        with copy_fixture() as td:
            edit(td, 'component_supply.csv', lambda rows: [r for r in rows if r['component'] != 'CAS-A'])
            x = audit(td)
            self.assertEqual(x['recomputed']['material_shortages']['CAS-A'], 1230)
            self.assertTrue(any('CAS-A' in f and 'no supply row' in f for f in x['material_findings']))

    def test_broken_inventory_fails(self):
        with copy_fixture() as td:
            def bump(rows):
                rows[0]['fg_close_units'] = str(int(rows[0]['fg_close_units']) + 8)
                return rows
            edit(td, 'inventory_actual.csv', bump)
            res = audit(td)
            self.assertEqual(res['status'], 'FAIL')
            self.assertTrue(any('conservation' in e for e in res['errors']))

    def test_broken_profit_fails(self):
        with copy_fixture() as td:
            def corrupt(rows):
                rows[0]['contribution_mJPY'] = '999'
                return rows
            edit(td, 'customer_item_profit.csv', corrupt)
            res = audit(td)
            self.assertEqual(res['status'], 'FAIL')
            self.assertTrue(any('contribution' in e for e in res['errors']))

    def test_reported_rounding_is_tolerated_but_real_error_is_not(self):
        with copy_fixture() as td:
            def reprice(rows):
                for r in rows:
                    if r['sku'] == 'AX-100' and r['customer'] == '北斗装置':
                        r['unit_price_kJPY'] = '43.0001'  # 300 x 43.0001 / 1000 = 12.90003, reported 12.9
                return rows
            edit(td, 'sales_plan_actual_forecast.csv', reprice)
            self.assertNotIn("('AX-100', '北斗装置') revenue from price x shipments", audit(td)['errors'])

            def reprice_more(rows):
                for r in rows:
                    if r['sku'] == 'AX-100' and r['customer'] == '北斗装置':
                        r['unit_price_kJPY'] = '43.5'
                return rows
            edit(td, 'sales_plan_actual_forecast.csv', reprice_more)
            self.assertIn("('AX-100', '北斗装置') revenue from price x shipments", audit(td)['errors'])

    def test_split_bom_rows_accumulate(self):
        with copy_fixture() as td:
            def split(rows):
                out = []
                for r in rows:
                    if r['parent_sku'] == 'AX-100' and r['component'] == 'IC-7':
                        out += [dict(r, qty_per_good='1'), dict(r, qty_per_good='1')]
                    else:
                        out.append(r)
                return out
            edit(td, 'bom.csv', split)
            x = audit(td)
            self.assertEqual(x['status'], 'PASS', x['errors'])
            self.assertEqual(x['recomputed']['component_needs']['IC-7'], 3540)

    def test_other_month_works(self):
        with copy_fixture() as td:
            set_period(td, '2026-11')
            x = audit(td)
            self.assertEqual((x['status'], x['period']), ('PASS', '2026-11'))
            self.assertEqual(audit(td, '2026-11')['recomputed']['component_needs']['IC-7'], 3540)

    def test_multiple_periods_require_period_argument(self):
        with copy_fixture() as td:
            append_period(td, '2026-11')
            with self.assertRaisesRegex(ValueError, '--period'):
                audit(td)
            self.assertEqual(audit(td, '2026-11')['status'], 'PASS')
            with self.assertRaisesRegex(ValueError, 'not present'):
                audit(td, '2027-01')

    def test_missing_column_is_reported(self):
        with copy_fixture() as td:
            p = Path(td) / 'sales_plan_actual_forecast.csv'
            p.write_text(p.read_text(encoding='utf-8-sig').replace('next1_forecast_units', 'nov_forecast_units'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'next1_forecast_units'):
                audit(td)


if __name__ == '__main__':
    unittest.main()
