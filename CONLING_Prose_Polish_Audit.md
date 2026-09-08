# CONLING — Prose Polish Audit Prompt

## Job

Perform a prose rhythm and readability pass on an academic manuscript.
Intervene only where one of the eight trigger criteria below is met
(*Reference — Trigger criteria*): weak sentence openers, close-proximity
repetition, overlong sentences, duplicate in-text citations, stacked
qualifiers, and L1 intensifiers on standard academic verbs. Do not rewrite,
restructure arguments, or change domain terminology.

This is not a grammar, content, or ESL fluency pass — those are handled
elsewhere (see Guardrails → Scope). Run this pass *after* the ESL Fluency
Audit and the L1 Interference Analysis, so that residual sentence-level
issues not caught by those passes surface here.

Depending on `Mode` (see Session Parameters), either return the findings CSV
only and wait for confirmation (`review`), or return the findings CSV and the
corrected labelled paragraphs together (`apply`).

---

## Why

Five sibling CONLING passes all touch sentence-level language in some way,
and without clear boundaries between them a manuscript ends up either
under-edited (each pass assumes another will catch an issue) or
over-processed (multiple passes flag and re-flag the same passage,
costing Frans review time reconciling contradictory or duplicate findings).
This prompt exists to own a specific, narrow band — sentence rhythm and
flow — precisely so the passes stay additive rather than redundant. See
*Guardrails → Scope* and *Reference — Relationship to other CONLING passes*
for exactly where the line sits.

The repetition trigger (4) carries an extra piece of reasoning worth stating
directly: general same-stem repetition is properly the job of
`word_repetition_detector.py`, feeding the Repetition Resolution pass — that
pipeline is the more reliable way to catch it, since it's exhaustive and
script-driven rather than dependent on what a model happens to notice while
reading. This prompt's own repetition detection exists only as a fallback
for when that script hasn't been run — most often because it was simply
forgotten before this pass was invoked directly. Running both detection
paths on the same manuscript is wasted, duplicated effort; the guardrail
below exists to prevent that, not to relitigate which pass "owns"
repetition.

---

## Guardrails

### Scope

- Focus is sentence-level flow only — not grammar, not content, not ESL
  fluency.
- The following are out of scope, handled elsewhere:
  - Grammar, SVA, wrong articles or prepositions → **ESL Fluency Audit**
  - Register mismatch, colloquial vocabulary → **ESL Fluency Audit**
  - Hollow academic openers (*The study reveals valuable insights*; *It
    infers that*) → **ESL Fluency Audit — Trigger 5**
  - L1 transfer at clause/discourse level → **L1 Interference Analysis**
  - Claim recycling or section-level structural overlap → **DEDUP_MARKUP**
  - Reference and citation format compliance → **Citation Audit / Reference
    Cleanup** (this pass only flags duplicate citation *placement* as a
    prose-flow issue — see Trigger 6)
  - Spelling standardisation → **Spellcheck Pass**
- See *Reference — Relationship to other CONLING passes* for the full table.

### Repetition detection — check before applying Trigger 4

Before scanning for close-proximity word repetition yourself, check whether
`word_repetitions.csv` (the output of `word_repetition_detector.py`) is
available for this manuscript.

- **If it is available and Repetition Resolution has run, or will run,
  against it:** do not re-detect general same-stem repetition here — that
  work is already covered and duplicating it wastes review time. Still apply
  the two rules below that the script-fed pipeline does not cover: repeated
  author names opening or closing consecutive sentences, and mechanical
  recurrence of structural words (*support, found, show, result, analysis,
  study, indicate, suggest, provide*).
- **If it is not available** — most commonly because the detector script
  simply wasn't run before this pass was invoked directly — apply the full
  Trigger 4 criterion yourself, including general same-stem repetition, using
  the resolution hierarchy and constraints in *Reference — Trigger criteria*.
- **If you cannot tell** whether the script has already been run or is
  planned, ask before proceeding rather than assuming either way — see When
  to stop and ask.

### Preservation principle

- Never substitute domain terms under any trigger, including `REPETITION`.
  In discipline-specific writing, near-synonyms are not synonyms — do not
  replace *cattle*, *beef*, *expenditure*, *household*, *ownership*,
  *elasticity*, or any other field-specific term with a variant, even if it
  repeats.
- Do not flag deliberate anaphora — a key term repeated for rhetorical
  cohesion or thematic emphasis stays.
- Do not impose an artificial minimum length when splitting long sentences —
  the goal is restoring the word-count condition, not equalising the two
  halves.
