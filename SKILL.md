---
name: insight-to-slides
description: Design and verify evidence-grounded Japanese business slides and reports that lead to a decision — 資料作成, プレゼン資料, 報告書, 決算分析資料, 月次会議資料, 経営会議・工場会議の資料, 既存資料のレビューや作り直し. Covers argument structure, source and numeric checks, chart selection, natural Japanese wording and rendered-page QA. Pairs with whatever renderer draws the file. Not for casual one-off visuals or non-business creative decks.
---

# Insight to Slides

Turn sources and data into a Japanese business deck or report whose main claim a reader can grasp at a glance, whose visuals mean what they say, and whose ending supports a real decision.

This skill designs meaning and verifies quality. It does **not** draw slides: hand the structured brief to the renderer the environment provides (`references/rendering-adapters.md`).

## Always-on rules

These apply to every task, at every tier.

1. **Output language.** Reader-facing text (slides, charts, labels, notes, reports, the QA summary given to the user) is Japanese unless the user explicitly asks for another language. Source language and these English instructions do not change that. Record it as `document.output_language`. → `references/language-policy.md`
2. **Reader channel vs production channel.** The deliverable contains only what the audience needs: findings, evidence, implications, decision-relevant uncertainty. Research plans, audit outputs, QA logs, draft comparisons, tool or skill names stay in a separate production package. Uncertainty about the *business* belongs in the deck; uncertainty about *your process* does not. → `references/audience-content-boundary.md`
3. **Evidence honesty.** Every material claim traces to a source or the user's data. Keep facts, derived arithmetic, interpretation, hypotheses, recommendations and forecasts distinct. Never invent figures, owners, thresholds, deadlines or probabilities. Never present a forecast as an actual, or synthetic data as real.
4. **Numeric integrity.** Recompute key percentages, point differences, shares and reconciliations. Keep original units, scopes and periods. `%` and `pt` are different.
5. **Cover and opening.** A multi-slide deck starts with a neutral cover (title, period, scope; no claim). The first substantive message is on physical slide 2. Housekeeping pages get short functional titles (`出典`, `出典・注記`, `付録`, `目次`, `用語集`). The user can override. → `references/cover-and-opening.md`
6. **Natural Japanese that preserves meaning.** Read `references/japanese-editorial-style.md` before drafting copy, not only at the end. State the finding instead of announcing its importance; never smooth away numbers, qualifiers, scope or uncertainty.
7. **Honest verification.** Machine checks, your own inspection of rendered pages, and human testing are separate. Never claim a two-second comprehension result unless real readers were timed. Report what you did not check as `NOT PERFORMED` or `NOT AUTOMATED`.

## Step 0 — Choose mode and tier

**Mode** decides whether you retrieve evidence. An explicit user constraint on browsing always wins.

| Mode | When | External retrieval |
| --- | --- | --- |
| `presentation` | Restyle, restructure or convert supplied material | None |
| `analysis` | Assess data or documents the user supplied | None by default |
| `research` | Company, market, competitor, technology or strategy question without a no-browsing constraint | Yes, bounded |

**Tier** decides how much process to run. Pick the lowest tier that fits, state it to the user in one line, and move up if the stakes or the data turn out larger.

| Tier | Typical request | Production artifacts | Gates |
| --- | --- | --- | --- |
| **Light** | Polish or convert existing content; short informational deck; no new analysis | Headline outline, `communication-brief.json`, `pages_manifest.json` | `validate_brief`, `lint_japanese_style`, render + `review_deck`, `audience_purity`, inspect every page |
| **Standard** | Analysis of supplied data; any deck that asks the reader to decide | Light + `argumentation-contract.json`, `source-values.json`, `calculations.json`, `semantic-contract.json` | Light + `evaluate_decision_quality`, `audit_calculations`, `semantic_qa` |
| **Full** | `research` mode; board-level, external, or money-committing decisions | Standard + `research-plan.json`, `evidence-ledger.json`, `analysis-brief.json`, issue log | Standard + `research_gate`; consider an independent reviewer who has not seen the drafting |

**Domain audits run whenever their data is present, at any tier:**

| Data | Read | Run |
| --- | --- | --- |
| Multi-ledger plant data (sales plan/actual/forecast, production, inventory, customer-SKU cost, BOM, supply) | `references/factory-monthly-review.md` | `audit_factory_monthly.py`, `audit_factory_decision_readiness.py` |
| Flow line / WIP reduction case | `references/operational-improvement-case.md` | `audit_operational_case.py` |
| Public or industry-aggregate statistics used for an operations briefing | `references/public-operational-data-boundary.md` | `audit_public_data.py` |

