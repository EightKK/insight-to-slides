import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audience_purity import lint_text


class AudiencePurity(unittest.TestCase):
    def test_skill_branding_flagged(self):
        self.assertTrue(lint_text("Insight to Slides | 深掘り分析"))

    def test_version_banner_flagged(self):
        self.assertTrue(lint_text("スキル v1.2 による自動生成"))

    def test_draft_comparison_flagged(self):
        self.assertTrue(lint_text("旧版との比較：Before / After"))

    def test_internal_testing_flagged(self):
        self.assertTrue(lint_text("スキルのテスト49件が成功"))

    def test_methodology_flagged(self):
        self.assertTrue(lint_text("調査プロセスの自己検証"))

    def test_business_uncertainty_allowed(self):
        self.assertFalse(lint_text("関税影響の個別額が公表されていないため、収益性低下の持続性はまだ判断できない。"))

    def test_business_evidence_allowed(self):
        self.assertFalse(lint_text("営業利益率は9.52%から7.86%へ低下。出典：2027年3月期第1四半期決算説明資料。"))

    def test_functional_source_allowed(self):
        self.assertFalse(lint_text("出典・注記　トヨタ自動車 2027年3月期 第1四半期決算"))


if __name__ == "__main__":
    unittest.main()
