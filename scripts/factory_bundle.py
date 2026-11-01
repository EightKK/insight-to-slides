"""Load and period-filter the factory monthly CSV bundle (shared by both factory audits).

Column contract (UTF-8, BOM allowed). `period` is the reporting month YYYY-MM;
"next1"/"next2" mean the two months after it; bom.csv is period-independent master data.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

TABLES = {
    'sales': ('sales_plan_actual_forecast.csv',
              ['period', 'sku', 'customer', 'plan_units', 'shipped_units', 'confirmed_orders_units', 'overdue_units',
               'next1_forecast_units', 'next2_forecast_units', 'unit_price_kJPY', 'unit_customer_cost_kJPY']),
    'profit': ('customer_item_profit.csv',
               ['period', 'sku', 'customer', 'shipped_units', 'unit_price_kJPY', 'unit_customer_cost_kJPY',
                'revenue_mJPY', 'customer_cost_mJPY', 'contribution_mJPY', 'plan_contribution_mJPY']),
    'manufacturing': ('manufacturing_actual.csv',
                      ['period', 'sku', 'planned_good_units', 'actual_good_units', 'wip_starts_units',
                       'wip_open_units', 'wip_close_units', 'scrap_units']),
    'inventory': ('inventory_actual.csv',
                  ['period', 'sku', 'fg_open_units', 'produced_good_units', 'shipped_units', 'fg_close_units',
                   'fg_unit_manufacturing_cost_kJPY', 'fg_close_value_mJPY', 'wip_open_units', 'wip_close_units']),
    'bom': ('bom.csv', ['parent_sku', 'component', 'qty_per_good']),
    'supply': ('component_supply.csv',
               ['period', 'component', 'onhand_start_units', 'next1_confirmed_receipt_units', 'reserve_units',
                'next1_usable_units']),
}
PERIOD = re.compile(r'^\d{4}-(0[1-9]|1[0-2])$')


def _read(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        return list(reader), list(reader.fieldnames or [])


def load_bundle(data_dir, period: str | None = None):
    """Return (tables, period). Raises ValueError for missing files/columns or ambiguous periods."""
    if period is not None and not PERIOD.match(period):
        raise ValueError(f'--period must be YYYY-MM, got {period!r}')
    d = Path(data_dir)
    tables, seen = {}, set()
    for key, (name, required) in TABLES.items():
        path = d / name
        if not path.exists():
            raise ValueError(f'missing input file: {name}')
        rows, fields = _read(path)
        missing = [c for c in required if c not in fields]
        if missing:
            raise ValueError(f'{name} lacks required column(s): {", ".join(missing)}')
        if 'period' in fields:
            seen.update(r['period'] for r in rows)
            if period is not None:
                rows = [r for r in rows if r['period'] == period]
        tables[key] = rows
    if period is None:
        if len(seen) != 1:
            raise ValueError(f'expected exactly one reporting period, found {sorted(seen)}; pass --period YYYY-MM')
        period = next(iter(seen))
    elif period not in seen:
        raise ValueError(f'period {period} not present in data (found {sorted(seen)})')
    for key in ('sales', 'profit', 'manufacturing', 'inventory', 'supply'):
        if not tables[key]:
            raise ValueError(f'{TABLES[key][0]} has no rows for period {period}')
    return tables, period


def bom_map(bom_rows):
    """parent -> component -> summed qty_per_good (duplicate rows accumulate)."""
    out = defaultdict(lambda: defaultdict(float))
    for r in bom_rows:
        out[r['parent_sku']][r['component']] += float(r['qty_per_good'])
    return out


def component_needs(net_units_by_sku, bom):
    needs = defaultdict(float)
    for sku, units in net_units_by_sku.items():
        for component, qty in bom.get(sku, {}).items():
            needs[component] += units * qty
    return dict(needs)


def shortages(needs, usable_by_component):
    """Union of needed and supplied components; a needed component without supply is fully short."""
    out = {}
    for c in sorted(set(needs) | set(usable_by_component)):
        out[c] = max(0.0, needs.get(c, 0.0) - usable_by_component.get(c, 0.0))
    return out


def rounding_tolerance(reported: str) -> float:
    """Half a unit of the reported value's last decimal place (e.g. '31.28' -> 0.005)."""
    s = str(reported).strip()
    decimals = len(s.split('.', 1)[1]) if '.' in s else 0
    return 0.5 * 10 ** -decimals + 1e-9


def matches_reported(computed: float, reported: str) -> bool:
    return abs(float(computed) - float(reported)) <= rounding_tolerance(reported)
