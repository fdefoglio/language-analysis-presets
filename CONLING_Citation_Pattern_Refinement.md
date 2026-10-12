<!--
HOW TO USE THIS PROMPT (note to self; not part of the prompt)

Attach both of these before running it:
  1. citation_patterns.csv
     Columns: citation | count | dominant_pattern | pattern_frequency |
     locations | suggestion
  2. The manuscript, as full text with paragraph labels [13] through [1326]
     (so every [N] in the locations column can be found).

If either is missing, the model should say so and wait. It should not work
from a pasted excerpt unless you confirm the excerpt is the complete scope.

What the model works on:
  Only citations flagged with pattern_frequency of 50% or more. It rewrites
  the instances that use the dominant pattern, then normalises the tense of
  the reporting verb across all instances of the same author/year.

What you get back:
  One CSV, every field double-quoted, columns exactly: "current","to_replace"

The model may stop and ask you:
  - if the discipline is not evident from the manuscript and the choice of
    reporting verbs or hedging depends on it
  - if it cannot tell whether a citation reports a specific finding (past)
    or an enduring definition/theory/current position (present)

No session parameters (language variant, register) are set in this prompt.
-->

# CONLING — Citation Pattern Refinement Audit Prompt

## Job

Refine the mechanical citation phrasing flagged in `citation_patterns.csv`.
For every flagged citation where 50% or more of its uses share identical
phrasing, rewrite those instances so that sentence structures, openers and
phrasing vary, while the academic tone, the meaning and the clarity of
attribution stay intact. Then normalise the tense of the reporting verb
around each of those citations so that it is consistent across the manuscript.

The procedure — examining instances, the revision strategies, and the tense
rules — is in *Reference — Method*. Return one CSV of replacements (see
*What done looks like*).

---

## Why

The manuscript repeats the same citation phrasing again and again ("The data
of X showed...", "The findings of Y revealed..."). The repetition makes the
prose monotonous and reads as non-academic. The point of the pass is to give
the prose more varied, academically richer citation phrasing *without* costing
the manuscript any scholarly rigour or meaning.

That is why variation is always the lower priority: a rewrite that reads
better but blurs who found what, softens or strengthens a claim, or changes
when a study took place has defeated the purpose of the pass.

---

## Guardrails

### Academic standards

- Keep attribution precise. There must be no ambiguity about who found what.
- Preserve all original citations. Do not remove or consolidate any.
- Maintain the original meaning and nuance.
- Ensure grammatical correctness.
- Keep the tone appropriate to the discipline.

### Accuracy over variation

- If a variation requires even a subtle shift in meaning, note it clearly.
- If accuracy and variation conflict, prioritise accuracy.

### Tense

- Do not alter the temporal meaning of the original study. If the source
  describes an ongoing trend, use the past progressive ("was gaining") rather
  than the simple present.

### Scope

- Rewrite only the instances of citations flagged with `pattern_frequency`
  ≥ 50%.

### When to stop and ask

- **Inputs missing.** If `citation_patterns.csv` or the manuscript (with its
  paragraph labels) is not available, say so and wait. Do not work from a
  pasted excerpt unless the user confirms it is the complete scope.
- **Discipline cannot be told from the text.** If the manuscript does not make
  its discipline clear and the choice of reporting verbs or hedging depends on
  it, ask which conventions apply rather than assuming a default.
- **Tense call is genuinely unclear.** If you cannot tell whether a citation
  reports a specific study finding (past) or an enduring definition,
  established theory or current position (present), and the choice would
  change what the sentence claims, ask rather than guess.
- Proceed without asking on everything else — the strategies, the tense rules
  and the output format are settled by this prompt.

---

## What done looks like

Return **one CSV** with every field double-quoted and columns exactly:

```
"current","to_replace"
```

| Column | Content |
|---|---|
| `current` | The existing citation-bearing wording as it stands in the manuscript |
| `to_replace` | The varied, tense-normalised replacement |

Before returning the CSV, check that:

1. Every flagged citation with `pattern_frequency` ≥ 50% has had its
   dominant-pattern instances examined and rewritten.
2. No original citation has been removed or consolidated, and attribution is
   as clear as in the original.
3. Each replacement keeps the original meaning and nuance and is grammatically
   correct. Any subtle meaning shift is noted clearly.
4. Every instance of the same author/year uses one consistent reporting tense,
   applied to the reporting verb *and* the verbs inside the reported clause,
   with no change to the study's temporal meaning.

---

## Reference — Required inputs

### `citation_patterns.csv`

Columns:

- `citation`: Author et al. (Year)
- `count`: Number of times cited
- `dominant_pattern`: The repeated sentence structure (first 6 words)
- `pattern_frequency`: How many uses share the dominant pattern
- `locations`: Paragraph labels [N], [M], etc.
- `suggestion`: Consolidation recommendation

### Manuscript

Full text with paragraph labels [13] through [1326].

---

## Reference — Method

For each citation flagged with `pattern_frequency` ≥ 50%:

### Step 1 — Examine all instances

- Read all paragraphs containing that citation.
- Identify the mechanical pattern (e.g. "The data of [CITATION]
  showed/revealed/indicated").
- Note which instances use this pattern.

### Step 2 — Create varied alternatives

For each instance, choose from these revision strategies:

| Strategy | Example |
|----------|---------|
| Shift to active voice | "The data showed..." → "[CITATION] demonstrated..." |
| Use different verb | "...showed..." → "...confirmed/established/supported..." |
| Move citation within sentence | "[CITATION] revealed..." → "...according to [CITATION]" |
| Embed in dependent clause | "[CITATION] found that X" → "Based on [CITATION]'s findings, X" |
| Lead with finding, cite after | "X occurs because..." → "X occurs because [CITATION] documented..." |
| Academic hedging | "[CITATION] showed X" → "[CITATION] suggests X may..." |

### Step 3 — Maintain academic standards

See *Guardrails → Academic standards*.

### Step 4 — Flag trade-offs

See *Guardrails → Accuracy over variation*.

### Step 5 — Normalise tense consistency around citations

- Identify the reporting verb tense for each citation (e.g. "showed" = past,
  "shows" = present, "has shown" = present perfect).
- Check all instances of the same author/year across the manuscript.
- If you find a mixed pattern (past in one paragraph, present in another),
  standardise to the most appropriate tense:
  - **Use past tense** for reporting specific study findings, methods, or
    results ("Gosselin et al. (2016) indicated that...").
  - **Reserve present tense** only for enduring definitions, established
    theories, or current positions ("Braun and Clarke (2006) define thematic
    analysis as...").
- Apply the chosen tense consistently to both the reporting verb **and** the
  verbs inside the reported clause (e.g. change "showed that EWPs deliver" →
  "showed that EWPs delivered").
- Do not alter the temporal meaning of the original study — if the source
  describes an ongoing trend, use past progressive ("was gaining") rather than
  simple present.
