# CONLING — Passive-to-Active Voice Audit Prompt

## Job

Perform a voice pass on a manuscript: find the specific instances where the
passive voice is doing no useful work — where it obscures the actor, inflates
the sentence, or breaks the rhythm — and convert only those to active voice.
Everywhere else, leave the passive alone.

This is a self-contained pass. It does not require the output of any other
CONLING pass and does not consume a pre-compiled findings list — it performs
its own detection and its own resolution in a single pass, reading the
manuscript in full and applying the Golden Rule test (see Guardrails) to
every passive construction found.

Return two files: an editorial findings CSV for conversions you can resolve
outright, and an author-queries TSV for the ones you can't (see What done
looks like).

---

## Why

The passive voice is a normal, correct, and frequently superior English
construction — in formal registers it is often the *only* appropriate choice.
This is not a grammar-correctness pass; there is no rule being enforced that
says passive is wrong. The task exists because passive constructions
sometimes do real work (methods sections, statutory drafting, preserving a
topic chain, keeping a heavy subject out of the way) and sometimes don't
(hiding an actor the reader needs, stacking into flat prose, inflating a
simple action into a weak-verb phrase) — and only a reader-level judgment can
tell the two apart.

The dominant failure mode of this kind of pass is over-conversion: a model
told to "find and fix passives" will find grammatical passives everywhere
and convert mechanically, producing a manuscript that reads as *less*
professional in the registers where passive is convention (methods sections,
legal drafting), and that breaks topic chains and buries real subjects
elsewhere. A pass that returns twelve well-chosen conversions is more useful
than one that returns ninety mechanical ones. Every guardrail below exists to
hold that line.

---

## Guardrails

### The Golden Rule — improvement, not conversion

> **A passive construction is not a defect. If the active version is
> demonstrably more natural to read, convert it; if it is not, leave the
> passive in place.**

Before recording any finding, apply this test in order:

1. **Write out the active version.** Actually construct it. Do not assume it
   will be better.
2. **Read both aloud.** Which one would a fluent native reader move through
   without pausing?
3. **Check what was gained.** The active version must deliver at least one
   of: a named actor where the actor matters, fewer words with no loss of
   meaning, better information flow, or a stronger verb.
4. **Check what was lost.** If the active version forces a vague or invented
   subject, buries the sentence's real topic, breaks the link to the
   previous sentence, or changes emphasis in a way the author did not
   intend — **abandon the conversion and move on.**

If steps 3 and 4 do not clearly favour the active version, **do not record a
finding.**

### Counter-criteria — do not convert when any of these apply

These are not soft preferences. If any counter-criterion applies, the
passive stays, even if a trigger criterion (*Reference — Trigger criteria*)
also applies.

**A. The actor is genuinely unknown, irrelevant, or deliberately unstated.**
If you would have to invent a subject, guess at one, or fall back on a vague
placeholder (*someone*, *the relevant party*, *one*), the passive is correct.
Do not convert. If the actor is unknown **and the reader needs it**, that is
a TSV item, not a CSV item.

**B. The passive is the established convention of the genre.**
Methods sections in scientific writing (*Samples were incubated at 37°C*),
legal and statutory drafting (*A person shall be deemed to have
contravened…*), and formal definitions routinely use the agentless passive by
convention. Converting these makes the text read as *less* professional, not
more. This is the single most common way a voice pass goes wrong.

**C. The passive preserves the topic chain.**
English prefers given information first, new information last. If the
sentence's grammatical subject is the topic carried over from the previous
sentence, converting to active will break that thread and force the reader
to re-orient.

**D. The passive keeps a long or heavy subject out of the way.**
If the active version would open the sentence with a long noun phrase before
reaching the verb, the passive is doing real work. Leave it.

**E. The passive is in a direct quotation, a cited statutory provision, or a
verbatim extract.**
Never alter quoted or statutory text under any circumstances.

**F. The passive softens an attribution the author may have softened
deliberately.**
*Concerns have been raised about the allocation* may be a deliberate choice
not to name who raised them. Do not force attribution the author avoided. If
it reads as evasion rather than discretion, that is a TSV item.

**G. The conversion would require changing terminology, adding information
not in the text, or altering the scope of the claim.**
The `to_replace` value must contain exactly the same information as the
`original`. Converting is a syntactic operation, not a licence to add facts.

### Register calibration

The intervention threshold shifts with the document's register — see
*Reference — Register calibration table*. When in doubt about which threshold
applies to a given passage, apply the more conservative one.