- Tables, figures, and figure/table captions are not subject to the
  sentence-length trigger.

### Labelling convention

The manuscript must be pre-labelled with paragraph identifiers in the format
`[n]` (e.g. `[8]`, `[13]`, `[29]`). Each finding cites the paragraph label.
If a finding spans two paragraphs, cite both (e.g. `[13]–[14]`).

### When to stop and ask

- **Mode not specified.** If Session Parameters doesn't state `review` or
  `apply`, ask which is wanted rather than assuming — the two produce
  materially different deliverables (findings only, versus findings plus
  applied text).
- **Unclear whether repetition detection has already run.** If it isn't
  clear whether `word_repetitions.csv` exists or Repetition Resolution has
  already processed this manuscript, ask rather than guessing — guessing
  wrong either duplicates work already done or silently skips repetition
  detection that nothing else will catch.
- **Target language variant not established**, and a synonym is needed to
  resolve a repetition trigger. Defer to the project brief if stated; if
  neither Session Parameters nor a brief settles it, ask.
- Proceed without asking on everything else — the trigger criteria and
  output format are settled by this prompt.

---

## What done looks like

Return **only** a CSV file. No preamble, no post-amble, no summary prose.
Every field enclosed in double quotes, fields separated by commas. Column
headers exactly:

```
"label","issue_type","original","remark","solution"
```

| Column | Content |
|---|---|
| `label` | Paragraph identifier, e.g. `[25]` |
| `issue_type` | One of: `OPENER-THIS`, `OPENER-THERE`, `OPENER-IT`, `REPETITION`, `LONG-SENT`, `DUP-CITE`, `DBL-QUALIFIER`, `L1-INTENSIFIER` |
| `original` | Verbatim passage from the manuscript — as short as possible while locating the issue unambiguously |
| `remark` | One sentence explaining the trigger criterion met |
| `solution` | Proposed replacement. For `LONG-SENT`, provide the full split as two sentences. For `REPETITION`, provide the sentence containing the second instance with the repeated word replaced. |

If `Mode` is `apply`, also return the corrected labelled paragraphs
reflecting every row in the CSV, in one response alongside the CSV.

### Output rules

- One row per finding.
- Order findings by label, ascending.
- Within a label, order by `issue_type` if multiple findings exist.
- Do not merge multiple issue types into one row.
- Do not output a row where `original` and `solution` are substantively the
  same.
- Do not flag domain terminology under `REPETITION` under any circumstances.

### Self-check before submitting

1. Every `original` value can be found verbatim in the manuscript.
2. No `solution` changes the factual content, domain terminology, or
   argument.
3. No domain term has been substituted under `REPETITION`.
4. If `word_repetitions.csv` was available, no `REPETITION` row duplicates a
   general same-stem finding already owned by the Repetition Resolution
   pass — only author-name and structural-word repetition rows appear.
5. Every `LONG-SENT` solution is two grammatically complete sentences with no
   orphaned clauses.
6. The CSV opens with the header row and contains data rows only — no
   markdown fences, no explanatory text.

---

## Reference — Session parameters

**Target language variant: [SPECIFY: en-GB | en-US | other]**
*Applied when synonyms are required for REPETITION solutions. Leave blank to
defer to the project brief.*

**Mode: [review | apply]**
- `review` — return the findings CSV only; wait for confirmation before
  producing edited text
- `apply` — return the findings CSV and the corrected labelled paragraphs in
  one response

---

## Reference — Trigger criteria

**1. Weak opener — `This/These + verb`**

Sentences opening with *This* or *These* followed directly by a verb or a
verb phrase (*This shows…*, *These confirm…*, *This suggests…*, *These
findings indicate…*). Rework to a more specific subject or restructure so
the sentence leads with the actor or the finding.

> Exception: *This study*, *This paper*, *This article*, *This section* as a
> subject is acceptable where the study itself is the referent.

**2. Weak opener — `There + be / verb`**

Sentences opening with *There is*, *There are*, *There was*, *There were*, or
*There exists*. Restructure to assign the logical subject its proper
position as grammatical subject.

> Exception: *There is growing evidence that…* and similar idiomatic
> scholarly phrases where the existential construction is the norm may be
> left or flagged at editorial discretion.

**3. Weak opener — `It + verb` (hollow existential or impersonal
construction)**

Sentences opening with *It is*, *It was*, *It should be noted*, *It is worth
noting*, *It is important to note*, *It is evident*, *It can be seen*, or
similar impersonal constructions. Rework to a direct subject–verb structure.

