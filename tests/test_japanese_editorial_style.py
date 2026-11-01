import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lint_japanese_style import inspect_segments, load_segments, main

class JapaneseEditorialStyleTests(unittest.TestCase):
    def kinds(self, text):
        return {f['kind'] for f in inspect_segments([(1,text)])}

    def test_empty_importance_is_flagged(self):
        self.assertIn('importance_staging',self.kinds('重要なのは、工場の構造的な課題を見つめ直すことです。'))
    def test_empty_closer_is_flagged(self):
        self.assertIn('empty_closer',self.kinds('今後も継続的に注視します。'))
    def test_unnecessary_contrast_is_flagged(self):
        self.assertIn('performative_contrast',self.kinds('単なる在庫削減ではなく、収益力向上が重要です。'))
    def test_rhetorical_warning_is_flagged(self):
        self.assertIn('rhetorical_warning',self.kinds('在庫総額＋0.2%の裏で、仕掛品だけが＋0.8%増加'))
    def test_business_presentation_finding_remains_clean(self):
        self.assertEqual([],inspect_segments([(2,'在庫総額は0.2%増、仕掛品は0.8%増。')]))
    def test_clear_numeric_claim_is_not_flagged(self):
        self.assertEqual([],inspect_segments([(2,'8月の出荷額は前月比1.5%増。価格調整後は横ばい。')]))
    def test_necessary_uncertainty_not_flagged(self):
        self.assertEqual([],inspect_segments([(3,'原価上昇が一因となった可能性があるが、要因別金額は未公表。')]))
    def test_functional_heading_not_flagged(self):
        self.assertEqual([],inspect_segments([(12,'出典・注記')]))
    def test_repeat_detections_high(self):
        findings=inspect_segments([(1,'重要なのは採算です。'),(2,'重要なのは数量です。'),(3,'重要なのは納期です。')])
        self.assertIn('repetitive_deck_voice',{f['kind'] for f in findings})
    def test_utf8_md_input(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.md';p.write_text('## 出典・注記\n重要なのは分析です。',encoding='utf-8')
            self.assertEqual(1,len(inspect_segments(load_segments(p))))
    def test_pptx_shape_extract_and_page(self):
        xml="""<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>重要なのは利益です。</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>"""
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.pptx'
            with ZipFile(p,'w') as z:z.writestr('ppt/slides/slide2.xml',xml)
            findings=inspect_segments(load_segments(p))
            self.assertEqual(2,findings[0]['location'])
            self.assertEqual('importance_staging',findings[0]['kind'])
    def test_linter_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.txt';p.write_text('重要なのは全体です。',encoding='utf-8')
            before=p.read_bytes()
            self.assertEqual(0,main([str(p)]))
            self.assertEqual(before,p.read_bytes())

if __name__=='__main__':unittest.main()
