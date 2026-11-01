# Narrative and discussion design

## Communication contract

- `audience`: Intended readers, expertise, prior knowledge, and concerns.
- `intent`: `inform`, `align`, `decide`, or `explore`.
- `primary_question`: The main question the artifact must address.
- `takeaway`: The most important overall message.
- `medium`: Projection, handout, asynchronous reading, dashboard, or report.
- `output_language`: Explicit user choice, otherwise `ja`.
- `decision_owner`: Only when a decision is sought; leave unknown if not provided.
- `constraints`: Available time, decision authority, confidentiality, and accessible evidence.

## Four communication intents

### INFORM — understand the situation accurately

Suggested flow: takeaway → baseline/comparison → evidence → exceptions → next checks. Do not force a discussion prompt if none is needed.

### ALIGN — establish a shared understanding

Suggested flow: agreed facts → divergent interpretations → reasons for divergence → shared definitions → open issues. Represent the strongest counterargument fairly rather than creating a straw man.

### DECIDE — support a choice

Suggested flow: why a decision is needed → feasible options → evaluation criteria → comparative evidence → recommendation (possibly conditional) → decision request. Consider "do nothing", pilot, and full adoption only where genuinely feasible. Do not fabricate alternatives just to fill a matrix.

### EXPLORE — investigate uncertainty

Suggested flow: observed facts → unexplained behavior → competing hypotheses → discriminating data → next experiment or analysis. Frame unverified causes as hypotheses.

## Opening page policy

For ordinary multi-slide decks, **physical slide 1 is a normal, neutral cover** (report title, period, scope), while the evidence-backed argument begins on physical slide 2. Action headlines never apply to the default cover. See `cover-and-opening.md`. A user can explicitly request a message-first opening or no cover.

## Slide design unit

A slide has a `headline` (central claim), `support` (supporting evidence), `visual_focus` (first visual target), `qualifier` (uncertainty or exception), and `discussion` (a decision or question only if applicable). Translate these *values* into the selected output language while keeping the structural keys in English.

### Writing action headlines

The examples below are English explanations of the rule, **not** a request to generate English slide titles:

- **Weak:** "Inventory analysis", "Monthly trends", "Causes and actions".
- **Better:** "Total inventory fell by 10% while long-aging inventory increased by 30%."
- **Unsupported:** "Inventory reduction caused obsolete stock to increase."

For actual default Japanese wording, see the `headline` of slide `S01` in `examples/inventory-decision.json`.

Avoid mixing facts with recommendations. When causality is unverified, express the appropriate uncertainty rather than presenting a definitive causal explanation.

## Functional and reference slides: content-first title selection

Action headlines are reserved for substantive analysis and recommendations, **not** navigational or supporting pages. Pick concise Japanese titles by content rather than blindly applying the action-headline rule.

| Actual contents | Japanese page title | Recommended body structure |
| --- | --- | --- |
| Citations, source links, publication dates only | `出典` | Primary sources; source URLs and dates |
| Sources **and** metric definitions, scope, forecast flags, comparison conditions, or caveats | `出典・注記` | `出典`, `指標の定義`, `分析上の留意事項` as needed |
| Extended tables, detailed calculations, supporting analyses | `付録` | Descriptive subsection headings matching the details |
| Terminology definitions | `用語集` | Terms and short explanations |
| Analysis methods | `調査方法` | Methods and limitations |
| Agenda / navigation | `目次` | Agenda entries |

Use `role: reference` for citation/notes pages and `role: appendix` for backup analysis where appropriate. In the optional `reference_content_types` field of a reference slide, record `sources` and any applicable `definitions`, `scope`, `caveats`, `forecast`, `comparison`. If the only type is `sources`, label `出典`; if at least one other type is present, label `出典・注記`. These are Japanese defaults, and an explicit user language request takes priority. Do **not** remove content just to fit a shorter page title. A title is a navigation label, not a rhetorical claim. Do not duplicate the complete title as a body subsection.

## Conditions for a productive discussion prompt

- **Specificity:** What exactly needs to be assessed or decided?
- **Decision feasibility:** Can the participants decide, or at least delegate the next investigation?
- **Evidence:** Is there a basis for evaluating options?
- **Real alternatives:** Would choosing differently have meaningful consequences?
- **Fairness:** Are counterarguments and conditional assumptions acknowledged?

Weak question: "What do you think about this issue?"

More useful: "Should the aging-inventory ratio be added to monthly KPIs, or should we first investigate its drivers?"

For the equivalent Japanese decision question, see `slides[1].discussion.question` in `examples/inventory-decision.json`.

## Headline-only continuity test

Hide slide bodies and read **substantive** headlines in sequence (ignore reference, glossary, agenda, and appendix pages). Can the intended reader follow the context, key findings, evidence, and next decision? If the story contains ungrounded jumps or recommendations unsupported by evidence, revise it. Perform this check **in the output language**, not only on an internal English outline.

## Answer-first narrative and a decision-ready ending

Do not mistake a risk/indicator list for a synthesis. The first substantive slide should provide the best-supported current assessment and its key limitation. Subsequent pages should (a) support, (b) challenge, or (c) qualify that assessment. Before the functional sources/notes page, state the choice the audience actually faces, the best current working hypothesis, an alternative worth considering, trade-offs, and concrete reversal conditions.

Example in manufacturing: `Machining organic order +33%` is not synonymous with cutting-tool volume. `Cutting tools +19%` is a different scope: company management estimates ~5 percentage points underlying volume, ~2 prebuy and the rest predominantly price. Do not combine these into one invented causal bridge. Instead explain their separate business scope, evaluate why nominal growth cannot be annualized, and show a clearly labeled margin sensitivity rather than a made-up earnings forecast.
