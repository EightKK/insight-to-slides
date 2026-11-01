# Factory monthly review: from multi-ledger data to a decision

Use this playbook when a plant or business review can join several of: sales plan/actual/forecast, manufacturing output, inventory, customer-by-item price and variable cost, BOM, and component supply. It applies by analogy to project, operating and investment reviews. The goal is a **decision**, not a reproduction of source dashboards.

If only public or aggregate data exist, use `public-operational-data-boundary.md` instead; never fill plant ledgers with synthetic values presented as real.

## 1. Pin down the grain of every dataset

1. Record period, plant, SKU, customer, unit, currency, legal entity and status (plan / firm order / shipment / backlog / forecast) for each file. These are different measures; never substitute one for another.
2. Join sales, production, FG inventory and BOM at canonical SKU; keep customer granularity for price, variable cost, contribution and commitments.
3. Check BOM expansion: unit conversions, approved versus alternate BOMs, validity dates, and duplicate parent–component rows (they add, they do not overwrite).

## 2. Reconcile before telling any causal story

- `FG opening + good completions − shipments ± permitted adjustments = FG closing`
- `WIP opening + starts − completions − scrap ± adjustments = WIP closing`
- Customer shipment totals equal the inventory ledger's shipments per SKU.
- `revenue = shipped × unit price`; `contribution = shipped × (unit price − customer-specific variable unit cost)`.

Any unexplained residual blocks publication until explained. Call the profit measure **contribution / 限界利益** unless fixed costs are assigned and documented; never label it operating profit (営業利益). Value FG inventory with a documented valuation policy, not customer-specific selling costs.

## 3. Executive relevance on slide 2

A plant manager needs financial exposure, service consequences and controllable decisions first. When customer-SKU variable cost data exist, put **plan versus actual contribution** and its link to production and finished goods on the first substantive slide (physical slide 2, after a neutral cover). Never substitute a production-attainment rate for profitability.

Working executive question: *What did the plant lose, why might it have happened, and which decision can change the next period?* Each answer needs a claim ID, numeric evidence, time scope and open dependencies.

## 4. Cross-period demand: a decision-blocking gate

For each customer-SKU, separate:

- shipment and firm-order backlog at the previous period end;
- next-period baseline forecast and confirmed orders;
- whether prior backlog is **included in** or **excluded from** the forecast;
- allocated or quality-held FG versus freely available FG at the supply date;
- production requirement and component supply after BOM expansion.

Arithmetic:

- `total_demand = next_period_forecast + (0 if backlog_included else valid_carryover_backlog)`
- `net_build = max(0, total_demand − eligible_unallocated_FG)` per SKU
- `component_need = Σ net_build × approved_BOM_qty`
- `usable_supply = on_hand + firm_receipts − reservations − holds`
- `shortage = max(0, component_need − usable_supply)` for **every needed component**; a needed component with no supply record is a shortage, not zero.

When backlog inclusion is **unknown**, do not add backlog unconditionally and do not ignore it. Publish both conditional cases (pattern `conditional_bom_cases`), state that they are alternatives rather than additive, and hold any definitive expedite or purchase quantity until reconciled. Confirmed orders can differ from overdue orders through cancellation, rescheduling and customer consent.

A correct formula is not enough; state and check each input's definition. If eligible stock, backlog treatment, capacity, yield or supplier ETA is unknown, the decision stays conditional. A cross-period inconsistency found after the deck is drafted is a material content defect requiring revision.

## 5. Inventory adequacy is not one month of cover

Compare FG with at least the next two **distinct, non-overlapping** periods of forecast, plus documented lead time, safety stock or target cover, minimum lot, shelf life, quality holds and planned shutdowns (pattern `inventory_demand_cover`). Without an agreed target, write `在庫は需要の約Xか月分` rather than `過剰` / `滞留` / `処分対象`. Inventory book-value reduction is not released cash without a cash-flow mechanism.

## 6. Alternatives and the decision request

