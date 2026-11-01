# Semantic visual selection

`patterns/catalog.json` is the canonical list. Each pattern defines `intent`, `best_for`, `minimum_inputs`, `composition`, `must_show`, `avoid`, `alternatives` and a `discussion_hook`. `validate_brief.py` rejects a `pattern_id` that is not in the catalog.

## Selection procedure

1. Write the reader's **question**, not a chart name: "Which factor produced the increase?", "Why is cash lower than profit?", "Which option should we approve?"
2. Name the relationship: change drivers, part-to-whole, before/after, flow, distribution, uncertainty, competing explanations, decision.
3. Pick a catalog pattern whose `minimum_inputs` you actually have, and check that the numbers genuinely reconcile.
4. Prefer the pattern that makes the intended truth easiest to grasp: direct labels, a common baseline, one emphasis.
5. Record `visual.pattern_id` and Japanese `visual_focus` / `design_notes` in the brief. Write the most dangerous misreading in `visual.avoid`.
6. After rendering, check at full size and at 20–25% scale that the intended insight still dominates and every `must_show` item is visible.

## Pattern families

| Reader's question | Patterns |
| --- | --- |
| What changed and by how much? | `contrast_kpi`, `slope_before_after`, `trend_small_multiples`, `quarterly_divergence` |
| What drove the change? | `variance_waterfall`, `profit_driver_waterfall`, `contribution_plan_actual_bridge`, `regional_contribution`, `cash_flow_bridge` |
| How is the whole composed? | `composition_bar`, `mix_margin_gap`, `margin_dilution`, `segment_profit_divergence`, `profit_tier_divergence` |
| How do items rank or spread? | `ranked_comparison`, `distribution_range`, `queue_age_distribution` |
| How certain is it? | `uncertainty_band`, `evidence_ladder`, `hypothesis_evidence_matrix`, `outlook_fact_separation`, `guidance_revision`, `reported_vs_constant_currency`, `volume_sales_divergence` |
| How does work flow? | `process_linkage`, `process_capacity_queue`, `wip_stock_flow_bridge`, `timeline_milestones` |
| What should we decide? | `decision_option_matrix`, `service_feasibility_scenarios`, `cause_intervention_gate`, `conditional_bom_cases`, `inventory_demand_cover` |

## Guardrails that apply to every pattern

- A waterfall works only when categories are mutually exclusive and reconcile to the total, including a stated residual.
- Do not mix lease commitments with cash capex in one cash bridge; label them separately.
- An open-ended outlook such as ">50" is a threshold mark, not a point estimate.
- A chain from demand to margin to cash is a **monitoring model** unless each link is shown to be causal; label arrows accordingly.
- Segments under a new definition are not compared with old segments unless recast.
- When missing evidence is the real story, prefer an evidence ladder or decision matrix to a trend chart.
- Use literal `+` / `−` and arrows consistently; distinguish `%` from `pt` (`ポイント`).

## Typical transformations

| Weak original | Underlying defect | Better pattern |
| --- | --- | --- |
| Two KPI cards: total growth and one component's growth | The component's contribution to the total is hidden | `variance_waterfall` with signed, reconciled drivers |
| Operating cash flow, capex and FCF as unrelated bars | The subtraction that explains FCF is invisible | `cash_flow_bridge` on a shared scale |
| Actual capex and an "over 50" outlook drawn as two exact dots | An open-ended forecast looks precise | `uncertainty_band` with a threshold mark |
| Many KPI tiles ending in "continue to monitor" | Readers cannot tell what to decide | `decision_option_matrix` with criteria and a reversal condition |
| A list of claimed causes | Evidence mixed with hypotheses | `evidence_ladder` separating fact, inference and missing evidence |
| One BOM shortage figure when backlog treatment is unknown | A conditional answer looks definitive | `conditional_bom_cases` |
| "Excess inventory" with no agreed stock target | Judgement presented as fact | `inventory_demand_cover` |

## Typography and medium

Default audience language is Japanese: use a typeface with full Japanese glyph coverage, headlines that stay legible as thumbnails, and readable footnotes. Do not drop units or dates for visual simplicity. Projection, handout, document and dashboard media tolerate different densities.

A declared `pattern_id` is an intention, not proof that the rendered visual implements it. Verify on the rendered page (`visual-and-editorial-qa.md`).
