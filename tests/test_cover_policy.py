"""A conventional title page must remain separate from the first message."""
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_brief import validate

class CoverPolicyTests(unittest.TestCase):
    def setUp(self):
        self.brief = json.loads((ROOT / 'examples/inventory-decision.json').read_text(encoding='utf-8'))

    def test_neutral_cover_is_accepted(self):
        self.brief['document']['cover'] = {'title': '工場月次運営レビュー', 'reporting_period': '2026年10月', 'scope':'架空工場'}
        errors, warnings = validate(self.brief)
        self.assertFalse(errors, errors)
        self.assertFalse(any('cover.' in w for w in warnings), warnings)

    def test_cover_rejects_message_field(self):
        self.brief['document']['cover'] = {'title': '月次運営レビュー', 'takeaway': '需要と生産に乖離がある'}
        errors, _ = validate(self.brief)
        self.assertTrue(any('document.cover.takeaway is not permitted' in e for e in errors), errors)

    def test_cover_requires_title(self):
        self.brief['document']['cover'] = {'reporting_period': '2026年10月'}
        errors, _ = validate(self.brief)
        self.assertTrue(any('document.cover.title' in e for e in errors), errors)

    def test_cover_optional_for_non_deck(self):
        self.brief['document'].pop('cover', None)
        errors, _ = validate(self.brief)
        self.assertFalse(errors, errors)

if __name__ == '__main__':
    unittest.main()
