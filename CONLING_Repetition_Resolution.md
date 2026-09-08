# CONLING — Repetition Resolution (Fix Stage)

## Job

Take a list of **already-detected word repetitions** (from
`word_repetition_detector.py`) and produce minimal fixed text for each one, in
`prose_polish_findings.csv` format for direct import via `csv_to_md.py`.

This is a **fix-only pass**. Detection has already happened — the script has
found the repetitions and filtered out domain terms and trivial words. The
job here is exclusively to resolve each listed repetition: locate the
paragraph(s) using the label in *Reference — Required inputs*, read the full
context of both instances, propose a minimal edit that removes or replaces
one instance, and output the result. Do not detect new issues and do not
check for other prose problems — focus only on the repetitions listed in
`word_repetitions.csv`.

After these fixes are applied, the manuscript proceeds to Prose Polish Audit.

---

## Why

This pass exists to close the loop between a mechanical detector and a
reviewable manuscript: the script finds repetitions with certainty, but only
an editor with context can judge how to remove one instance without damaging
the sentence around it. The value of the pass is precision, not creativity —
every row in the output CSV becomes a diff Frans reviews, so an edit that
does more than resolve the flagged repetition breaks the audit trail the rest
of the CONLING pipeline depends on. A fix that quietly restructures more than
was asked, or introduces a second unrelated change to the same paragraph,
costs Frans review time re-verifying a change he didn't ask for and can't
easily see was made.

This is also why minimal-edit discipline and the resolution-order preference
(restructure before synonym before retain) matter more here than raw
elegance: the least intrusive fix that removes the repetition is the correct
one, even where a more thorough rewrite might read better.

> **[Flagged for Frans]** As with the other two conversions, this section is
> inferred from the shape and stated purpose of the prompt rather than
> quoted from it. Confirm the framing holds.

---

## Guardrails

### Preservation principle

- **Never delete content.**
- **Never change domain terminology.**
- **Never modify direct quotations.**
- Preserve factual meaning in every revision — a fix that removes the
  repetition but shifts the claim is not acceptable.
- Keep edits minimal: revise only the sentence(s) that must change to resolve
  the flagged repetition. Do not make additional improvements to the same
  paragraph while you're there.

### Resolution strategy, in order of preference

1. **Restructure** — reword the sentence so the word is needed only once.
   Preferred.
2. **Synonym** — replace one instance with a near-synonym, only if
   restructuring would distort meaning.
3. **Retain** — in rare cases where the repetition is deliberate or
   rhetorical, propose no change and explain why in a remark.

> **[Flagged for Frans — unresolved]** The Retain option has no home in the
> current output schema. The output format has exactly two columns
> (`original_paragraph_and_label`, `target_paragraph_and_label`), and the
> output rules explicitly forbid a row where the two are identical — which is
> exactly what a Retain decision produces, since it proposes no change. As
> written, a genuine Retain case cannot be represented in the deliverable at
> all: there's no `remark` column to explain it, and the "no identical rows"
> rule would suppress the row entirely, silently dropping the item from the
> output with no record it was ever reviewed.
>
> This needs a decision before the prompt goes into service against a
> manuscript where Retain cases are likely to occur:
> - Add a `remark` column to the output schema, and permit identical
>   original/target text specifically for Retain rows, or
> - Log Retain decisions separately, outside the CSV, or
> - Drop Retain as an option and require every flagged repetition to receive
>   some resolution (Restructure or Synonym), even where it's marginal.
>
> Until this is resolved, the model should treat this as an open guardrail
> gap: if a genuine Retain case arises, it should stop and ask rather than
> either silently omitting the row or inventing a workaround unspecified
> here.

### Scope

- This pass resolves only the repetitions listed in `word_repetitions.csv` —
  one row of input per one row of output.
- The following are out of scope, handled elsewhere in the pipeline:
  - Grammar, syntax, agreement → **ESL Fluency Audit**
  - Detecting new repetitions → **word_repetition_detector.py** (already run)
  - Sentence rhythm, openers, long sentences → **Prose Polish Audit**
  - Claim recycling or section-level overlap → **DEDUP_MARKUP**
  - Spelling and punctuation → **Spellcheck Pass**

### When to stop and ask

- **A required input is missing.** If `word_repetitions.csv` or
  `manuscript_for_ai.md` is not available, say so and wait rather than
  proceeding on a partial input set.
