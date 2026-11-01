"""Public-data provenance and scope gate."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_public_data import validate

BASE = json.loads((ROOT / 'examples' / 'public-data-manifest.json').read_text(encoding='utf-8'))
URL = BASE['sources'][0]['url']


class TestPublicData(unittest.TestCase):
    def data(self):
        return copy.deepcopy(BASE)

    def claim(self, **kw):
        d = self.data()
        d['claims'].append(kw)
        return validate(d)

    def test_example_passes(self):
        self.assertEqual(validate(self.data()), [])

    def test_plant_observation_from_sector_source(self):
        self.assertTrue(self.claim(type='observed', scope='plant', source_url=URL))

    def test_type_is_case_insensitive(self):
        self.assertTrue(self.claim(type='Observed', scope='customer_sku', source_url=URL))

    def test_missing_link(self):
        self.assertTrue(self.claim(type='observed', scope='industry_aggregate'))

    def test_source_url_must_be_listed(self):
        self.assertTrue(self.claim(type='observed', scope='industry_aggregate', source_url='https://elsewhere.example'))

    def test_advance_as_firm_order(self):
        self.assertTrue(self.claim(type='advance', scope='industry_aggregate', represented_as='firm_order'))

    def test_estimate_presented_as_actual(self):
        self.assertTrue(self.claim(type='estimate', scope='customer_sku', represented_as='confirmed_actual'))

    def test_finer_inference_must_be_labelled(self):
        self.assertTrue(self.claim(type='inference', scope='sku'))
        self.assertFalse(self.claim(type='inference', scope='sku', represented_as='estimate'))

    def test_unavailable_dataset_conflict(self):
        self.assertTrue(self.claim(type='observed', dataset='bom', scope='industry_aggregate', source_url=URL))

    def test_schema_errors_reported(self):
        d = self.data()
        d['sources'] = 'https://x'
        self.assertTrue(any(e.startswith('schema:') for e in validate(d)))


if __name__ == '__main__':
    unittest.main()
