import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import contains_token, normalize_text


class TokenBoundaryTests(unittest.TestCase):
    def test_numbers_on_consecutive_lines_stay_separate(self):
        text = normalize_text("0.36\n3.42\n0.87\n3.55")
        for tok in ["0.36", "3.42", "0.87", "3.55"]:
            self.assertTrue(contains_token(text, tok), tok)

    def test_axis_zero_then_value(self):
        self.assertTrue(contains_token(normalize_text("0\n5.70\nEBITDA"), "5.70"))

    def test_japanese_line_wrap_inside_unit_still_joins(self):
        self.assertTrue(contains_token(normalize_text("−2.22\n億€"), "−2.22億€"))

    def test_sign_still_explicit_after_newline(self):
        text = normalize_text("前年\n−0.66")
        self.assertFalse(contains_token(text, "0.66"))
        self.assertTrue(contains_token(text, "−0.66"))

    def test_digit_boundary_still_enforced(self):
        self.assertFalse(contains_token(normalize_text("112%"), "12%"))


if __name__ == "__main__":
    unittest.main()
