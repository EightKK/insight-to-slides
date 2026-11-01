import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_brief import output_language, validate


class BriefTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads((ROOT / "examples" / "inventory-decision.json").read_text(encoding="utf-8"))

    def test_example_passes_without_warnings(self):
        errors, warnings = validate(self.sample)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_evidence_rejected(self):
        data = deepcopy(self.sample)
        data["slides"][0]["evidence_refs"].append("nonexistent")
        errors, _ = validate(data)
        self.assertTrue(any("nonexistent" in error for error in errors))

    def test_decision_without_options_rejected(self):
        data = deepcopy(self.sample)
        data["slides"][1]["discussion"]["options"] = []
        errors, _ = validate(data)
        self.assertTrue(any("two real options" in error for error in errors))

    def test_calculation_without_formula_rejected(self):
        data = deepcopy(self.sample)
        data["evidence"][4].pop("formula")
        errors, _ = validate(data)
        self.assertTrue(any("formula" in error for error in errors))

    def test_missing_language_defaults_to_japanese(self):
        data = deepcopy(self.sample)
        data["document"].pop("output_language")
        self.assertEqual(output_language(data), "ja")
        errors, warnings = validate(data)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_english_prose_flagged_in_japanese_output(self):
        data = deepcopy(self.sample)
        data["slides"][0]["headline"] = "Total inventory declined while aging stock increased"
        _, warnings = validate(data)
        self.assertTrue(any("S01.headline" in w and "English-only" in w for w in warnings))

    def test_explicit_english_override_respected(self):
        data = deepcopy(self.sample)
        data["document"]["output_language"] = "en"
        data["slides"][0]["headline"] = "Total inventory fell while aging stock increased"
        self.assertEqual(output_language(data), "en")
        errors, warnings = validate(data)
        self.assertEqual(errors, [])
        self.assertFalse(any("S01.headline" in w for w in warnings))
        self.assertTrue(any("document.title" in w for w in warnings))

    def test_invalid_language_tag_rejected(self):
        data = deepcopy(self.sample)
        data["document"]["output_language"] = "Japanese"
        errors, _ = validate(data)
        self.assertTrue(any("output_language" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
