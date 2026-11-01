"""Function-slide titles should match the contents, not an action-title formula."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_brief import validate

class ReferenceSlideTitles(unittest.TestCase):
    def setUp(self):
        self.brief=json.loads((ROOT/'examples/toyota-fy2027-q1.json').read_text(encoding='utf-8'))
        self.page=self.brief['slides'][-1]

    def lint(self):
        return validate(self.brief)

    def test_mixed_sources_notes_accepted(self):
        self.assertEqual(self.page['headline'],'出典・注記')
        errors,warnings=self.lint()
        self.assertFalse(errors)
        self.assertFalse(any('reference page title should' in w for w in warnings))

    def test_sources_only_accepted(self):
        self.page['reference_content_types']=['sources']
        self.page['headline']='出典'
        errors,warnings=self.lint()
        self.assertFalse(errors)
        self.assertFalse(any('reference page title should' in w for w in warnings))

    def test_sources_and_notes_wrong_title_warned(self):
        self.page['headline']='出典'
        errors,warnings=self.lint()
        self.assertFalse(errors)
        self.assertTrue(any('reference page title should be 出典・注記' in w for w in warnings))

    def test_long_explanatory_reference_title_warned(self):
        self.page['headline']='出典・定義・留保条件を最後まで明示する'
        errors,warnings=self.lint()
        self.assertFalse(errors)
        self.assertTrue(any('reference slide title should' in w for w in warnings))

    def test_appendix_title_accepted(self):
        self.page['role']='appendix'
        self.page['headline']='付録'
        self.page['reference_content_types']=['supporting_details']
        errors,warnings=self.lint()
        self.assertFalse(errors)
        self.assertFalse(any('appendix title' in w for w in warnings))

if __name__=='__main__': unittest.main()