## Workflow

### 1. Communication contract

Fix audience, medium (`projection`, `handout`, `async`, `dashboard`, `document`), intent (`inform`, `align`, `decide`, `explore`), governing question, decision owner (only if known) and output language. Ask only for essentials that change the output; otherwise state your assumption and continue. → `references/narrative-and-discussion.md`

### 2. Evidence

For each source capture title, date, page or section, fact vs forecast, original figure, unit, comparison period and definition. In `research` mode follow the bounded loop in `references/research-orchestration.md`: hypotheses including the null, ranked gaps with a falsification question, batch retrieval from primary sources, an explicit stopping point. Domain traps: `references/manufacturing-financial-analysis.md`, `references/capital-equipment-case.md`, `references/analytical-reasoning.md`.

### 3. Insight

Explore divergences, drivers, concentration, bottlenecks and competing explanations. Rank by consequence for the audience, not novelty. Mark unproven causes as hypotheses and list what would refute each. → `references/insight-methods.md`

### 4. Argument, then headlines

(Standard and Full) Write `argumentation-contract.json`: governing question, current answer with confidence, claims linked to evidence, competing hypotheses with falsifiers, and — for decisions — at least two real options with trade-offs and a reversal condition. Validate it. → `references/answer-completeness-and-decision-quality.md`

Then write **all substantive headlines in sequence before any layout**. Read them alone: they must tell the story. Merge repeats; move peripheral detail to an appendix.

### 5. Visual pattern per page

Choose from `patterns/catalog.json` by the reader's question. Confirm `minimum_inputs`, plan every `must_show`, and note the main misreading in `visual.avoid`. → `references/visual-patterns.md`

### 6. Brief and render

Write `communication-brief.json` (`schemas/communication-brief.schema.json`): every substantive slide has a headline, `evidence_refs`, `visual.pattern_id` and at least one `audit_token` (a fact that must appear on the rendered page). Render through the environment's renderer, export PDF/PNG, and write `pages_manifest.json` mapping slide IDs to physical pages.

### 7. Verify, fix, re-render

Run the gates for your tier on the **final exported file**, then inspect every page at full size and as a thumbnail. Fix meaning before geometry; revise the brief, re-render, re-run. Close an issue only after seeing the fixed render. → `references/visual-and-editorial-qa.md`, `references/vector-semantics-and-contracts.md`

### 8. Deliver

- **Reader channel:** the deck or report (editable file plus PDF where the renderer supports it).
- **Production package:** brief, contracts, source values, audit outputs, renders, issue log. Offer it; do not merge it into the deck.
- **Message to the user (in the output language):** what was produced, remaining evidence gaps that matter to the decision, and which checks were run, not automated, or not performed.

## Scripts

Run from the skill directory; adjust paths to your working files. Dependencies are in `requirements.txt`; rendering PPTX input also needs LibreOffice.

Exit codes are shared by all gates: **0 = PASS / READY**, **1 = FAIL or invalid input**, **2 = HOLD / review required**. Treat 2 as "do not publish as a definitive decision until resolved", not as an error to suppress.

