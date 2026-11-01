# Rendering adapters

This skill designs and verifies meaning. It does not draw slides itself. `communication-brief.json` is the source of truth; a rendering backend turns it into the deliverable.

## Choosing the renderer

Use what the host environment offers, in this order:

1. **The host's native output for the requested medium.** If the environment provides a slide-deck, document or dashboard artifact type, or a dedicated skill for PPTX/DOCX/XLSX, use it and follow its own instructions for layout and export. Map brief fields onto its content model (headline → slide title, `visual` → chart or diagram, `qualifier` → footnote, `discussion` → closing question).
2. **A file-format skill** (for example a PPTX skill) when the user asked for that file format.
3. **Direct generation** with python-pptx, PptxGenJS, HTML or similar, when neither of the above exists.

Never claim a format the available renderer cannot produce. Verify the renderer's actual capabilities (editable charts, Japanese fonts, notes, PDF export) before promising them.

## Contract with any renderer

**Input**
- `communication-brief.json` with `document.output_language` (default `ja`).
- Every substantive slide carries `visual.pattern_id`, `evidence_refs`, headline, `audit_tokens`, and Japanese `visual_focus` / `design_notes`.

**Output**
- The deliverable with all reader-visible text in the output language.
- A render of each page (PDF or PNG) for inspection.
- `pages_manifest.json` mapping `slide_id` → physical page number, expected visible tokens and `pattern_id`. The cover is page 1 in a conventional deck, so substantive slide `S01` is usually page 2.

**When no PDF/PNG render is obtainable** (for example a hosted artifact without export access), run the checks that do not need one (`validate_brief.py`, `audit_calculations.py`, `evaluate_decision_quality.py`, `lint_japanese_style.py` on the text), inspect the artifact visually by whatever means exist, and report the render-dependent checks as `NOT AUTOMATED`.

## Medium-specific guidance

- **PPTX:** prefer editable text, shapes and native charts. Localise headings, shapes, charts, tables and speaker notes. Use a font with full Japanese glyph coverage and check line breaking.
- **Document/report:** logical sections take priority over one-claim-per-page. Keep evidence readable; the same claim, evidence and caveat discipline applies.
- **HTML/PDF:** preserve claims and evidence; add interaction only when it helps. Do not let a library's English defaults leak into labels.
- **Dashboard:** show filter effects on populations, series definitions and drill-down paths. Localise titles, legends and tooltips.

## Reviewing an existing deck or report

When the user supplies an artifact to critique or rework:

1. Extract the primary message of each page or section.
2. Classify facts, hypotheses and recommendations; find text–chart inconsistencies.
3. Evaluate in priority order: factual errors and unsupported inference → narrative and discussion structure → layout and readability.
4. For each page give `current`, `problem`, `rewrite`, `visual_change`, `discussion_change`, `evidence_gap`.
5. Output language follows `language-policy.md`: the user's explicit choice, otherwise Japanese. The source file's language does not override the default unless the user asks to preserve it.
6. If a revised file is requested and a renderer is available, regenerate from a corrected brief and run the QA loop.

## Requirements for a reproducible pipeline

- Rebuild the deliverable from the brief; push corrections upstream into the brief rather than patching the output.
- Keep the generation script and brief in the production package.
- `render_review.py` measures geometry and text-layer heuristics only. A PDF does not preserve speaker notes, animation or reading order; check those in the original file.
