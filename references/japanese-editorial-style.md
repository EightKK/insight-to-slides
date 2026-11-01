# Japanese editorial style for audience-facing slides and reports

## Purpose and precedence

Author all skill instructions in English while delivering Japanese audience copy by default. This is an editorial quality gate, **not** a content-research or fact-checking substitute. Evidence and uncertainty are authoritative: never alter numbers, units, denominators, periods, qualifiers, claims, source links, or confidence to create smoother sentences.

Apply the principles to titles, slide body, graphs, labels, captions, speaker notes, summary paragraphs and executive reports. A slide title may be a conclusion when it genuinely helps a reader; a neutral cover, references, glossary and appendix are intentionally exempt.

## Rules at drafting time

1. **Say the finding, not its importance.** Start with a concrete subject and a defensible assertion. Suppress empty set-ups such as `重要なのは`, `注目すべきは`, `本質的な課題`, and `改めて問われる` when the actual fact can be stated instead.
2. **One slide, one point, not one slogan.** A good headline names the subject, period or comparison where ambiguity matters. Avoid generic, overdramatic, slogan-like headlines. Don't mandate action-style titles on cover, sources and housekeeping pages.
3. **Keep the register of a Japanese business meeting.** Write measured business Japanese, not translated English, a startup ad, an opinion column or chat assistant commentary. Unnecessary metaphors, performative contrasts, exaggerated claims and artificial rhetorical questions weaken credibility.
4. **Reduce redundant signposting.** Avoid repeatedly saying `ここから分かるのは`, `この結果が示すのは`, `単なるAではなくB`, `AからBへ`, and `今後も注視が必要`. State the actual finding, a specific implication, or the decision condition.
5. **Use everyday business verbs when exact.** `増えた`, `下がった`, `不足する`, `見込む`, `確認する`, and `決める` can be clearer than `可視化する`, `収斂する`, `浮き彫りにする` or abstract nouns. Retain technical nomenclature when meaningful (`在庫評価額`, `限界利益`, `有機成長`, `BOM`), and explain unfamiliar terms at first use when needed.
6. **Vary only when meaningful.** Mix shorter and longer lines according to information density; don't manufacture unevenness for its own sake. A recurring KPI table can have uniform labels; repetitive intro and closing sentences across every slide are the problem.
7. **Be precise about agency.** A chart can `示す` a value, but `市場が判断する` or `数字が問いかける` may imply an agent that isn't there. Prefer the actor or the observed event.
8. **Use necessary uncertainty.** `可能性がある` may be essential if the cause is unproven. Do not mechanically replace hedging with assertion. Distinguish data, management explanations, analytical assumptions and recommendations.
9. **Do not force a decision at every page.** The main story may end with an explicit choice, alternatives and reversal conditions. Supporting pages provide evidence without artificial provocations.
10. **Read the entire deck as one voice.** A phrase that's natural once becomes conspicuous when it recurs six times. Review the outline and last sentence of each slide. Ask whether any whole slide repeats the previous slide without new evidence.

## Slide-specific before/after examples

The examples below are editorial illustrations, not claims about a particular factory's actual results.

| Too formulaic (Japanese) | Preferred Japanese | Reason |
| --- | --- | --- |
| `重要なのは、名目成長の裏に潜む構造的な課題を捉えることです。` | `8月の出荷額は前月比1.5%増。価格調整後は横ばい。` | Replaces an empty significance claim with a dated, measurable comparison. |
| `生産数量が計画を超過する一方、売上未達という逆説が浮き彫りになっています。` | `生産は計画比102%、売上は86%。生産品目と販売需要が合っていない。` | Specific finding instead of rhetorical drama. The numeric relation alone does not prove the exact cause without item-level evidence. |
| `単なる仕掛削減ではなく、工場全体の収益力向上につなげることが求められます。` | `不足する共通部品540個をどう配分するかで、来月の出荷と利益が変わる。` | Names a real decision. |
| `今後も継続的なモニタリングが必要であり、注視していくことが重要です。` | `11月の確定受注と部品納期を確認し、生産計画を確定する。` | Assigns a useful next step. |
| `在庫適正化の鍵は、部門横断的な連携の高度化にあります。` | `販売見込の更新を週次で生産計画に反映する。` | Replaces an abstract virtue with an actionable process. |
| `粗利益率の改善は継続的な競争優位を強く示唆しています。` | `粗利益率は3.5ポイント上昇。ただし、継続性は製品構成と一時要因の確認が必要。` | Preserves the boundary between observation and hypothesis. |


## Example: rewriting a public-statistics deck

A draft deck on Canada's August 2026 manufacturing statistics illustrates a common editorial risk. The revised wording is an **example** and must be validated against the underlying evidence before use.

| Draft copy | Better Japanese for this reader |
| --- | --- |
| `名目売上＋1.5%でも、実質の出荷は横ばい` | `8月の出荷額は1.5%増。価格調整後は横ばい。` |
| `8月の改善を「工場の生産能力が向上した」と解釈してはいけない` | `出荷金額の増加だけでは、生産量が増えたとは判断できない。` |
| `月次判断で外してはいけない3点` | `生産計画を決める前の確認事項` |
| `在庫総額＋0.2%の裏で、仕掛品だけが＋0.8%増加` | `在庫総額は0.2%増、仕掛品は0.8%増。` |

**Why:** The original is not all inaccurate. It uses dramatic warnings and rhetorical framing when measured facts and decisions are sufficient. An industry aggregate is not one factory, so do not say `factory capacity improved` or `declined` as if directly observed. Also prefer `出荷額` to `売上` if the official statistic measures manufacturing shipments.

## Review procedure

**Pass A — evidence lock.** Before editing, identify facts that must not change (names, figures, periods, units, source identifiers, forecast/actual distinctions, conditionals, causal strength and decisions). After rewriting, compare against that list.

**Pass B — structural read.** Read the cover, slide titles (starting at slide 2), and conclusion alone. Check for useful progression rather than a parade of identical contrasts or three-item lists. Do not replace clear action titles with generic topic headings solely to appear less AI-like.

**Pass C — line edit.** Remove empty emphasis, repetitious meta-discourse, inflated words, awkward nominalizations, unnatural translated collocations, unnecessary quotation marks, and nested modifiers. Do not overcorrect into colloquial prose.

**Pass D — mechanical flags.** Run `scripts/lint_japanese_style.py`. It examines plain text/Markdown and editable PPTX slide text. Treat each finding as a prompt for contextual human/AI editing, not as a mandatory deletion. Run after final slide regeneration as well.

**Pass E — narrative and display.** Confirm the rendered Japanese copy is legible and adequately explained. Run all previous numeric/semantic/cover/research gates unchanged. Report style scores as heuristic diagnostic results only, never as an AI-authorship score or proof of human comprehension.

## Do not blindly adopt other humanizer skills

- `stop-ai-slop-jp` recommends avoiding proposition-style section titles in essays. In an analytical presentation, evidence-backed action titles are still useful. Apply **only** its advice on needless drama, empty language, and overt word-pattern repetition.
- Some skills encourage adding first-person feelings, edge, rhetorical provocation and deliberate irregularity. These are inappropriate for formal corporate and technical reviews unless requested and grounded.
- Avoid hard-word banlists: `構造的`, `重要`, `可能性`, and `可視化` are sometimes precise technical descriptions. Flag **repetition** and **emptiness**, not their mere occurrence.
