# CONLING — Repetition Resolution (Fix Stage)

## Job

Resolve a list of **already-detected word repetitions** in a labelled manuscript. The list comes from
`word_repetition_detector.py` in scoped mode: each item is a pair of consecutive sentences that share
one or more content words, either within one paragraph or across the boundary between paragraph
`[n]` and `[n+1]`. The detector has already left out headings, captions, citations, direct quotations,
numbers, acronyms, function words and the manuscript's approved field terms.

For each item, read both sentences in their paragraph, decide how to resolve the repetition, and
record the result as one finding: a minimal fix (**REPETITION**) or a reasoned decision to keep the
wording (**RETAIN**).

This is a fix-only pass. Detection has already happened, so do not look for new repetitions or other
prose problems: if something else catches your eye, leave it to the pass that owns it (see Scope).
In the CONLING thesis pipeline this pass runs after Prose Polish Audit, on the post-PP manuscript.

---

## Why

The detector finds repetitions with certainty but cannot judge them: only an editor with context can
tell whether a second "system" is clumsy or whether it is the precise term the argument depends on.
Every fix becomes a diff the editor reviews, so the value of the pass is precision, not elegance. A fix
that restructures more than the repetition needs, or slips in a second unrelated change, costs review
time and breaks the audit trail.

RETAIN exists for the same reason. Many detected repetitions are correct: a technical term, a fixed
phrase, a defined quantity or deliberate parallelism. Recording why such a repetition stays is as
useful to the editor as a fix, because it shows the item was judged rather than skipped.

---

## Categories

- **REPETITION** — the repetition is resolved by an edit (Action edit).
- **RETAIN** — the repetition stays; the Remark says why (Action none, no edit).

---

## Guardrails

### Preservation (these always hold)

- Preserve the factual meaning of every sentence. A fix that removes the repetition but shifts the
  claim is not a fix.
- Never change direct quotations, citations (author, year, page) or the content of tables and figures.
- Never delete content.
- Never vary a field or technical term, a defined term, a variable or scenario name, or a heading's
  wording.

### Resolution strategy, in order of preference

1. **Eliminate** — if one instance can simply go (the second mention is redundant, a pronoun or the
   sentence's own subject carries the reference, or the phrase can be dropped without losing
   content), remove it. This is the preferred fix.
2. **Restructure** — if eliminating would lose content, reword the sentence so the word is needed
   only once, without changing the claim.
3. **Synonym** — a fallback only, when neither of the above works. The synonym must carry exactly
   the same meaning in this context: the same quantity, the same evaluation, the same certainty. If
   no exact synonym exists, do not approximate: use RETAIN.
4. **Retain** — if the repeated word is a term of the field, part of a fixed phrase or name, needed
   for precision, deliberately parallel, or if every fix would shift the claim, keep it and record
   RETAIN with the reason.

Name the strategy you used (eliminate, restructure or synonym) in the Remark. A synonym fix is always
for the editor to confirm, because meaning drift in a near-synonym is easy to miss: "higher" is not
"improved", "contribution" is not "share", "variation" is not "differences".

### Keeping edits minimal

- Change only the words the item needs. If you notice another weakness in the paragraph, leave it:
  it belongs to another pass.
- For an adjacent-paragraph item, change one of the two paragraphs, not both.
- If several items touch the same sentence, resolve them in one edit rather than in overlapping ones.

### Scope

- This pass handles only the items on the work list: one finding per item.
- Out of scope, handled elsewhere in the pipeline:
  - Grammar, syntax, agreement → **ESL Fluency Audit**
  - Sentence rhythm, openers, long sentences → **Prose Polish Audit**
  - Detecting repetitions → **word_repetition_detector.py** (already run)
  - Claim recycling or section-level overlap → **DEDUP_MARKUP**
  - Spelling and punctuation → **Spellcheck Pass**

### When to stop and ask

- If the work list or the manuscript is missing, say so and wait rather than working from a partial set.
- If a work-list label cannot be found in the manuscript, report that item instead of guessing at the
  paragraph it meant.
- Otherwise, proceed: the strategy, the guardrails and the output format settle every other case.

---

## What done looks like

A findings table with one row per work-list item, columns:

| Column | Content |
|---|---|
| `id` | Your finding id (the run tells you the prefix). |
| `Location` | `§x.y, [n]`: section, then the label of the paragraph whose wording changes. For RETAIN, the item's label (its first label for an adjacent pair). |
| `Original Text` | For REPETITION, the words to be changed, copied exactly from paragraph `[n]`. For RETAIN, the repeated word as it appears in paragraph `[n]`. |
| `Category` | REPETITION or RETAIN. |
| `Severity` | Medium if the repetition is noticeable on a normal reading; Low if it is mild. RETAIN rows are Low. |
| `Suggestion` | For REPETITION, the replacement wording for `Original Text`. For RETAIN, empty. |
| `Remark` | Starts with the work-list id(s), e.g. `W12:`; then the strategy used (eliminate, restructure or synonym) or the reason for retaining, in a few words. |

### Self-check before submitting

1. Every work-list item appears in exactly one row, named by its id at the start of the Remark.
2. Every `Original Text` is verbatim in the paragraph its Location names.
3. Every REPETITION keeps the meaning, the field terms, quotations and citations, and changes only what
   the item needs; no word is added that changes the claim (therefore, must, clearly).
4. Every synonym carries exactly the same meaning; where none does, the item is RETAIN.
5. No row raises anything that is not on the work list.

---

## Reference — Required inputs

| File | Role |
|------|------|
| Work list (`word_repetitions.csv`, or the WORK LIST section of the range file) | Items to resolve: id, range, label, label_2, issue_type, stems, sentence_1, sentence_2 |
| Labelled manuscript (`*_for_ai.md`, or the range file) | Full paragraphs for context and verbatim text |

---

## Reference — Worked example

**Work list:**

```csv
"id","range","label","label_2","issue_type","stems","sentence_1","sentence_2"
"W1","R02","88","","SAME_PARA_TWO_SENT","approach","The approach reduced handling time.","Because the approach needs no new equipment, it was adopted on all sites."
"W2","R02","120","","SAME_PARA_TWO_SENT","grower","Most growers in the survey planted canola in rotation.","These growers also kept sheep on the stubble."
"W3","R02","45","46","ADJACENT_PARA","interval","Samples were taken at weekly intervals.","The sampling interval was shortened in the second season."
```

**Findings:**

```csv
"id","Location","Original Text","Category","Severity","Suggestion","Remark"
"M1","§3.2, [88]","Because the approach needs no new equipment, it was adopted","REPETITION","Medium","Because it needs no new equipment, it was adopted","W1: eliminate (pronoun)"
"M2","§4.1, [120]","These growers also kept","REPETITION","Medium","They also kept","W2: eliminate (pronoun carries the reference)"
"M3","§3.1, [45]","intervals","RETAIN","Low","","W3: 'sampling interval' is the defined design parameter; varying it would blur the definition"
```
