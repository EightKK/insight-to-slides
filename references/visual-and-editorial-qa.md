# Visual and editorial QA

No single check certifies an effective page. Run three verification classes and report them separately; none substitutes for another.

| Class | Who / what | What it can establish | What it cannot establish |
| --- | --- | --- | --- |
| Machine checks | `scripts/*.py` | Schema conformance, arithmetic, expected tokens in the PDF text layer, page bounds, overlap and font-size heuristics, narrow vector-direction checks | Factual truth of sources, chart meaning outside declared contracts, comprehension |
| Editorial review | The agent inspecting rendered pages | Whether each page says what its headline claims, hierarchy, pattern fit, caveats, language | A measured human response |
| Human test | Real readers from the intended audience | Timed two-second comprehension, decision usefulness | Anything, unless actually performed and logged |

An unperformed human test is reported as `NOT PERFORMED`. An unautomated semantic concept is `NOT AUTOMATED`, never `PASS`.

## Review loop

1. Freeze the inputs: source values, brief, semantic contract.
2. Render the editable file to PDF and PNG (`scripts/render_review.py`).
3. Run machine checks; fix factual and semantic failures before geometry.
4. Inspect **every** page at full size and on the contact sheet at roughly 20–25% scale.
5. Log each issue (schema below). Revise the brief first when the problem is semantic, then re-render.
6. Re-run all checks; close an issue only when the new render was actually inspected and shows the fix.

At Light tier (see SKILL.md), steps 3 and 6 may be limited to `review_deck.py` and `audience_purity.py`, but step 4 is never skipped.

## Per-page inspection

- **Glance:** at thumbnail size, which value or phrase draws attention first? Does it match the headline? Would a two-second reader repeat something stronger than the evidence supports?
- **Integrity:** fact, inference, hypothesis and recommendation are distinguishable; denominators, signs, forecasts and non-comparable scopes are visible.
- **Fit:** the declared `pattern_id` is actually implemented; the pattern's `must_show` items are visible; its `avoid` list is not violated.
- **Hierarchy:** one dominant headline and one dominant visual; main figures legible at projection size.
- **Counter-case:** decision pages show a credible alternative explanation or option.
- **Language:** all audience-visible text in the output language; no leftover template strings.
- **Notes and appendix:** speaker notes, headers, footers and appendix pages inspected too (PDF does not preserve notes; check the PPTX).

## High-impact visual defects to look for

- Headline and the main marks describe different facts.
- A negative value drawn in the positive direction, or an arrow contradicting its label.
- Labels overlapping values or category names.
- Company forecast and analyst-derived figures styled identically.
- Reported growth compared with constant-currency growth without a scope note.
- Regional or driver contributions showing only positives, with negatives hidden in an unlabelled "other".
- A hypothesis presented as an established conclusion.

## Hard gates (any failure blocks delivery)

- **G1 Evidence:** a material claim or value has no traceable source, or fictional values appear as fact.
- **G2 Encoding:** misleading axes, scales, periods, signs or comparison scopes.
- **G3 Reconciliation:** claims do not reconcile with the underlying data.
- **G4 Rendering:** text or graphics missing, overlapping or too small to read.
- **G5 Invented urgency:** an informational piece manufactures conflict, urgency or alternatives.
- **G6 Language:** output contradicts the explicit language choice, or is materially in English under the Japanese default.
- **G7 Answer completeness:** the governing question has no calibrated current answer (`answered`, `conditional` or `unanswerable` with stated limits).
- **G8 Causal integrity:** management explanations, residuals or associations presented as independently verified causes.
- **G9 Discussion readiness:** a decision piece lacks a ranked current view, a credible alternative with trade-offs, and an observable reversal condition.

## Optional heuristic rubric

Use only when the scoring method and reviewer are stated. It is a discussion aid, not a validated measure.

| Criterion | Points |
| --- | ---: |
| Purpose fit | 15 |
| Claim clarity (headlines alone carry the story) | 20 |
| Evidentiary validity | 20 |
| Visual design | 20 |
| Discussion value | 15 |
| Accessibility, export quality, editability, language | 10 |

## Issue log format (production package only)

```json
{
  "review_method": "Agent inspection of rendered PNGs",
  "human_two_second_test": "NOT PERFORMED",
  "issues": [
    {
      "slide": "S05",
      "severity": "high",
      "observation": "Reported-rate label overlaps the constant-currency bar",
      "proposed_fix": "Move the reported-rate annotation outside the plot area",
      "before_evidence": "qa/draft/page-05.png",
      "status": "verified_fixed",
      "verified_after": "qa/final/page-05.png"
    }
  ]
}
```

`status` is one of `open`, `fixed_pending_verification`, `verified_fixed`, `accepted_limitation`. Never mark `verified_fixed` without inspecting the cited after-image.

The issue log, check outputs and render images belong to the production package, never the reader-facing artifact (`audience-content-boundary.md`). The summary of QA findings given to the user is written in the output language.
