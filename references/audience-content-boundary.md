# Audience Content Boundary: Final Deliverables vs. Production Records

## Core rule

The final presentation or report must stand on its own. It must communicate what the target audience **needs to know, understand, discuss or decide**, not describe the process used by the assistant to assemble the artifact. Do not assume the reader has seen a previous draft, chat, slide deck, assessment, or skill version.

### Final artifact: include

- A primary argument and a decision-relevant sequence of supportable conclusions.
- Material facts, comparative data, business implications, and warranted uncertainty.
- The necessary scope, units, source citations, definitions, limitations, and conditions to interpret claims responsibly.
- The audience's decisions and monitoring indicators, when relevant to the user's purpose.
- Concise housekeeping pages with functional titles such as `出典・注記`.

### Final artifact: exclude unless explicitly requested by the audience

- Previous-version comparisons, before/after slides, and what was improved or changed in the author's workflow.
- Skill/plugin/model labels and version numbers, agent performance reports, QA outcomes, regression results, test totals, issue logs, and human comprehension test status.
- Research plans, retrieval steps, evidence-gap counts, checklists, tool descriptions, and any narrative about how the assistant investigated or designed the slides.
- Slides defending the work of creating the presentation instead of supporting the business claim.

## Important distinction

Uncertainty **about the business conclusion** belongs in the audience-facing artifact. An unexplained profit bridge, incomplete tariff disclosure, or unknown market assumptions may change the conclusion, so explain them in the language of the decision being made. Uncertainty **about the assistant's process** (which searches were tried, which tests passed) belongs in separate working records.

For instance:

| Not suitable in an ordinary earnings deck | Suitable in an earnings deck |
| --- | --- |
| "We searched nine evidence gaps and resolved five" | "The disclosed figures do not isolate the tariff and model-mix effects" |
| "Research improved explainability compared with the prior version" | "Operating margin fell despite revenue growth" |
| "Our QA caught overlapping labels" | Fix the labels; do not mention the QA |
| "Our skill verified three hypotheses" | "Non-operating gains contributed materially to net income growth" |

## Mandatory two-channel deliverable design

1. **Audience channel**: the publishable Japanese PPTX/PDF/document. Only reader-relevant conclusions, support, implications, and necessary qualifications. This is the primary output.
2. **Production channel**: research plans, evidence ledgers, draft comparisons, test outcomes, generated images, source code, and analytical logs. Keep it in a separate artifact or workspace folder and do not merge into the audience artifact. Supply it when reproducibility, audit or development is needed, and do not announce it inside the published deck.

## Pre-release checklist

- Can a reader who has not seen any earlier chat or draft understand every page?
- Does each substantive page answer a question the target audience cares about?
- Is any page primarily explaining the assistant's process instead of the subject matter?
- Are prior deck comparisons, internal QA metrics and version labels absent?
- Are critical source notes and legitimate substantive uncertainties retained?
- Did the exported PDF pass `scripts/audience_purity.py`? All flagged items must be reviewed; no direct skill/process disclosure is allowed without explicit scope.

When the user explicitly requests a methodology report or a presentation about the skill itself, these exclusions may be overridden to match the actual audience intent. The exception must be explicit and scoped; do not assume that internal QA is interesting to viewers just because it was done.
