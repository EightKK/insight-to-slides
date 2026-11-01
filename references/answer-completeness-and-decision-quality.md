# Answer Completeness, Causal Integrity and Discussion Readiness

## Principle
The final presentation is an argument addressed to its reader, not a tour of the research process. A reader should be able to articulate: **What is the present assessment, why, what alternative might be true, and what would change the assessment?** The second-to-last substantive page should normally synthesize the argument; the last substantive page should help the reader decide, not merely watch a KPI list.

## A. Answer completeness
1. Name a **governing question** the audience cares about. It must be both answerable to some degree and nontrivial (e.g., "Is this industrial company's margin uplift repeatable?").
2. Write a short, calibrated **current answer** BEFORE designing visuals. The answer must contain a stance, the strongest supporting evidence, and one material uncertainty. "We need further research" is not a stance unless the sources really prevent even a conditional judgment.
3. Track every substantial secondary question: answered, conditionally answered, or genuinely unknown. A conditional answer needs both a current best-supported assessment and the particular missing disclosure that could reverse it.
4. Reject content which neither proves/disproves the stance nor changes its implications. Move peripheral market trivia and methodology to backup material.
5. Explicitly distinguish information which is missing from information that is merely unimportant. Stop research when the next obtainable evidence is unlikely to affect the audience's conclusion.

## B. Causal integrity
- Classify each claim `fact`, `interpretation`, `hypothesis`, or `recommendation`. Link it to source/evidence IDs.
- Distinguish `(1)` company statements/management estimates, `(2)` independently verified calculations, `(3)` explanatory hypotheses, and `(4)` associations. An executive explanation is evidence of what management believes; it is not necessarily independent proof of causation.
- Price/volume/mix bridges must use the same denominator, period, business scope and measurement basis. Management approximations require `≈` and explicit scope labels. Do not infer segment profit from percentages of a different segment.
- Avoid precise causal bridges from a mixture of revenue, orders, and margin effects. If a line item is a residual, call it **residual/primarily price**, not exactly measured price.
- The causal review should be a human examination of each headline, chart label, adjacent annotation and final interpretation, not solely a word-based lint.

## C. Discussion readiness
- A meaningful decision has genuine alternatives with trade-offs, not "monitor versus do nothing".
- Provide an **evidence-ranked working assessment**, plus at least one credible alternative hypothesis whose presence would change the decision.
- For each hypothesis: supportive facts, counter-evidence, falsifier and confidence calibration. `undetermined` is legitimate; numerical probabilities must never be invented.
- Show a **reversal trigger**: an observable metric or event and what each possible result means. Never invent a firm threshold based on data which cannot justify one; an illustrative sensitivity must be labeled as a sensitivity, not a prediction.
- A decision question may be investor, manager, customer or engineering oriented. Avoid forcing an investment BUY/SELL recommendation when not asked.

## D. Separate validation classes
- `evaluate_decision_quality.py` checks the structure: evidence IDs, central question, claim traceability, missing alternative cases, options/trade-offs and reversal conditions. It cannot reason about numerical truth.
- Editorial review checks whether claims actually follow from cited sources, every diagram says what the text claims, and the reader can make a defensible provisional assessment.
- Actual two-second audience testing is separate and is never implied by machine checks.

## E. Final editorial release questions
- Could someone see this deck for the first time and grasp its main judgment?
- Are important figures accurately scoped (orders vs sales, adjusted vs reported earnings, quarter vs year-to-date)?
- Does each key claim have evidence and an alternative explanation?
- Is the current preferred hypothesis stated explicitly, with confidence calibrated?
- Does the last substantive slide give the audience a choice and a reason to debate it?
- Is there any unnecessary assistant-process, version-change, or research-log content? Delete it from the reader-facing version.