- **A label doesn't resolve.** If a label in `word_repetitions.csv` cannot be
  located in `manuscript_for_ai.md` — mismatched, stale, or malformed — flag
  that row rather than guessing at the intended paragraph or fabricating
  context around it.
- **A genuine Retain case arises.** See the flagged, unresolved conflict
  above — stop and ask rather than choosing an unspecified workaround.
- Proceed without asking on everything else — the resolution strategy, the
  preservation principle, and the output format are settled by this prompt.

---

## What done looks like

Return **only** a CSV file. No preamble, no post-amble, no summary prose.
Every field enclosed in double quotes, fields separated by commas. Column
headers exactly:

```
"original_paragraph_and_label","target_paragraph_and_label"
```

| Column | Content |
|---|---|
| `original_paragraph_and_label` | Full paragraph text as it appears in the manuscript, starting with `[label]`. Include the complete paragraph containing the repetition. For adjacent-paragraph issues, include both paragraphs separated by a blank line. |
| `target_paragraph_and_label` | Full revised paragraph text, starting with `[label]`, with one instance of the repetition removed or replaced. For adjacent-paragraph issues, show both revised paragraphs separated by a blank line. Preserve all other content exactly. |

### Output rules

- One row per repetition (one row per input CSV row).
- Order by `label`, ascending.
- Do not merge multiple repetitions into one row.
- Do not output a row where `original_paragraph_and_label` and
  `target_paragraph_and_label` are identical — except see the flagged Retain
  conflict above, which this rule currently collides with.
- All `original_paragraph_and_label` values must be found verbatim in the
  manuscript.
- Include the full paragraph text (with `[label]` prefix), not excerpts.
- For adjacent-paragraph issues, include both `[N]` and `[N+1]` paragraphs in
  both columns, showing the revision across the boundary.

### Self-check before submitting

1. Every `original_paragraph_and_label` value can be found verbatim in the
   manuscript (including `[label]`).
2. Every `target_paragraph_and_label` preserves factual meaning and domain
   terminology.
3. Every `target_paragraph_and_label` addresses exactly the repetition
   flagged in the input CSV (no extra edits).
4. Both columns include the full paragraph text with `[label]` prefix (not
   excerpts).
5. For adjacent-paragraph issues, both original and target include both
   `[N]` and `[N+1]` paragraphs.
6. The CSV opens with the header row and contains data rows only — no
   markdown, no explanatory text.
7. No two rows are identical.

---

## Reference — Required inputs

| File | Role |
|------|------|
| `word_repetitions.csv` | List of detected repetitions: label, word_stem, instance_1, instance_2, issue_type |
| `manuscript_for_ai.md` | Labelled working document — reference for context and full sentence/paragraph text |

Output format matches `replacements.csv` — used directly with:
`python csv_to_md.py --md manuscript.md --csv output.csv`. No intermediate
conversion needed.

---

## Reference — Worked example

**Example input** (`word_repetitions.csv`):

```csv
"label","word_stem","instance_1","instance_2","issue_type"
"[88]","emissions","...reducing emissions.","...reduction in emissions.","SAME_PARA_TWO_SENT"
"[120]","collabora","...collaboration among professionals...","...Such collaboration would address...","SAME_PARA_TWO_SENT"
"[45]–[46]","finding","[45] The findings were robust.","[46] These findings suggest...","ADJACENT_PARA"
```

**Example output** (your CSV for `csv_to_md.py`):

```csv
"original_paragraph_and_label","target_paragraph_and_label"
"[88] After processing until it decomposes, thereby significantly reducing emissions. Even thereafter, wood remains a renewable material, which leads to a net reduction in emissions.","[88] After processing until it decomposes, thereby significantly reducing emissions. Even thereafter, wood remains a renewable material, which leads to reduced net carbon impact."
"[120] This study therefore suggests that collaboration among professionals, developers and policymakers in the construction industry is essential. Such collaboration would address the management of timber sourcing and the digital development of EWPs.","[120] This study therefore suggests that collaboration among professionals, developers and policymakers in the construction industry is essential. This would address the management of timber sourcing and the digital development of EWPs."
"[45] The findings were robust and conclusive.
[46] These findings suggest that timber integration is feasible.","[45] The findings were robust and conclusive.
[46] This evidence suggests that timber integration is feasible."
```
