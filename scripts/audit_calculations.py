#!/usr/bin/env python3
"""Recompute a narrowly-defined arithmetic inventory against a numeric JSON datasource.

Usage: python3 scripts/audit_calculations.py source-values.json calculations.json [--out report.json]

Expressions may contain numbers, parentheses, + - * / and dotted identifiers that
resolve to numeric (int/float, not bool or string) leaves of the source tree.
No arbitrary Python is evaluated. Each entry may set `absolute_tolerance`
(default 0.02) and/or `relative_tolerance` (fraction of |expected|); the larger wins.
"""
import ast
import math
import operator
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, dumps, read_json, run, write_text

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.USub: operator.neg, ast.UAdd: operator.pos}


def _numeric(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Non-numeric value for {name}: {value!r}")
    return value


def resolve(node, source):
    if isinstance(node, ast.Name):
        if node.id not in source:
            raise ValueError(f"Unknown identifier: {node.id}")
        value = source[node.id]
        return value if isinstance(value, dict) else _numeric(value, node.id)
    if isinstance(node, ast.Attribute):
        parent = resolve(node.value, source)
        if not isinstance(parent, dict) or node.attr not in parent:
            raise ValueError(f"Missing value: {node.attr}")
        value = parent[node.attr]
        return value if isinstance(value, dict) else _numeric(value, node.attr)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_numeric(resolve(node.left, source), 'left operand'),
                                  _numeric(resolve(node.right, source), 'right operand'))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_numeric(resolve(node.operand, source), 'operand'))
    raise ValueError("Unsupported calculation syntax")


def audit(source, definitions):
    results = []
    for calc in definitions.get('calculations', []):
        try:
            val = float(_numeric(resolve(ast.parse(calc['expression'], mode='eval').body, source), calc['expression']))
            expected = float(_numeric(calc['expected'], 'expected'))
            tolerance = max(float(calc.get('absolute_tolerance', .02)),
                            float(calc.get('relative_tolerance', 0)) * abs(expected))
            passed = math.isfinite(val) and abs(val - expected) <= tolerance
            results.append({'id': calc['id'], 'expression': calc['expression'],
                            'actual': val, 'expected': expected,
                            'tolerance': tolerance, 'passed': passed})
        except (ValueError, SyntaxError, TypeError, ZeroDivisionError, KeyError, OverflowError) as e:
            results.append({'id': calc.get('id', 'unknown'), 'passed': False, 'error': str(e)})
    return results


def main(argv=None):
    p = Parser(description=__doc__)
    p.add_argument('source')
    p.add_argument('definitions')
    p.add_argument('--out')
    args = p.parse_args(argv)
    results = audit(read_json(args.source), read_json(args.definitions))
    ok = bool(results) and all(x['passed'] for x in results)
    report = {'status': 'PASS' if ok else 'FAIL', 'method': 'AST-limited recomputation',
              'counts': {'total': len(results), 'passed': sum(x['passed'] for x in results)}, 'results': results}
    print(dumps(report))
    if args.out:
        write_text(args.out, dumps(report) + '\n')
    return EXIT_PASS if ok else EXIT_FAIL


if __name__ == '__main__':
    run(main)
