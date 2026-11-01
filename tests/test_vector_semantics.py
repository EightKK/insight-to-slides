"""Semantic contracts: reject source and PDF-geometry contradictions."""
import importlib.util
import sys
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from common import load_pymupdf
fitz=load_pymupdf()
spec=importlib.util.spec_from_file_location('semantic_qa',ROOT/'scripts/semantic_qa.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)

class VectorSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.values={'prev':100,'current':90,'fx':10,'other':-20,'revprev':200,'revcurrent':220,'segmentA':60,'segmentB':30}
        self.dir=tempfile.TemporaryDirectory()
        self.pdf_path=Path(self.dir.name)/'vector.pdf'
        doc=fitz.open()
        p=doc.new_page(width=1000,height=600)
        p.insert_text((20,40),'forecast label company outlook (not actual)')
        p.insert_text((20,65),'SEGMENT DO NOT SUM')
        p.draw_rect(fitz.Rect(310,200,480,234),color=None,fill=(.77,.34,.29))
        p.draw_rect(fitz.Rect(480,310,680,344),color=None,fill=(0,.49,.53))
        doc.save(self.pdf_path)
        self.pdf=fitz.open(self.pdf_path)

    def tearDown(self):
        self.pdf.close();self.dir.cleanup()

    def test_reconcile_passes(self):
        c={'id':'delta','type':'reconcile','current':'current','previous':'prev','components':['fx','other']}
        self.assertTrue(qa.check(c,self.values,self.pdf)['passed'])

    def test_reconcile_rejects_bad_components(self):
        v=dict(self.values,other=-19)
        c={'id':'delta','type':'reconcile','current':'current','previous':'prev','components':['fx','other']}
        self.assertFalse(qa.check(c,v,self.pdf)['passed'])

    def test_direction_checks_source(self):
        c={'id':'sign','type':'numeric_direction','current':'current','previous':'prev','expected':'down'}
        self.assertTrue(qa.check(c,self.values,self.pdf)['passed'])
        c['expected']='up'
        self.assertFalse(qa.check(c,self.values,self.pdf)['passed'])

    def test_negative_vector_left(self):
        c={'id':'neg','type':'signed_vector_bar','page':1,'current':'current','previous':'prev','axis_x_fraction':.48,'y_fraction_range':[.32,.40],'rgb':[196,86,74]}
        self.assertTrue(qa.check(c,self.values,self.pdf)['passed'])

    def test_negative_vector_rejects_reversed_sign(self):
        c={'id':'neg','type':'signed_vector_bar','page':1,'current':'revcurrent','previous':'revprev','axis_x_fraction':.48,'y_fraction_range':[.32,.40],'rgb':[196,86,74]}
        self.assertFalse(qa.check(c,self.values,self.pdf)['passed'])

    def test_positive_vector_right(self):
        c={'id':'positive','type':'signed_vector_bar','page':1,'current':'revcurrent','previous':'revprev','axis_x_fraction':.48,'y_fraction_range':[.50,.59],'rgb':[0,126,136]}
        self.assertTrue(qa.check(c,self.values,self.pdf)['passed'])

    def test_forecast_text(self):
        c={'id':'f','type':'forecast_label','page':1,'tokens':['forecast label','not actual']}
        self.assertTrue(qa.check(c,self.values,self.pdf)['passed'])
        c['tokens'].append('missing')
        self.assertFalse(qa.check(c,self.values,self.pdf)['passed'])

    def test_scope_guard(self):
        c={'id':'scope','type':'scope_caveat','page':1,'tokens':['SEGMENT','DO NOT SUM']}
        self.assertTrue(qa.check(c,self.values,self.pdf)['passed'])

    def test_missing_number_is_not_pass(self):
        c={'id':'err','type':'numeric_direction','current':'unknown','previous':'prev','expected':'up'}
        with self.assertRaises(ValueError):qa.check(c,self.values,self.pdf)

    def test_low_contrast_text_on_saturated_bar_is_detected(self):
        s=__import__('sys')
        s.path.insert(0,str(ROOT/'scripts'))
        from render_review import low_contrast_vector_text
        d=fitz.open()
        pg=d.new_page(width=700,height=400)
        pg.draw_rect(fitz.Rect(180,155,490,192),fill=(.77,.34,.29),color=None)
        pg.insert_text((210,183),'DECLINE',fontsize=20,color=(.77,.34,.29))
        self.assertTrue(any('DECLINE' in w['text'] for w in low_contrast_vector_text(pg)))
        d.close()

    def test_high_contrast_text_on_bar_is_not_false_positive(self):
        s=__import__('sys');s.path.insert(0,str(ROOT/'scripts'))
        from render_review import low_contrast_vector_text
        d=fitz.open();pg=d.new_page(width=700,height=400)
        pg.draw_rect(fitz.Rect(180,155,490,192),fill=(.77,.34,.29),color=None)
        pg.insert_text((210,183),'CLEAR',fontsize=20,color=(1,1,1))
        self.assertEqual(low_contrast_vector_text(pg),[])
        d.close()

    def test_page_zero_is_rejected_not_last_page(self):
        c={'id':'p0','type':'required_text','page':0,'tokens':['forecast label']}
        with self.assertRaises(ValueError):qa.check(c,self.values,self.pdf)

    def test_sign_explicit_token_matching(self):
        from common import contains_token, normalize_text
        text=normalize_text('営業利益 ▲１２％ 売上 +3.5% 合計 1,234')
        self.assertTrue(contains_token(text,'-12%'))
        self.assertTrue(contains_token(text,'▲12%'))
        self.assertTrue(contains_token(text,'△12％'))
        self.assertFalse(contains_token(text,'12%'))
        self.assertFalse(contains_token(text,'+12%'))
        self.assertTrue(contains_token(text,'+3.5%'))
        self.assertFalse(contains_token(text,'3.5%'))
        self.assertTrue(contains_token(text,'1234'))
        self.assertFalse(contains_token(text,'123'))

    def test_flat_vector_passes_without_signed_bar(self):
        v=dict(self.values,flatprev=100,flatcur=100)
        c={'id':'flat','type':'signed_vector_bar','page':1,'current':'flatcur','previous':'flatprev','axis_x_fraction':.48,'y_fraction_range':[.05,.15],'rgb':[196,86,74]}
        self.assertTrue(qa.check(c,v,self.pdf)['passed'])
        c['y_fraction_range']=[.32,.40]  # a red bar extends left of the axis here
        self.assertFalse(qa.check(c,v,self.pdf)['passed'])

    def test_relative_tolerance_for_large_units(self):
        v={'prev':1_000_000,'current':1_000_500}
        c={'id':'d','type':'numeric_direction','current':'current','previous':'prev','expected':'flat','relative_tolerance':0.001}
        self.assertTrue(qa.check(c,v,self.pdf)['passed'])

    def test_real_brief_has_japanese_default(self):
        from importlib import util
        s=util.spec_from_file_location('validate_brief',ROOT/'scripts/validate_brief.py')
        m=util.module_from_spec(s);s.loader.exec_module(m)
        j=json.loads((ROOT/'examples/toyota-fy2027-q1.json').read_text(encoding='utf-8'))
        errors,warnings=m.validate(j)
        self.assertEqual(errors,[])
        self.assertEqual(j['document']['output_language'],'ja')

if __name__=='__main__':unittest.main()