### Labelling convention

The manuscript must be pre-labelled with paragraph identifiers in the format
`[n]` (e.g. `[8]`, `[13]`, `[29]`). The `original` value must be reproducible
**verbatim** from the manuscript and must be long enough to locate the
instance unambiguously — but no longer. Quote the clause or sentence
containing the passive, not the whole paragraph.

### Scope

Do not record findings for, or silently fix, any of the following. If you
notice them, ignore them — they belong to other passes.

- Sentence length, weak openers (*This/There/It*), sentence rhythm → **Prose Polish Audit**
- Grammar, subject–verb agreement, articles, prepositions → **ESL Fluency Audit**
- L1 transfer patterns → **L1 Interference Analysis**
- Word repetition → **Word Repetition Pass**
- Content duplication → **DEDUP_MARKUP**
- Citation format, reference lists → **Citation Audit**
- Spelling standardisation → **Spellcheck Pass**
- Nominalisations not involving a passive verb (*the implementation of* →
  *implementing*) — related, but out of scope here

**One exception, tightly bounded:** where converting a passive would leave
the sentence grammatically broken unless an adjacent word changes (an
article, a preposition, or subject–verb agreement on the new subject), make
that minimal adjustment as part of the conversion. Do not extend this to any
improvement beyond what the conversion strictly requires.

### When to stop and ask

- **Manuscript missing.** If `manuscript_for_ai.md` is not available, say so
  and wait. Do not proceed on a pasted excerpt unless the user explicitly
  confirms the excerpt is the complete scope.
- **Target language variant not established.** If Session Parameters is
  blank and no style guide is supplied, defer to the project brief; if
  neither settles it, proceed and flag the assumption in the first line of
  the CSV rather than guessing silently.
- **Document register not established.** Register materially changes the
  intervention threshold (see Register calibration), so do not assume a
  default register such as `academic`. If the document's subject area or
  discipline hasn't already been made clear earlier in this conversation —
  for instance because the manuscript itself is self-evidently a financial
  report, a policy document, or a piece of legal drafting, or because it was
  stated when this pass was requested — ask which register applies before
  beginning. If it has already been established in context, proceed on that
  basis without asking again.
- Proceed without asking on everything else — the trigger and counter-criteria,
  the Golden Rule, and the output format are settled by this prompt.

---

## What done looks like

Return **two files**. No preamble, no post-amble, no summary prose between or
after them.

### File 1 — `passive_to_active_findings.csv`

Every field enclosed in double quotes, fields separated by commas. Column
headers exactly:

```
"original","to_replace"
```

| Column | Content |
|---|---|
| `original` | The exact verbatim passage from the manuscript, prefixed with its paragraph label in square brackets — e.g. `[292] The questionnaire is sent to trust administrators.` |
| `to_replace` | The proposed active-voice replacement, prefixed with the same label. Identical in meaning, terminology, and scope to the original |

**CSV output rules**

- One row per conversion.
- Order by label, ascending. Within a label, order by position in the
  paragraph.
- Do not output a row where `original` and `to_replace` are substantively the
  same.
- Do not output a row for any instance meeting a counter-criterion.
- Do not merge two separate conversions into one row, even within the same
  sentence — unless converting one necessarily requires converting the
  other, in which case treat the whole sentence as one row.
- The `to_replace` value must be a grammatically complete, correctly
  punctuated replacement that can be dropped into the manuscript as-is.

### File 2 — `passive_author_queries.tsv`

Tab-separated. Column headers exactly:

```
Position	Issue	Comment
```

This file is **only** for items that cannot be resolved editorially — where
converting to active would require information only the author has, or would
force an attribution decision that is not yours to make.

| Column | Content |
|---|---|
| `Position` | Paragraph label, e.g. `[292]`. For a pattern spanning several paragraphs, list them comma-separated |
| `Issue` | Short description of what blocks the conversion (under ~15 words) |
| `Comment` | The question for the author, phrased as a question rather than an instruction. State what the passive currently obscures and what you would need in order to convert it |

**Route an item to the TSV — not the CSV — when:**

- The actor is unknown to you but the reader plainly needs it (*Approval was
  granted in March* — by whom?).
- Converting would assign responsibility or liability, and the correct party
  is not stated anywhere in the document.
- The passive may be deliberate discretion rather than evasion, and only the
  author can say which.
- The same unattributed passive recurs as a pattern across the document,
  such that the answer is a document-wide decision rather than a line edit.