- Do not end with a preselected action list. Present at least two credible choices, including one that defers or declines the favoured action.
- Compare contribution **net of** known fees, customer commitments and penalties, units left undelivered, time to impact, feasibility and open evidence. Show who is underserved under each allocation policy, not only contribution per scarce component.
- Never present revenue as a profit benefit. Scenario contribution is not cash. A quoted expedite fee applies only to the quoted quantity. Treat `benefit − fee` as a conditional sensitivity, not an approved return.
- Separate **recommendation**, **authorisation requested**, **information still needed**, and **execution after approval**. Name the decision owner and the go/no-go conditions. Do not invent an owner, threshold or deadline that the user has not supplied.
- Flag negative customer-SKU contribution even when its revenue grows. A SKU can hold FG and overdue orders at the same time; check allocation, quality hold, cut-off and packaging before blaming low output.

## 7. Suggested sequence

Cover → financial and service headline (plan vs actual contribution) → contribution driver bridge → production mix and stock evidence → backlog and availability boundary → two-period inventory cover → conditional BOM cases → alternatives with constraints → decision gates and owners → `出典・注記` / `付録`.

## 8. Headlines in natural Japanese

A good headline is a clear result plus a qualification only when needed. `売上高は計画比86%。限界利益は81%` is precise but misses the contrast; `生産数量は計画達成、限界利益は計画比81%` adds a meaningful contrast without drama. Do not flatten headlines into category labels (`在庫実績`, `生産状況`) to sound less artificial. See `japanese-editorial-style.md`.

## 9. Automated checks

Run both on the normalised CSV bundle before drafting decisions:

```bash
python3 scripts/audit_factory_monthly.py <data-dir> --period YYYY-MM --out factory-audit.json
python3 scripts/audit_factory_decision_readiness.py <data-dir> --period YYYY-MM --out readiness.json
```

### Data bundle contract

All files UTF-8 (a BOM is fine). `period` is `YYYY-MM`; `next1` and `next2` are the two following months. If the bundle holds several periods, pass `--period`.

| File | Required columns (optional in brackets) |
| --- | --- |
| `sales_plan_actual_forecast.csv` | period, sku, customer, plan_units, shipped_units, confirmed_orders_units, overdue_units, next1_forecast_units, next2_forecast_units, unit_price_kJPY, unit_customer_cost_kJPY |
| `customer_item_profit.csv` | period, sku, customer, shipped_units, unit_price_kJPY, unit_customer_cost_kJPY, revenue_mJPY, customer_cost_mJPY, contribution_mJPY, plan_contribution_mJPY (next1_forecast_contribution_mJPY) |
| `manufacturing_actual.csv` | period, sku, planned_good_units, actual_good_units, wip_starts_units, wip_open_units, wip_close_units, scrap_units (production_achievement_pct) |
| `inventory_actual.csv` | period, sku, fg_open_units, produced_good_units, shipped_units, fg_close_units, fg_unit_manufacturing_cost_kJPY, fg_close_value_mJPY, wip_open_units, wip_close_units |
| `bom.csv` | parent_sku, component, qty_per_good (component_name) — master data without period; duplicate rows add up |
| `component_supply.csv` | period, component, onhand_start_units, next1_confirmed_receipt_units, reserve_units, next1_usable_units (expedite_qty_option_units, expedite_fee_per_unit_kJPY, expedite_delivery_status) |

Map the user's own ledgers onto these columns first; record the mapping in the production package. Reported mJPY values are matched within half a unit of their last decimal place. A worked bundle is in `examples/factory-monthly-synthetic/data/`.

`HOLD` is an expected, informative status for an unresolved decision: carry the open conditions into the deck as conditional facts. Exit codes: READY 0, HOLD 2, FAIL 1. `READY` means the arithmetic reconciles, no shortage remains in the selected case and the confirmation flags were supplied; it does not validate the real business circumstances. Keep audit outputs in the production package.