| Script | Usage | Tier | What it checks |
| --- | --- | --- | --- |
| `validate_brief.py` | `brief.json` | All | JSON Schema, then semantic rules: pattern IDs in the catalog, evidence references, `audit_tokens`, cover and functional titles |
| `lint_japanese_style.py` | `draft.md\|.txt\|.pptx [--json] [--fail-on-high]` | All | Formulaic Japanese patterns across the whole deck (heuristic warnings) |
| `render_review.py` | `deck.pptx\|deck.pdf --out DIR [--dpi 150]` | All | Renders PDF/PNG and a contact sheet; clipping, overlap, small text, low contrast. Not a gate by itself |
| `review_deck.py` | `deck.pdf pages_manifest.json --out report.json` | All | Headlines and expected tokens on the right pages (sign-explicit: `12%` ≠ `▲12%`); missing token = error |
| `make_review_packet.py` | `pages_manifest.json --qa DIR --pdf deck.pdf --out packet.md` | All | Assembles a page-by-page packet for your visual inspection |
| `audience_purity.py` | `final.pdf\|.md\|.txt [--out F]` | All | Process, QA, tool or skill wording leaking into the deliverable (returns 2 for review) |
| `evaluate_decision_quality.py` | `argumentation-contract.json [--out F]` | Standard+ | Governing question answered, claims traced, hypotheses with falsifiers, real options with trade-offs and reversal conditions; rejects placeholders and duplicates |
| `audit_calculations.py` | `source-values.json calculations.json [--out F]` | Standard+ | Recomputes declared formulas from source values (numeric inputs only) |
| `semantic_qa.py` | `source-values.json semantic-contract.json deck.pdf --out F` | Standard+ | Directions, reconciliations, margin points, required caveats and forecast labels, signed vector bars on the rendered PDF |
| `research_gate.py` | `research-plan.json evidence-ledger.json [--analysis analysis-brief.json] [--allow-open-gaps] [--out F]` | Full | Gap coverage, claim support, source dates; `pending` gap with impact ≥ 4 → HOLD |
| `audit_factory_monthly.py` | `DATA_DIR [--period YYYY-MM] [--out F]` | Domain | Ledger reconciliation across sales, production, inventory, contribution and BOM; material shortages reported |
| `audit_factory_decision_readiness.py` | `DATA_DIR [--period YYYY-MM] [--backlog included\|additional\|unknown] [--eligible-stock-confirmed] [--supply-eta-confirmed] [--capacity-confirmed] [--inventory-policy-confirmed] [--out F]` | Domain | Conditional BOM cases, two-period inventory cover, contribution gap; HOLD while any shortage or unconfirmed condition remains |
| `audit_operational_case.py` | `case.json [--out F]` | Domain | WIP conservation, capacity, service gaps, scenario arithmetic, benefit-basis note |
| `audit_public_data.py` | `manifest.json [--out F]` | Domain | Observation level and provenance of public-data claims |

Every script checks structure and arithmetic only. A passing result does not prove that sources are true, that a cause is real, or that readers will understand.

## Reference map

| When | Read |
| --- | --- |
| Before drafting any Japanese copy | `japanese-editorial-style.md` |
| Building the storyline, discussion prompts, functional page titles | `narrative-and-discussion.md`, `cover-and-opening.md` |
| Deciding what stays out of the deck | `audience-content-boundary.md` |
| Governing question, causal labels, decision ending | `answer-completeness-and-decision-quality.md` |
| `research` mode | `research-orchestration.md`, `analytical-reasoning.md` |
| Earnings or financial analysis of a manufacturer | `manufacturing-financial-analysis.md` |
| Long-lead-time equipment makers (orders vs sales vs cash) | `capital-equipment-case.md` |
| Plant monthly review from internal ledgers | `factory-monthly-review.md` |
| WIP, bottleneck, release-control decisions | `operational-improvement-case.md` |
| Public statistics instead of plant data | `public-operational-data-boundary.md` |
| Choosing charts | `visual-patterns.md` |
| Rendered-page review, hard gates, issue log | `visual-and-editorial-qa.md` |
| Semantic contracts and vector-direction checks | `vector-semantics-and-contracts.md` |
| Which renderer, reviewing an existing deck | `rendering-adapters.md` |
| Output language edge cases | `language-policy.md` |

## Examples to copy from

When writing a production file for the first time, open the matching example and follow its shape. Fictional examples are safe to imitate freely. The Toyota files are the only real-company case: they show how real disclosures are recorded, but their figures are from a past period and must never be quoted as current.

| When you write | Look at |
| --- | --- |
| `communication-brief.json` (cover, slides, functional titles, audit tokens) | `examples/inventory-decision.json`; real-data version `examples/toyota-fy2027-q1.json` |
| `argumentation-contract.json` | `examples/factory-monthly-synthetic/contracts/argumentation-contract.json` |
| `source-values.json` and `semantic-contract.json` | `examples/toyota-source-values.json`, `examples/toyota-semantic-contract.json` |
| `research-plan.json`, `evidence-ledger.json`, `analysis-brief.json` | `examples/toyota-deep-research/` |
| Factory CSV bundle and integrated contract | `examples/factory-monthly-synthetic/data/`, `.../contracts/integrated-monthly-contract.json` |
| Operational WIP case | `examples/fictional-mixed-model-wip.json` |
| Public-data manifest | `examples/public-data-manifest.json` |

`tests/fixtures/` holds regression data for the test suite only; do not use it as a template.
