# DEDUP_MARKUP — Conceptual Deduplication & Markup Procedure

## Job

Perform conceptual deduplication on an academic manuscript and produce a
downloadable markdown file with inline deletion/addition markup that the
editor can apply directly to the source document. Work within the LANG_EVAL
framework: extract the manuscript, analyse it for duplication, apply markup,
and output the result — see *Reference — Method* for the four-phase
procedure.

This activates when a LANG_EVAL analysis or duplication report has already
been completed (or is run concurrently) and the user requests deduplication
markup on the analysed document.

---

## Why

Academic manuscripts — especially those assembled from multiple contributors
or revised over several drafts — often restate the same claim, mechanism, or
data point in more than one section: an Abstract that repeats Results almost
verbatim, a claim recycled across three sections, a phrase used mechanically
throughout. Left uncorrected, this inflates word count against journal
limits, dilutes the manuscript's argument, and signals to a reviewer that the
piece wasn't tightened before submission.

The task is markup, not rewriting, because the editor — not the model — makes
the final call on each proposed change. The manuscript is Frans's client's
work; a canonical location for a claim, a decision about which of two
near-identical sections to keep, and a judgment about whether a passage adds
genuine nuance are all decisions that belong to the human reviewing the
markup, not to a silent rewrite the author never sees a record of. This is
why every change is annotated with a `[DEDUP-xx]` rationale rather than
applied invisibly, and why anything genuinely uncertain becomes a
`DEDUP-QUERY` comment instead of a decision made on the author's behalf.

