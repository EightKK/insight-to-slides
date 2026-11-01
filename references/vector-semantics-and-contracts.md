# Vector semantics and claim contracts

This reference provides a **limited, repeatable semantic contract**, not a general-purpose visual-understanding engine.

## Why this matters

A PDF can be free from clipping and still be misleading. Common examples include a negative change drawn to the right of a zero axis, unrelated segment amounts visually presented as additive, a forecast labeled as an actual result, or a waterfall that does not reconcile. The tool checks these risks where the producer supplied explicit testable contracts.

## Minimal workflow

1. Preserve original numeric source fields, units, periods, and cited source sections.
2. Compute arithmetic independently using `scripts/audit_calculations.py`.
3. Author `semantic-contract.json` from the claim and source fields, **before** looking at the rendered result. Declare a numeric direction, reconciliation, page-level caveat, forecast qualifier, or signed-vector bar as applicable.
4. Export the editable presentation to PDF using `scripts/render_review.py`.
5. Execute `scripts/semantic_qa.py source-values.json semantic-contract.json render.pdf --out semantic-review.json` and `scripts/review_deck.py`.
6. Inspect all full-size images in the generated deck. Record findings and changes. Export and rerun checks after each edit.

## Supported checks

| Type | Input | What it verifies | Limit |
|---|---|---|---|
| `numeric_direction` | Previous and current numeric field paths | Up/down/flat source delta | Does not inspect the chart |
| `reconcile` | Two totals and additive signed components | Factor waterfall sums to change | Depends on correct source classification |
| `margin_points` | Revenue/profit by period | Percentage-point bridge arithmetic | Numeric only |
| `required_text` | Required tokens and page | PDF contains the designated labels | Text presence is not comprehension |
| `scope_caveat` | Caution tokens and page | Essential comparability note survives rendering | Cannot judge strength of language |
| `forecast_label` | Forecast tokens and page | Outlook explicitly designated | Does not verify forecasting quality |
| `signed_vector_bar` | Numeric delta, fill color, axis x, y-band and page | Colored PDF vector rectangle is physically on the correct side of the axis | Requires vector PDF and deliberately narrow geometry configuration |

For `signed_vector_bar`, `axis_x_fraction` is the fraction of the PDF page width, `y_fraction_range` is the accepted vertical band in page-height fractions, and `rgb` is the expected three-integer color. Use the PDF rendered from the actual PPTX—not an SVG mock. The renderer also detects text touching a filled, saturated PDF vector shape with a near-identical ink color; this is a narrowly scoped low-contrast warning rather than a full contrast audit. The shape detector is a conservative heuristic; fail the check if no matching vector rectangle exists. Require manual image inspection for all charts that are rasterized or outside the supported geometry.

## Honest completion criteria

- Report arithmetic, PDF text, vector directions, editorial review, and human timed comprehension as **distinct** statuses.
- An unautomated semantic concept is `NOT AUTOMATED`, not `PASS`.
- There is no general AI model call in `semantic_qa.py`. The AI agent performs the image critique using the rendered pages it receives; the helper script only verifies explicit invariants.
- A 2-second human understanding test is not performed unless real participants were exposed to timed slides and their responses logged.

## Toyota example

`examples/toyota-source-values.json`, `examples/toyota-semantic-contract.json`, and `examples/toyota-fy2027-q1.json` show an automotive manufacturer case. The source is Toyota's FY2027 Q1 financial summary filed with the US SEC (August 4, 2026).
