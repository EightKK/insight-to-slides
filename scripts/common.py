"""Shared helpers for the insight-to-slides scripts.

Exit-code convention for every gate script:
  0 = PASS / READY, 1 = FAIL or invalid input, 2 = HOLD / REVIEW REQUIRED.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / 'schemas'
SCHEMA_VERSION = '1.0.0'
EXIT_PASS, EXIT_FAIL, EXIT_HOLD = 0, 1, 2
EXIT_CODES_HELP = 'Exit codes: 0 = PASS/READY, 1 = FAIL or invalid input, 2 = HOLD/REVIEW REQUIRED.'

# Windows pipes default to the locale code page (e.g. cp932), which cannot encode
# characters such as '—'; emit UTF-8 so output does not depend on the host.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(encoding='utf-8')


class Parser(argparse.ArgumentParser):
    """ArgumentParser whose usage errors exit 1 (2 is reserved for HOLD)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('epilog', EXIT_CODES_HELP)
        kwargs.setdefault('formatter_class', argparse.RawDescriptionHelpFormatter)
        super().__init__(*args, **kwargs)

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f'{self.prog}: error: {message}', file=sys.stderr)
        sys.exit(EXIT_FAIL)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def write_text(path, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def schema_errors(data, schema_file: str) -> list[str]:
    """Validate with JSON Schema draft 2020-12; returns readable messages."""
    from jsonschema import Draft202012Validator
    schema = read_json(SCHEMA_DIR / schema_file)
    out = []
    for e in sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path]):
        loc = '/'.join(str(p) for p in e.absolute_path) or '(root)'
        out.append(f'{loc}: {e.message}')
    return out


def run(main) -> None:
    """Run a CLI main(); unexpected input problems become exit 1 instead of a traceback."""
    try:
        code = main()
    except SystemExit:
        raise
    except (OSError, ValueError, KeyError, TypeError, IndexError, ZeroDivisionError) as exc:
        print(f'ERROR: {type(exc).__name__}: {exc}', file=sys.stderr)
        code = EXIT_FAIL
    sys.exit(code or 0)


def load_pymupdf():
    try:
        import pymupdf as module
    except ImportError:  # older PyMuPDF releases only expose the fitz name
        import fitz as module
    return module


def parse_date(value) -> date:
    """Parse YYYY-MM-DD or an ISO-8601 timestamp (Z allowed) to a calendar date."""
    s = str(value).strip()
    try:
        return date.fromisoformat(s)
    except ValueError:
        return datetime.fromisoformat(s.replace('Z', '+00:00')).date()


# Minus-like glyphs, including Japanese accounting negatives (▲, △), become ASCII '-'.
_MINUS = dict.fromkeys(map(ord, '−–—―‐‑‒▲△﹣'), '-')


def normalize_text(value) -> str:
    """NFKC (full-width digits/％/＋), unify minus signs, drop whitespace and thousands separators."""
    x = unicodedata.normalize('NFKC', str(value)).translate(_MINUS)
    # Keep a boundary between separate numbers (e.g. chart labels on consecutive lines),
    # otherwise '3.42\n0.87' would collapse to '3.420.87' and hide both values.
    x = re.sub(r'(?<=[\d%])\s+(?=[\d+\-])', '|', x)
    x = re.sub(r'\s+', '', x)
    x = re.sub(r'(?<=\d),(?=\d{3}(?!\d))', '', x)
    return x


def contains_token(normalized_text: str, token) -> bool:
    """Sign- and digit-boundary-aware search: '12%' does not match '-12%', '112%' or '12.5%'."""
    t = normalize_text(token)
    if not t:
        return False
    pattern = re.escape(t)
    if t[0].isdigit():
        pattern = r'(?<![\d.+\-])' + pattern
    if t[-1].isdigit():
        pattern += r'(?!\.?\d)'
    return re.search(pattern, normalized_text) is not None
