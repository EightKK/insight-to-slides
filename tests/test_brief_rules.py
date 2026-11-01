"""Brief validation rules, pattern catalog integrity and arithmetic recomputation."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_brief import validate
from audit_calculations import audit, resolve
import ast

class BriefRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads((ROOT/'examples/inventory-decision.json').read_text(encoding='utf-8'))
        cls.catalog = json.loads((ROOT/'patterns/catalog.json').read_text(encoding='utf-8'))

    def test_pattern_catalog_unique_and_complete(self):
        patterns=self.catalog['patterns']
        self.assertGreaterEqual(len(patterns),12)
        self.assertEqual(len(patterns),len({p['id'] for p in patterns}))
        for p in patterns:
            for key in ('id','intent','best_for','minimum_inputs','composition','must_show','avoid','alternatives','discussion_hook'):
                self.assertIn(key,p)

    def test_sample_validates(self):
        errors,_=validate(self.sample)
        self.assertEqual(errors,[])

    def test_pattern_id_required(self):
        data=deepcopy(self.sample)
        data['slides'][0]['visual'].pop('pattern_id')
        errors,_=validate(data)
        self.assertTrue(any('pattern_id' in e for e in errors))

    def test_unknown_pattern_id_rejected(self):
        data=deepcopy(self.sample)
        data['slides'][0]['visual']['pattern_id']='made_up'
        errors,_=validate(data)
        self.assertTrue(any('unknown' in e for e in errors))

    def test_only_current_schema_version_accepted(self):
        data=deepcopy(self.sample)
        data['schema_version']='0.9.0'
        errors,_=validate(data)
        self.assertTrue(any('schema_version' in e for e in errors))

    def test_schema_enums_enforced(self):
        data=deepcopy(self.sample)
        data['document']['medium']='tv'
        data['evidence'][0]['kind']='made_up'
        data['slides'][0]['secret_claim']='x'
        errors,_=validate(data)
        for needle in ('medium','kind','secret_claim'):
            self.assertTrue(any(needle in e for e in errors),needle)

    def test_null_headline_reports_error_not_crash(self):
        data=deepcopy(self.sample)
        data['slides'][-1]['headline']=None
        errors,_=validate(data)
        self.assertTrue(any('headline' in e for e in errors))

    def test_arithmetic_audit(self):
        results=audit({'a':{'x':10,'y':4}}, {'calculations':[{'id':'v','expression':'(a.x - a.y) / a.y * 100','expected':150.0}]})
        self.assertTrue(results[0]['passed'])

    def test_reject_arbitrary_calls(self):
        with self.assertRaises(ValueError):
            resolve(ast.parse("__import__('os').system('ls')",mode='eval').body, {})

    def test_string_values_are_not_numbers(self):
        r=audit({'a':'1','b':'2'},{'calculations':[{'id':'x','expression':'a+b','expected':12}]})[0]
        self.assertFalse(r['passed'])
        self.assertIn('Non-numeric',r['error'])

    def test_relative_tolerance(self):
        calc={'id':'r','expression':'x','expected':1000,'relative_tolerance':0.001}
        self.assertTrue(audit({'x':1000.9},{'calculations':[calc]})[0]['passed'])
        self.assertFalse(audit({'x':1002},{'calculations':[calc]})[0]['passed'])

    def test_calculation_mismatch_flags_error(self):
        self.assertFalse(audit({'x':2},{'calculations':[{'id':'x','expression':'x+1','expected':4}]})[0]['passed'])

if __name__=='__main__':
    unittest.main()
