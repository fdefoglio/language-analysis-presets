# CONLING Citation Pattern Refinement Audit

## Task
Refine mechanical citation patterns to create more varied, academically rich prose while maintaining scholarly rigor and meaning.

## Context
The manuscript exhibits repetitive citation phrasing ("The data of X showed...", "The findings of Y revealed...") that creates monotonous, non-academic prose. Your task is to:

1. Examine each flagged citation pattern in `citation_patterns.csv`
2. For citations with 50%+ of uses sharing identical phrasing, rewrite those instances
3. Vary sentence structures, openers, and phrasing while preserving academic tone
4. Ensure no loss of meaning or attribution clarity
5. Normalize tense consistency around citations

## Input Files

### citation_patterns.csv
Shows:
- `citation`: Author et al. (Year)
- `count`: Number of times cited
- `dominant_pattern`: The repeated sentence structure (first 6 words)
- `pattern_frequency`: How many uses share the dominant pattern
- `locations`: Paragraph labels [N], [M], etc.
- `suggestion`: Consolidation recommendation

### Manuscript
Full text with paragraph labels [1] through [336]

## Instructions

### For each citation flagged with pattern_frequency ≥ 50%:

**Step 1: Examine all instances**
- Read all paragraphs containing that citation
- Identify the mechanical pattern (e.g., "The data of [CITATION] showed/revealed/indicated")
- Note which instances use this pattern

**Step 2: Create varied alternatives**
For each instance, choose from these revision strategies:

| Strategy | Example |
|----------|---------|
| Shift to active voice | "The data showed..." → "[CITATION] demonstrated..." |
| Use different verb | "...showed..." → "...confirmed/established/supported..." |
| Move citation within sentence | "[CITATION] revealed..." → "...according to [CITATION]" |
| Embed in dependent clause | "[CITATION] found that X" → "Based on [CITATION]'s findings, X" |
| Lead with finding, cite after | "X occurs because..." → "X occurs because [CITATION] documented..." |
| Academic hedging | "[CITATION] showed X" → "[CITATION] suggests X may..." |

**Step 3: Maintain academic standards**
- Keep precise attribution (no ambiguity about who found what)
- Preserve all original citations (don't remove or consolidate)
- Maintain the original meaning and nuance
- Ensure grammatical correctness
- Keep discipline-appropriate tone

**Step 4: Flag trade-offs**
- If variation requires subtle meaning shift, note it clearly
- Prioritize accuracy over variation if there's conflict

**Step 5: Normalize tense consistency around citations**
- Identify the reporting verb tense for each citation (e.g., "showed" = past, "shows" = present, "has shown" = present perfect)
- Check all instances of the same author/year across the manuscript
- If you find a mixed pattern (past in one paragraph, present in another), standardize to the most appropriate tense:
    - **Use past tense** for reporting specific study findings, methods, or results ("Gosselin et al. (2016) indicated that...")
    - **Reserve present tense** only for enduring definitions, established theories, or current positions ("Braun and Clarke (2006) define thematic analysis as...")
- Apply the chosen tense consistently to both the reporting verb AND the verbs inside the reported clause (e.g., change "showed that EWPs deliver" → "showed that EWPs delivered")
- Do not alter temporal meaning of the original study — if the source describes an ongoing trend, use past progressive ("was gaining") rather than simple present

## Output Format

Create a CSV with columns:
"current","to_replace"