# Public Data Granularity and Disclosure Boundaries

## Why this matters

When building a board, plant, or manufacturing-management briefing using public data, an official statistic can be true at the *industry* level and still provide no evidence about one specific plant. An attractive slide must not conceal this inference gap.

## Required provenance fields

For each observed metric, record `source_url`, release/reference date, geography, entity, sector or product grouping, observation granularity, unit, seasonal adjustment, source status (original/preliminary/revised/advance), and whether the measure is directly observed or a calculated proxy.

## Common forbidden substitutions

| Needed for plant operations | Public substitute | Why it is not equivalent |
|---|---|---|
| Production units per SKU/line | Sector shipment revenue | Prices and mix change without any change in units |
| Confirmed customer orders | Industry unfilled-order aggregate | Does not establish an order for a particular customer's item |
| Finished goods available to promise | Industry total inventories | Includes raw materials, WIP, and restricted stock |
| Customer-item variable contribution | Industry producer price index | Lacks customer contract price and actual material/conversion cost |
| Engineering BOM | Industry input price index | A price basket is not a product/component relationship |
| Plant sales forecast | Statistical advance survey indicator | A survey estimate is not an internal commercial forecast |

## Valid output in the absence of plant data

Publish a **clearly labeled benchmark** discussing observed shifts in aggregate shipments, orders, inventory, utilization, and prices, followed by decisions that depend on plant-level confirmation. Do not create fictitious production orders, inventory allocations, savings estimates, or contribution margins. If demonstration assumptions are specifically requested, isolate them in an explicitly modeled scenario without blending them into observed results.

## Automated checks and reviewer responsibilities

`audit_public_data.py` (manifest schema: `schemas/public-data-manifest.schema.json`; example: `examples/public-data-manifest.json`) can detect missing source citations, unqualified plant-level observed claims grounded solely in industry aggregates, and unsupported declarations of confidential datasets. It cannot verify each value against its original website; agent review must do that separately. Run the ordinary visual QA and answer-completeness checks afterwards.
