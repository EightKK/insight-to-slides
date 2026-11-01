"""Non-financial manufacturing scenario validation regression fixtures."""
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_operational_case import audit
BASE=json.loads((ROOT/'examples/fictional-mixed-model-wip.json').read_text(encoding='utf-8'))
class OperationalCaseTests(unittest.TestCase):
    def test_nominal_model_passes(self):self.assertEqual(audit(BASE)['status'],'PASS')
    def test_inventory_balance_failure(self):
        x=copy.deepcopy(BASE);x['ending_wip_units']+=1;self.assertEqual(audit(x)['status'],'FAIL')
    def test_location_balance_failure(self):
        x=copy.deepcopy(BASE);x['stages'][1]['wip_units']+=1;self.assertEqual(audit(x)['status'],'FAIL')
    def test_age_band_failure(self):
        x=copy.deepcopy(BASE);x['stages'][2]['aging']['6+']+=1;self.assertEqual(audit(x)['status'],'FAIL')
    def test_capacity_overrun_failure(self):
        x=copy.deepcopy(BASE);x['scenarios'][2]['completed_per_day']=800;self.assertEqual(audit(x)['status'],'FAIL')
    def test_pilot_demand_shortfall_failure(self):
        x=copy.deepcopy(BASE);x['pilot']['completion_target_per_day']=690;self.assertEqual(audit(x)['status'],'FAIL')
    def test_proposed_stock_mismatch_failure(self):
        x=copy.deepcopy(BASE);x['pilot']['target_end_wip_units']=3000;self.assertEqual(audit(x)['status'],'FAIL')
    def test_recovery_too_high_failure(self):
        x=copy.deepcopy(BASE);x['constraint_capacity_model']['pilot_minutes_recovered_per_day']['changeover']=65;self.assertEqual(audit(x)['status'],'FAIL')
    def test_scenarios_delivery_warning(self):
        x=audit(BASE)['metrics']['scenarios']; self.assertEqual(next(z for z in x if z['id']=='release_only')['delivery_deficit_units'],440)
    def test_projection_and_value(self):
        x=audit(BASE)['metrics']; self.assertEqual(next(z for z in x['scenarios'] if z['id']=='combined')['end_wip_units'],2550);self.assertEqual(x['selected_book_value_reduction_yen'],29700000)
    def test_recommended_scenario_is_not_hardcoded(self):
        x=copy.deepcopy(BASE)
        for s in x['scenarios']:
            if s['id']=='combined':s['id']='S4'
        x['pilot']['recommended_scenario_id']='S4'
        self.assertEqual(audit(x)['status'],'PASS',audit(x)['errors'])
    def test_pilot_must_match_recommended_scenario(self):
        x=copy.deepcopy(BASE);x['pilot']['recommended_scenario_id']='output_only'
        self.assertEqual(audit(x)['status'],'FAIL')
    def test_declared_constraint_must_be_bottleneck(self):
        x=copy.deepcopy(BASE);x['constraint_capacity_model']['constraint_stage_id']='cut'
        self.assertEqual(audit(x)['status'],'FAIL')
    def test_schema_requires_benefit_basis_note(self):
        from common import schema_errors
        x=copy.deepcopy(BASE);x.pop('benefit_basis_note')
        self.assertTrue(schema_errors(x,'operational-decision.schema.json'))
if __name__=='__main__':unittest.main()