> Exception: *It follows that…* and *It appears that…* in inferential chains
> are borderline; flag rather than mandate change.

**4. Word repetition in close proximity**

The same word stem used more than once within a two-sentence window in the
same paragraph, or once each in two adjacent paragraphs, where the
repetition is unintentional and creates a jarring or flat effect. See
*Guardrails → Repetition detection* for when to apply this in full versus
the narrowed version.

Apply the following resolution hierarchy in this order:

1. **Retain at least one instance from the original** — always keep the
   first or the second occurrence; never delete both.
2. **Eliminate one instance if the sentence allows it** — preferred solution.
   Restructure the sentence so the word is needed only once without loss of
   meaning.
3. **Use a synonym for one instance if necessary** — fallback only, when
   elimination would require restructuring that distorts the meaning or the
   syntax.

Constraints, applied strictly regardless of which version of the trigger is
active:

- **Never substitute domain terms.** Flag only non-technical content words
  and structural words.
- **Do not flag deliberate anaphora.**
- **Do flag structural words that recur mechanically:** *support*, *found*,
  *show*, *result*, *analysis*, *study*, *indicate*, *suggest*, *provide* —
  when the same form appears within two sentences.
- **Do flag repeated author names.** When the same author name (*Smith*,
  *Hosu et al.*, *FAO*) opens or closes two consecutive sentences, flag as
  `REPETITION`. The preferred fix is to merge the two sentences into one so
  the author is named once; do not substitute a different name.

**5. Long sentence — exceeds 34 words**

The target for all body-text sentences is **up to 34 words**. Any sentence
that exceeds this threshold must be split at the nearest natural clause
boundary (coordinating conjunction, relative clause boundary, or adverbial
clause boundary) so that each resulting sentence is itself within the
34-word limit.

> Exceptions: sentences containing a list of three or more enumerated items
> (splitting fragments the list); sentences that form a single tight logical
> unit where splitting would introduce ambiguity; table and figure captions.

**6. Duplicate in-text citation**

The same citation key (e.g. `[R12]`, `(Hosu et al., 2012)`) appearing more
than once within the same paragraph, where both instances cite the source
for closely related or identical claims. The preferred fix is to merge the
citing sentences so the reference appears once. If the two sentences make
genuinely distinct claims from the same source that cannot be merged, retain
both citations but flag for editorial review.

> Scope: citation duplication as a *prose-flow* issue only — not citation
> format compliance, which belongs to the Citation Audit pass.

**7. Double qualifier stacking**

Two near-synonymous qualifiers or adverbs in the same clause (*particularly …
specifically*, *mainly … especially*, *broadly … generally*). Remove the
weaker one; retain the more precise.

**8. L1 intensifiers on standard academic verbs**

Intensifying adverbs (*strongly*, *greatly*, *highly*, *deeply*, *firmly*)
placed before verbs that carry no degree of intensity in standard academic
English (*acknowledge*, *recommend*, *note*, *confirm*, *state*). Remove the
intensifier; the verb is sufficient. Flag in context, as this is a common L1
transfer pattern from Bantu and other Afrikaans-influenced registers.

> This trigger is complementary to, not duplicative of, the L1 Interference
> Analysis prompt, which flags this pattern at a higher structural level.
> Record it here when found at the word level in an otherwise clean
> sentence.

---

## Reference — Relationship to other CONLING passes

| Issue | Primary pass |
|---|---|
| Hollow academic openers (*The study reveals valuable insights*; *It infers that*) | ESL Fluency Audit — Trigger 5 |
| Domain-term near-synonyms, wrong collocations, register mismatch | ESL Fluency Audit — Triggers 1–4 |
| L1 transfer at structural/discourse level | L1 Interference Analysis |
| Content-level deduplication | DEDUP_MARKUP |
| `This/There/It` opener counts, long-sentence metrics | LANG_EVAL_preset — detection/scoring |
| General same-stem word repetition, when `word_repetitions.csv` exists | **Repetition Resolution** (via `word_repetition_detector.py`) |
| **Sentence-level opener patterns, sentence splitting, qualifier stacking, L1 intensifiers, author-name and structural-word repetition, and same-stem repetition when the detector script has not been run** | **This prompt (Prose Polish Audit)** |

Run this pass *after* the ESL Fluency Audit and *after* the L1 Interference
Analysis so that residual issues not caught by those passes surface here.