> **[Flagged for Frans]** This section is inferred from the shape and stated
> constraints of the source prompt, not quoted from it — confirm the framing,
> particularly whether "reviewer trust" and "word-count limits" are the
> actual stakes you have in mind or whether there's a more specific concern
> (e.g. a particular journal's structural requirements) worth naming instead.

---

## Guardrails

### Preservation principle

- Never rewrite the full manuscript. Produce markup annotations on the
  original text only.
- Never delete content that introduces genuinely new information, data, or
  interpretation — only content that restates what appears elsewhere.
- Never modify direct quotations, statistical data within tables, or
  figure/table content. Tables and figures are marked `[TABLE X UNCHANGED]`
  or `[FIGURE X UNCHANGED]` in the surrounding narrative rather than touched
  directly.
- Replacement text (`{{+...}}`) preserves the register, tense, and
  perspective of the surrounding context.
- Additions are always shorter than the text they replace. If a passage
  cannot be shortened, leave it unmarked and add an advisory comment instead
  of forcing a weaker replacement.
- Minimum deletion granularity is a full sentence. Phrase-level or
  word-level substitutions (e.g. varying sentence openers) belong to
  copy-editing, not deduplication, and must not appear in DEDUP markup.

### Editorial principles

- **State once, reference back.** Each factual claim, mechanism description,
  or data point has exactly one canonical location. Other sections
  cross-reference rather than restate.
- **Reference list integrity.** Mark uncited references with `{{-...}}
  [DEDUP-REF: uncited — remove]`. Insert placeholders for missing references
  with `{{+...}} [DEDUP-REF: missing — author to supply]`.
- **Structural repairs.** Where section numbering or headings need
  correction (e.g. a corrupted heading), mark the old heading with `{{-...}}`
  and the corrected heading with `{{+...}}`, tagged `[DEDUP-A1]` or similar.
- **Typology hierarchy.** Resolve Type A (structural echo) first — it often
  eliminates several Type B instances automatically. See *Reference —
  Duplication typology*.

### Markup conventions

| Marker | Meaning |
|--------|---------|
| `{{-...}}` | **DELETE** this text |
| `{{+...}}` | **ADD** this text (replacement or insertion) |
| `[DEDUP-xx]` | Cross-reference tag linking to the duplication typology (e.g. `[DEDUP-B1]`, `[DEDUP-A1]`) |
| Unmarked text | Leave unchanged |

For each marked deletion or addition, append a bracketed `[DEDUP-xx: brief
rationale]` explaining why the change is made, referencing the duplication
type and the primary/canonical location where the content should remain.

### When to stop and ask

- **`doc_path` missing or ambiguous.** This is the one required input
  (*Reference — Required inputs*). If it isn't clear which file is the
  manuscript to process, ask before proceeding — do not guess at a path or
  process the wrong file.
- **Uncertain whether a passage is redundant or adds nuance.** Do not decide
  this silently either way. Leave the passage unmarked and add:
  `<!-- DEDUP-QUERY: Consider whether this adds to [section]. If not,
  delete. -->` — this is the standing mechanism for genuine uncertainty and
  should be used liberally rather than forcing a call that isn't clearly
  supported by the text.
- **Ambiguous canonical location.** If two sections state a claim with
  equal weight and nothing in the manuscript or the typology hierarchy
  indicates which should be treated as canonical, flag it with a
  `DEDUP-QUERY` comment rather than picking one arbitrarily.
- Proceed without asking on everything else — the markup conventions,
  editorial principles, and output format are settled by this prompt.

---

## What done looks like

One or more markdown files saved to `/mnt/user-data/outputs/`:
`DEDUP_part1.md` (and `DEDUP_part2.md`, etc., if split — see *Reference —
Splitting rules*).

The final part ends with an HTML comment block summarising:

- Total words deleted / added / net reduction
- Structural changes (renumbered sections, restored headings)
- References removed (list) and references added (placeholders)
- DEDUP cross-reference key (all codes used, with one-line descriptions)

Present the files with a concise summary covering:

- The net word reduction and percentage of body text affected
- The single most impactful structural deduplication
- The number of reference-list changes
- A reminder that `{{-...}}` = delete and `{{+...}}` = add

### Self-check before submitting

1. No full-manuscript rewriting has occurred — only markup annotations on
   the original text.
2. No deleted passage introduced genuinely new information, data, or
   interpretation.
3. No direct quotation, table statistic, or figure/table content has been
   modified; all are marked `[TABLE X UNCHANGED]` / `[FIGURE X UNCHANGED]`
   where relevant.
4. Every `{{+...}}` addition is shorter than the `{{-...}}` text it
   replaces, or is left unmarked with an advisory comment instead.
5. No deletion is smaller than a full sentence.
6. Type A (structural echo) has been resolved before addressing residual
   Type B instances.
7. Every marked change carries a `[DEDUP-xx: rationale]` tag.
8. Any passage of genuine uncertainty carries a `DEDUP-QUERY` comment rather
   than a silent decision.

---

## Reference — Trigger

This procedure activates when:

- A LANG_EVAL analysis or duplication report has already been completed (or
  is run concurrently), AND
- The user requests deduplication markup on the analysed document.

---

## Reference — Required inputs

| Input | Required | Description |
|-------|----------|-------------|
| `doc_path` | Yes | Path to the .docx/.pdf/.md manuscript |
| `styleguide_path` | Optional | Path to the target journal's author guidelines |
| `duplication_report_path` | Optional | Path to a prior LANG_EVAL duplication report; if absent, generate the analysis first |
| `split_threshold` | Optional | Max approximate character count per output file before splitting (default: 30,000) |

---

## Reference — Duplication typology

- **Type A — Structural echo**: An entire section re-narrates what another
  section already covers.
- **Type B — Claim recycling**: A specific factual claim or interpretive
  statement recurs across ≥ 3 sections.
- **Type C — Abstract–body mirroring**: The Abstract contains details
  repeated almost verbatim in Results.
- **Type D — Phrase-level repetition**: A fixed phrasal formula recurs
  mechanically.

---

## Reference — Method

### Phase 1 — Extraction & baseline

1. Extract the full manuscript to markdown using `pandoc --wrap=none`,
   preserving tables, figures, emphasis, and heading structure.
2. Measure total word count, section count, and line count to determine
   whether the output must be split into parts.

### Phase 2 — Duplication analysis (if not already available)

3. Run n-gram repetition detection (4-gram through 7-gram) filtered for
   meaningful content phrases (≥ 2 content words per n-gram).
4. Segment the manuscript into sections and run thematic distribution
   scanning across 12–15 theme patterns relevant to the manuscript's domain.
5. Perform targeted claim-repetition searches: identify specific factual
   claims, data points, and interpretive statements, then locate every
   section in which each recurs.
6. Compare structurally parallel sections (e.g. Abstract ↔ Conclusions, KII
   narrative ↔ SWOT discussion) for overlapping content.
7. Check the reference list for uncited entries and the body text for
   cited-but-missing references.
8. Classify all duplications into the four types in *Reference — Duplication
   typology*.

### Phase 3 — Markup generation

9. Work through the manuscript sequentially, section by section, applying
   the markup conventions in Guardrails.
10. For each marked deletion or addition, append the `[DEDUP-xx: brief
    rationale]` tag as described in Guardrails.
11. Apply the editorial principles and preservation principle in Guardrails
    throughout.

### Phase 4 — Output

12. **Splitting rules.** If the total marked-up markdown exceeds
    `split_threshold`:
    - Split at a natural section boundary (between major numbered sections).
    - Part 1 ends with `<!-- END OF PART 1 — continues in DEDUP_part2.md -->`.
    - Part 2 begins with `<!-- PART 2: [section range] -->` and repeats the
      markup key.
    - Continue splitting (Part 3, etc.) if necessary.
13. Save the output file(s) and present them per *What done looks like*.

---

## Reference — Example invocation

```
run DEDUP_MARKUP with {
doc_path = "manuscript.docx",
styleguide_path = "journal_guidelines.pdf",
duplication_report_path = "LANG-EVAL_duplication_report.md"
}
```
