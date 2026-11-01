"""Command-line contract: documented example commands and the shared exit-code convention."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / 'examples'
FX = ROOT / 'tests' / 'fixtures'
FACTORY = EX / 'factory-monthly-synthetic' / 'data'
TOYOTA = EX / 'toyota-deep-research'


def cli(script, *args):
    return subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / script), *map(str, args)],
                          capture_output=True, text=True, encoding='utf-8', timeout=120)


class CliExitCodeTests(unittest.TestCase):
    def assertExit(self, expected, script, *args):
        r = cli(script, *args)
        self.assertEqual(r.returncode, expected, f'{script} {args}\n{r.stdout[-800:]}\n{r.stderr[-800:]}')
        self.assertNotIn('Traceback', r.stderr)
        return r

    def test_documented_examples(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertExit(0, 'validate_brief.py', EX / 'toyota-fy2027-q1.json')
            self.assertExit(0, 'audit_calculations.py', FX / 'komatsu-values.json', FX / 'komatsu-calculations.json')
            self.assertExit(0, 'audit_factory_monthly.py', FACTORY)
            self.assertExit(2, 'audit_factory_decision_readiness.py', FACTORY)
            self.assertExit(0, 'audit_operational_case.py', EX / 'fictional-mixed-model-wip.json')
            self.assertExit(0, 'evaluate_decision_quality.py', FX / 'sandvik-2026-q3-argumentation.json', '--out', Path(td) / 'd.json')
            self.assertExit(0, 'research_gate.py', TOYOTA / 'research-plan.json', TOYOTA / 'evidence-ledger.json',
                            '--analysis', TOYOTA / 'analysis-brief.json', '--out', Path(td) / 'g.json')
            self.assertExit(0, 'audit_public_data.py', EX / 'public-data-manifest.json')

    def test_shortage_holds_even_with_all_confirmations(self):
        self.assertExit(2, 'audit_factory_decision_readiness.py', FACTORY, '--backlog', 'included',
                        '--eligible-stock-confirmed', '--supply-eta-confirmed', '--capacity-confirmed',
                        '--inventory-policy-confirmed')

    def test_usage_and_input_errors_exit_1(self):
        self.assertExit(1, 'validate_brief.py')
        self.assertExit(1, 'audit_factory_monthly.py', FACTORY, '--period', 'October')
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / 'bad.json'
            bad.write_text('{not json', encoding='utf-8')
            for script in ('validate_brief.py', 'evaluate_decision_quality.py', 'audit_public_data.py', 'audit_operational_case.py'):
                self.assertExit(1, script, bad)

    def test_failing_inputs_exit_1(self):
        self.assertExit(1, 'validate_brief.py', FX / 'komatsu-values.json')
        self.assertExit(1, 'evaluate_decision_quality.py', EX / 'toyota-fy2027-q1.json')

    def test_review_required_exits_2(self):
        with tempfile.TemporaryDirectory() as td:
            draft = Path(td) / 'draft.txt'
            draft.write_text('旧版との比較：Before / After', encoding='utf-8')
            self.assertExit(2, 'audience_purity.py', draft)

    def test_help_documents_exit_codes(self):
        for script in ('validate_brief.py', 'audit_calculations.py', 'audit_factory_monthly.py',
                       'audit_factory_decision_readiness.py', 'audit_operational_case.py', 'audit_public_data.py',
                       'evaluate_decision_quality.py', 'research_gate.py', 'review_deck.py', 'semantic_qa.py',
                       'audience_purity.py', 'lint_japanese_style.py', 'render_review.py', 'make_review_packet.py'):
            r = self.assertExit(0, script, '--help')
            self.assertIn('Exit codes', r.stdout)


if __name__ == '__main__':
    unittest.main()
