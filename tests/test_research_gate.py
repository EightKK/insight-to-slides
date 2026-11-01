"""Evidence-coverage gate: schema validation, false coverage, open high-impact gaps and dates."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from research_gate import validate

P = {'schema_version': '1.0.0', 'mode': 'research', 'question': 'Why did margin fall?', 'as_of': '2026-11-01', 'max_retrievals': 5,
     'gaps': [{'id': 'G1', 'claim': 'C', 'decision_impact': 5, 'retrieval_cost': 1, 'preferred_sources': ['official'],
               'falsifier': 'F', 'required_evidence_ids': ['E1'], 'resolution': 'covered'}]}
L = {'schema_version': '1.0.0',
     'sources': [{'id': 'S1', 'publisher': 'P', 'title': 'T', 'published_at': '2026-08-04', 'locator': 'https://example.org', 'type': 'official_filing'}],
     'observations': [{'id': 'E1', 'source_id': 'S1', 'statement': 'A', 'status': 'verified', 'scope': 'Q', 'period': '2026Q1', 'kind': 'actual'}]}
A = {'schema_version': '1.0.0', 'primary_question': 'Q', 'language': 'ja', 'hypotheses': [],
     'conclusions': [{'id': 'C1', 'claim': 'foo', 'evidence_ids': ['E1'], 'confidence': 'high', 'relevance': 'X'}]}
EMPTY_LEDGER = {'schema_version': '1.0.0', 'sources': [], 'observations': []}


class ResearchGateTest(unittest.TestCase):
    def test_valid(self):
        r = validate(P, L, A)
        self.assertEqual(r['status'], 'PASS', r)

    def test_toyota_example_passes_with_warnings(self):
        d = ROOT / 'examples' / 'toyota-deep-research'
        load = lambda n: json.loads((d / n).read_text(encoding='utf-8'))
        r = validate(load('research-plan.json'), load('evidence-ledger.json'), load('analysis-brief.json'))
        self.assertEqual(r['status'], 'PASS', r['failures'] + r['holds'])
        self.assertTrue(r['warnings'])

    def test_schema_errors_fail(self):
        p = copy.deepcopy(P)
        p['gaps'][0]['retrieval_cost'] = 0
        r = validate(p, L)
        self.assertEqual(r['status'], 'FAIL')
        self.assertTrue(any('schema (plan)' in f for f in r['failures']))

    def test_false_coverage(self):
        r = validate(P, EMPTY_LEDGER)
        self.assertEqual(r['status'], 'FAIL')
        self.assertTrue(any('False coverage' in f for f in r['failures']))

    def test_pending_high_impact_gap_holds(self):
        p = copy.deepcopy(P)
        p['gaps'][0]['resolution'] = 'pending'
        r = validate(p, EMPTY_LEDGER)
        self.assertEqual(r['status'], 'HOLD')
        self.assertEqual(r['gap_counts']['pending'], 1)
        self.assertEqual(validate(p, EMPTY_LEDGER, allow_open_gaps=True)['status'], 'PASS')

    def test_pending_low_impact_gap_passes(self):
        p = copy.deepcopy(P)
        p['gaps'][0].update(resolution='pending', decision_impact=2)
        self.assertEqual(validate(p, EMPTY_LEDGER)['status'], 'PASS')

    def test_future_source(self):
        led = copy.deepcopy(L)
        led['sources'][0]['published_at'] = '2026-11-05'
        self.assertEqual(validate(P, led)['status'], 'FAIL')

    def test_same_day_timestamp_is_not_future(self):
        led = copy.deepcopy(L)
        led['sources'][0]['published_at'] = '2026-11-01T09:00:00Z'
        self.assertEqual(validate(P, led)['status'], 'PASS')

    def test_known_critical_gap(self):
        p = copy.deepcopy(P)
        p['gaps'][0]['resolution'] = 'unavailable'
        p['gaps'][0]['limitation'] = 'Issuer does not disclose'
        result = validate(p, EMPTY_LEDGER)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['gap_counts']['unavailable'], 1)
        self.assertTrue(result['warnings'])

    def test_missing_unavailability_rationale(self):
        p = copy.deepcopy(P)
        p['gaps'][0]['resolution'] = 'unavailable'
        self.assertEqual(validate(p, EMPTY_LEDGER)['status'], 'FAIL')

    def test_missing_exclusion_rationale(self):
        p = copy.deepcopy(P)
        p['gaps'][0]['resolution'] = 'excluded'
        self.assertEqual(validate(p, EMPTY_LEDGER)['status'], 'FAIL')

    def test_orphan_observation(self):
        led = copy.deepcopy(L)
        led['observations'][0]['source_id'] = 'no'
        self.assertEqual(validate(P, led)['status'], 'FAIL')

    def test_unsupported_conclusion(self):
        a = copy.deepcopy(A)
        a['conclusions'][0]['evidence_ids'] = ['NO']
        self.assertEqual(validate(P, L, a)['status'], 'FAIL')

    def test_conclusion_without_evidence(self):
        a = copy.deepcopy(A)
        a['conclusions'][0]['evidence_ids'] = []
        self.assertEqual(validate(P, L, a)['status'], 'FAIL')

    def test_unverified_evidence(self):
        led = copy.deepcopy(L)
        led['observations'][0]['status'] = 'unverified'
        self.assertEqual(validate(P, led)['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
