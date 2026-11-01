"""Rendered-deck checks: brief audit tokens, arithmetic inventory, text-layer review and rendering (not human comprehension)."""
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from common import load_pymupdf
fitz=load_pymupdf()
from validate_brief import validate
from review_deck import report,normal,upward_revision_direction_conflict
from render_review import render_file
from audit_calculations import audit

class RenderSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brief=json.loads((ROOT/'tests/fixtures/komatsu-fy2027-h1.json').read_text(encoding='utf8'))
        cls.catalog=json.loads((ROOT/'patterns/catalog.json').read_text(encoding='utf8'))
        cls.formulas=json.loads((ROOT/'tests/fixtures/komatsu-calculations.json').read_text(encoding='utf8'))
        cls.values=json.loads((ROOT/'tests/fixtures/komatsu-values.json').read_text(encoding='utf8'))
        cls.schema=json.loads((ROOT/'schemas/communication-brief.schema.json').read_text(encoding='utf8'))

    def test_original_patterns_remain_and_schema_identifiers_match(self):
        all_ids={p['id'] for p in self.catalog['patterns']}
        self.assertGreaterEqual(len(all_ids),19)
        self.assertIn("reported_vs_constant_currency",all_ids)
        self.assertIn("guidance_revision",all_ids)
        self.assertEqual(all_ids,set(self.schema['$defs']['slide']['properties']['visual']['properties']['pattern_id']['enum']))

    def test_manufacturing_example_is_valid_and_japanese(self):
        err,warn=validate(self.brief)
        self.assertEqual(err,[])
        self.assertEqual(warn,[])
        self.assertEqual(self.brief['document']['output_language'],'ja')
        self.assertEqual(len(self.brief['slides']),11)

    def test_audit_tokens_required(self):
        sample=deepcopy(self.brief)
        sample['slides'][1].pop('audit_tokens')
        errors,_=validate(sample)
        self.assertTrue(any('audit_tokens' in err for err in errors))

    def test_formula_inventory_recalculates(self):
        items=audit(self.values,self.formulas)
        self.assertEqual(len(items),17)
        self.assertTrue(all(item['passed'] for item in items))

    def test_source_definitions_dont_mix_quarter_and_h1(self):
        self.assertGreater(self.values['H1']['sales_2026'],self.values['Q2']['sales_2026'])
        self.assertGreater(self.values['Q2']['operating_2025'],0)
        self.assertEqual(self.values['regions_Q2']['total_delta_reported'],1338)

    def _pdf_with_text(self, text):
        t=tempfile.TemporaryDirectory()
        pdf=Path(t.name)/'sample.pdf'
        doc=fitz.open();page=doc.new_page(width=700,height=400)
        page.insert_text((44,90),text,fontname='helv',fontsize=18)
        doc.save(pdf);doc.close()
        return t,pdf

    def test_number_normalization_and_direction_gate(self):
        self.assertEqual(normal('＋14.1%'),normal('+14.1％'))
        self.assertTrue(upward_revision_direction_conflict(normal('通期業績を上方修正 ↓')))
        self.assertFalse(upward_revision_direction_conflict(normal('通期業績を上方修正 ↑')))
        t,pdf=self._pdf_with_text('Revision upward')
        try:
            # The glyph check is more meaningful in a Japanese-font PDF.
            # The normalization assertion guards its numeric matching.
            man=Path(t.name)/'manifest.json'
            man.write_text(json.dumps([{'slide_id':'A01','headline':'Revision upward','visual_tokens':['14.1%']}]))
            r=report(pdf,man)
            self.assertTrue(any(issue['type']=='missing_visual_tokens' and issue['severity']=='error' for issue in r['issues']))
            self.assertEqual(r['status'],'FAIL')
        finally:t.cleanup()

    def _japanese_pdf(self, lines):
        t=tempfile.TemporaryDirectory()
        pdf=Path(t.name)/'jp.pdf'
        doc=fitz.open()
        for page_lines in lines:
            page=doc.new_page(width=960,height=540)
            page.insert_font(fontname='jp',fontbuffer=fitz.Font('japan').buffer)
            for i,line in enumerate(page_lines):
                page.insert_text((40,60+40*i),line,fontname='jp',fontsize=20)
        doc.save(pdf);doc.close()
        return t,pdf

    def test_wrong_number_fails_gate(self):
        t,pdf=self._japanese_pdf([['表紙'],['営業利益は▲１２％減少','売上高 1,234億円','出典: 会社資料']])
        try:
            man=Path(t.name)/'manifest.json'
            spec=[{'slide_id':'S01','headline':'表紙','visual_tokens':[]},
                  {'slide_id':'S02','headline':'営業利益は▲12%減少','visual_tokens':['1234億円','-12%']}]
            man.write_text(json.dumps(spec,ensure_ascii=False),encoding='utf-8')
            self.assertEqual(report(pdf,man)['status'],'PASS')
            spec[1]['visual_tokens']=['9,999億円']
            man.write_text(json.dumps(spec,ensure_ascii=False),encoding='utf-8')
            self.assertEqual(report(pdf,man)['status'],'FAIL')
            spec[1]['visual_tokens']=['12%']  # unsigned token must not match a negative figure
            man.write_text(json.dumps(spec,ensure_ascii=False),encoding='utf-8')
            self.assertEqual(report(pdf,man)['status'],'FAIL')
        finally:t.cleanup()

    def test_headline_missing_is_error(self):
        t,pdf=self._pdf_with_text('Financial results 2026')
        try:
            man=Path(t.name)/'manifest.json'
            man.write_text(json.dumps([{'slide_id':'A01','headline':'A different headline','visual_tokens':[]}]))
            r=report(pdf,man)
            self.assertFalse(r['pass_machine_gates'])
            self.assertTrue(any(i['type']=='missing_headline' for i in r['issues']))
        finally:t.cleanup()

    def test_overlap_detector_reports_major_collisions(self):
        with tempfile.TemporaryDirectory() as td:
            pdf=Path(td)/'intersections.pdf'
            doc=fitz.open();page=doc.new_page(width=700,height=400)
            page.insert_text((60,130),'FIRST LINE',fontname='helv',fontsize=23)
            page.insert_text((84,130),'SECOND LINE',fontname='helv',fontsize=23)
            doc.save(pdf);doc.close()
            result=render_file(pdf,Path(td)/'qa',dpi=60)
            self.assertGreaterEqual(result['machine_checks']['text_overlap_warning_count'],1)

if __name__=='__main__':unittest.main()
