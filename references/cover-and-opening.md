# Cover and opening-slide design

## Why covers are exempt

A cover identifies what the document is and how to situate it. It is not an argument or data visualization. Action headlines belong to the substantive narrative starting on physical slide 2. A conventional first slide allows the viewer to orient without prematurely interpreting data.

## Default opening sequence

1. **Physical slide 1 — cover:** neutral document title, reporting period, and important scope. Optionally verified presenter, organization, publication/source date, and confidentiality classification. Keep the layout quiet, concise, and readable; a cover does not need a key insight, a question, charts, progress claims, or decorative statistics.
2. **Physical slide 2 — first substantive message:** one evidence-backed claim in a clear headline, an immediately understandable visual, and any caveat necessary to prevent a misleading interpretation. Depending on the use case, this may be an executive summary, opening finding, or conditional recommendation.
3. **Physical slides 3+ — argument:** subsequent evidence, alternatives, business implications and discussion questions as appropriate.

## Examples (English instructions; Japanese audience output)

| Page | Good Japanese headline | Why |
| --- | --- | --- |
| Cover | `カナダ製造業 月次運営レビュー` | Neutral document identity |
| Cover subtitle | `2026年8月実績` | Period, not a conclusion |
| Slide 2 | `8月の出荷額は1.5%増。価格調整後は横ばい` | Evidence-backed central finding, stated plainly |
| **Invalid cover** | `売上は増えた。実質出荷は伸びていない。` | Message should start on slide 2 |

## Cover content rules

- Do not confuse a normal title page with a marketing teaser. Avoid action/implication wording such as "should", "must", "declined despite", or "the cause is" on a neutral cover. These examples are indicative rather than a comprehensive language blacklist.
- Avoid duplicating the entire executive summary in small print on the cover. Do not put the research/QA process on the cover.
- If the underlying source is an industry aggregate rather than a single factory, state the scope accurately on the cover.
- The opening slide is not required to contain an action headline; do not flag a short cover title as weak.
- Allow an explicit user request for a message-first cover, no cover, or one-page visual to override this default.

## Quality gates

- `cover.title` is neutral and matches the reader's expectation; `document.cover` should carry only identity metadata.
- In the rendered PDF/PPTX, the first slide contains the correct title, scope and period, and **no takeaway headline**.
- The second slide is the first substantive page and communicates a defensible central claim.
- Slide order and numbering are synchronized when inserting an opening cover.
- Final delivery metadata and references stay out of the cover unless they identify the report.

