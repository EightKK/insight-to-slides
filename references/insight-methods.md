# Insight mining: discovery and evidence checks

## Candidate insight patterns (separate observations from conclusions)

| Pattern | What to look for | Verification warning |
|---|---|---|
| Contrast | One KPI improves while another deteriorates; aggregate improves while a subgroup worsens | Align units, scope, and time period |
| Gap | Actual vs. target; observed vs. expected | Check whether the target itself is meaningful |
| Composition shift | Changes in percentages and mix | Distinguish share increases caused by a shrinking denominator from absolute increases |
| Change point | Departures from the previous trend | Examine seasonality, sample sizes, and measurement changes |
| Concentration | Outcomes concentrated in a few categories | Check truncation and missing data |
| Causal hypothesis | Possible explanations for linked observations | Correlation does not establish causation |
| Trade-off | Quality vs. cost, speed vs. risk, etc. | Verify that choices are real and feasible |
| Uncertainty | Findings sensitive to assumptions or missing data | Communicate unknowns as unknowns |

## Verification procedure

1. Confirm provenance and scope; record whether the original data is accessible.
2. Check each measure's definition, units, denominator, period, population, missing-value treatment, and deduplication rules.
3. For before/after comparisons, calculate absolute and relative changes, distinguishing percentages from percentage points.
4. Consider at least one plausible alternative explanation for significant candidates when meaningful; do not manufacture alternatives.
5. Distinguish **fact**, **implication**, **hypothesis**, and **recommendation**. If the evidence is inadequate, label a proposal as an option for investigation instead of a confirmed recommendation.
6. Discard an insight that has no consequential relevance for the audience, however surprising it might be.
7. Write the selected insight and its audience-facing caveats in `document.output_language` (Japanese by default), regardless of source language.

## Qualitative prioritization

- **Relevance:** Whose decision or problem does this affect?
- **Evidence:** Can the observation be verified using sources or data?
- **Consequence:** Would action or inaction result in a meaningful difference?
- **Actionability:** Could it lead to a sound decision or investigation?
- **Novelty:** Does it add more than a restatement of already-known information?

This is a heuristic order, not a mathematically validated score. Do not favor novelty alone.

## Typical narrative errors

- "Revenue increased while margin fell" becomes "Discounting caused the margin decline" without causal evidence.
- "The share of aging inventory rose" becomes "The value of aging inventory rose" without checking the denominator.
- A small proportional difference is exaggerated with a bar chart that omits a zero baseline.
- Ordinary seasonality is framed as a crisis without relevant context.