**TSV output rules**

- One row per query. Order by first label, ascending.
- Never place a speculative conversion in the CSV and *also* query it in the
  TSV. Each instance goes to exactly one file.
- If there are no author queries, still return the file with the header row
  only.

### Self-check before submitting

1. Every `original` value can be found verbatim in the manuscript, including
   its `[label]` prefix.
2. Every `to_replace` value preserves the exact meaning, scope, terminology,
   and hedging of the original — no facts added, none removed.
3. Every `to_replace` value is grammatically complete and correctly
   punctuated, and could be pasted into the manuscript without further
   editing.
4. **No row converts an instance that meets a counter-criterion.** Re-read
   the counter-criteria and re-check the rows against them; this is where a
   voice pass most often overreaches.
5. No conversion introduces an invented, vague, or placeholder subject.
6. No conversion alters quoted, statutory, or definitional text.
7. No conversion breaks the topic chain with the preceding sentence.
8. No instance appears in both the CSV and the TSV.
9. Both files open with their header row and contain data rows only — no
   markdown fences, no explanatory text.

**Final calibration check:** count your CSV rows against the manuscript's
length. If you have converted more than roughly one instance per 150 words
of body text, you have very likely over-converted. Re-read the
counter-criteria and cut the weakest rows before submitting.

---

## Reference — Session parameters

**Target language variant: [SPECIFY: en-GB | en-US | other]**
*Applied to all lexical choices and spelling in the `to_replace` column.
Leave blank to defer to the project brief.*

**Document register: [SPECIFY: academic | policy | legal | technical | general]**
*This setting materially changes the threshold for intervention — see
Register calibration table below. Do not assume a default; see Guardrails →
When to stop and ask.*

---

## Reference — Required inputs

| File | Required | Role |
|------|----------|------|
| `manuscript_for_ai.md` | Yes | Labelled working document — all `[n]` paragraph references draw from this file |
| `styleguide_path` | Optional | Target journal or institutional guidelines — consult if voice preference is stated |

---

## Reference — Trigger criteria

Convert when the passive exhibits one or more of these:

**1. Agentless passive where the actor is known and matters**

The sentence hides who acts, but the actor is identifiable from context and
the reader needs it. Common in procedural and process text, where knowing
who performs a step is the entire point.

> *The questionnaire is sent to trust administrators.* → *The Division sends
> the questionnaire to trust administrators.*

**2. `by`-phrase passive with the actor already named**

The actor is stated in a trailing `by` phrase, so the sentence carries the
full information but in a roundabout order. Converting usually shortens the
sentence and puts the actor where the reader expects it.

> *The report is compiled annually by the NAMC.* → *The NAMC compiles the
> report annually.*

**3. Passive stacking**

Two or more passive constructions in a single sentence, or three or more
consecutive sentences all in the passive. Even where each instance is
individually defensible, the accumulation flattens the prose. If stacking is
present, convert the one or two instances that convert most cleanly; if
converting further would not clearly improve the passage, leave the rest as
passive.

**4. Inflated passive with a weak verb**

Passive constructions built on *is made*, *is given*, *is done*, *is carried
out*, *is undertaken*, *is provided*, *is conducted* — where a single active
verb replaces the whole phrase.

> *A submission is made by the Division.* → *The Division submits.*
> *Verification of the information is carried out.* → *The administrators
> verify the information.*

**5. Passive that obscures obligation or responsibility**

Particularly important in policy, procedural, and compliance text. *Records
must be kept* leaves it unclear who is liable. Where the responsible party is
identifiable, name it.

> *Records must be kept for five years.* → *Trust administrators must keep
> records for five years.*

**6. Double passive**

Two passives chained through an infinitive or participle, which is nearly
always harder to parse than the active equivalent.

> *The report is required to be submitted by the trustees.* → *The trustees
> must submit the report.*

---

## Reference — Register calibration table

| Register | Threshold | Notes |
|---|---|---|
| `general`, `technical` | Low — convert freely where the active is better | Reader-facing prose benefits most from active voice |
| `academic` | Moderate — convert in discussion and introduction; be conservative in methods | Methods-section passives are conventional (Counter-criterion B) |
| `policy` | Moderate — favour conversion in procedural and process passages, where naming the responsible party has practical value | Definitions and legal provisions stay passive |
| `legal` | High — convert only inflated and double passives (Triggers 4 and 6) | Statutory drafting convention dominates; agentless passive is correct |
