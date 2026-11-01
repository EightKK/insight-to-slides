"""Helpers that copy and mutate the synthetic factory CSV bundle in a temporary directory."""
import csv
import shutil
import tempfile
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / 'examples' / 'factory-monthly-synthetic' / 'data'


def copy_fixture():
    td = tempfile.TemporaryDirectory()
    for f in FIXTURE.glob('*.csv'):
        shutil.copy2(f, Path(td.name) / f.name)
    return td


def read_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as fh:
        r = csv.DictReader(fh)
        return list(r), list(r.fieldnames)


def write_rows(path, rows, fields):
    with Path(path).open('w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def edit(folder, name, fn):
    """Apply fn(rows) -> rows to one CSV in folder."""
    rows, fields = read_rows(Path(folder) / name)
    write_rows(Path(folder) / name, fn(rows), fields)


def set_period(folder, period):
    for f in Path(folder).glob('*.csv'):
        rows, fields = read_rows(f)
        if 'period' in fields:
            for r in rows:
                r['period'] = period
            write_rows(f, rows, fields)


def append_period(folder, period):
    """Duplicate every period-bearing row under another period (multi-period bundle)."""
    for f in Path(folder).glob('*.csv'):
        rows, fields = read_rows(f)
        if 'period' in fields:
            write_rows(f, rows + [dict(r, period=period) for r in rows], fields)
