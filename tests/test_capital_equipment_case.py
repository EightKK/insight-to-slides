"""Source-grounded regression fixture for the capital-equipment analytical guardrails."""
import unittest, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_decision_quality import evaluate
class CapitalEquipmentCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics=json.loads((ROOT/'tests'/'fixtures'/'asml-2026-q3-numeric-audit.json').read_text(encoding='utf-8'))['calculated']
        cls.contract=json.loads((ROOT/'tests'/'fixtures'/'asml-2026-q3-argumentation.json').read_text(encoding='utf-8'))
    def test_margin_up_share_down(self):
        self.assertAlmostEqual(self.metrics['gross_margin_qoq_pp'],3.5,places=3)
        self.assertLess(self.metrics['ibm_share_qoq_pp'],-1)
    def test_income_earnings_calculated(self):
        self.assertAlmostEqual(self.metrics['net_income_yoy_pct'],133.41,delta=.1)
        self.assertAlmostEqual(self.metrics['op_income_yoy_pct'],109.60,delta=.1)
    def test_argumentation_contract(self):
        self.assertEqual(evaluate(self.contract)['status'],'PASS')
    def test_supported_conclusion_and_alternative(self):
        self.assertIn('前受金',self.contract['current_answer'])
        self.assertGreaterEqual(len(self.contract['hypotheses']),2)
        self.assertGreaterEqual(len(self.contract['decision']['reversal_conditions']),2)
if __name__=='__main__': unittest.main()
