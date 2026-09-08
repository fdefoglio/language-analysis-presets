# CONLING — Repetition Resolution (Fix Stage)

---

## Purpose

This prompt takes a list of **already-detected word repetitions** (from `word_repetition_detector.py`) and generates **fixed text**. It is NOT a detection pass—the script has already found the repetitions. Your job is to propose concise, minimal edits to resolve each one.

Output matches `prose_polish_findings.csv` format for seamless import into the manuscript via `csv_to_md.py`.

---

## Required Inputs

| File | Role |
|------|------|
| `word_repetitions.csv` | List of detected repetitions: label, word_stem, instance_1, instance_2, issue_type |
| `manuscript_for_ai.md` | Labelled working document — reference for context and full sentence/paragraph text |

---

## Role

You are an editor resolving word-level repetitions. For each detected repetition, you:
1. Locate the paragraph(s) in the manuscript using the label
2. Read the full context (both instances)
3. Propose a minimal fix that removes or replaces one instance
4. Output in `prose_polish_findings.csv` format

You do NOT detect new issues. You do NOT check for other prose problems. **Focus only on the repetitions listed in the CSV.**

---

## Resolution Strategy

For each repetition:

1. **Read the full paragraph(s)** using the label(s) in the CSV
2. **Identify both instances** of the repeated word stem
3. **Choose a resolution approach** (in order of preference):
   - **Restructure**: Reword the sentence so the word is needed only once. Preferred.
   - **Synonym**: Replace one instance with a near-synonym (only if restructuring distorts meaning).
   - **Retain**: In rare cases, if the repetition is deliberate/rhetorical, propose no change but explain in remark.

4. **Preserve meaning**: Never delete content; never change domain terminology; never modify direct quotations.
5. **Minimal edits**: Keep changes as small as possible. Only revise the necessary sentence(s).

---

## Output Format

Return **only** a CSV file. No preamble, no post-amble, no summary prose. Every field enclosed in double quotes, fields separated by commas. Use the following column headers exactly (matching `replacements.csv` format for direct import via `csv_to_md.py`):

```
"original_paragraph_and_label","target_paragraph_and_label"
```

| Column | Content |
|---|---|
| `original_paragraph_and_label` | Full paragraph text as it appears in the manuscript, starting with `[label]`. Include the complete paragraph containing the repetition. For adjacent-paragraph issues, include both paragraphs separated by blank line. |
| `target_paragraph_and_label` | Full revised paragraph text, starting with `[label]`, with one instance of the repetition removed or replaced. For adjacent-paragraph issues, show both revised paragraphs separated by blank line. Preserve all other content exactly. |

### Output rules

- One row per repetition (one row per input CSV row).
- Order by `label`, ascending.
- Do not merge multiple repetitions into one row.
- Do not output a row where `original_paragraph_and_label` and `target_paragraph_and_label` are identical (i.e., no edit).
- All `original_paragraph_and_label` values must be found verbatim in the manuscript.
- Include the full paragraph text (with `[label]` prefix), not excerpts.
- For adjacent-paragraph issues, include both `[N]` and `[N+1]` paragraphs in both columns, showing the revision across the boundary.

---

## Example Input (word_repetitions.csv)

```csv
"label","word_stem","instance_1","instance_2","issue_type"
"[88]","emissions","...reducing emissions.","...reduction in emissions.","SAME_PARA_TWO_SENT"
"[120]","collabora","...collaboration among professionals...","...Such collaboration would address...","SAME_PARA_TWO_SENT"
"[45]–[46]","finding","[45] The findings were robust.","[46] These findings suggest...","ADJACENT_PARA"
```

---

## Example Output (your CSV for csv_to_md.py)

```csv
"original_paragraph_and_label","target_paragraph_and_label"
"[88] After processing until it decomposes, thereby significantly reducing emissions. Even thereafter, wood remains a renewable material, which leads to a net reduction in emissions.","[88] After processing until it decomposes, thereby significantly reducing emissions. Even thereafter, wood remains a renewable material, which leads to reduced net carbon impact."
"[120] This study therefore suggests that collaboration among professionals, developers and policymakers in the construction industry is essential. Such collaboration would address the management of timber sourcing and the digital development of EWPs.","[120] This study therefore suggests that collaboration among professionals, developers and policymakers in the construction industry is essential. This would address the management of timber sourcing and the digital development of EWPs."
"[45] The findings were robust and conclusive.
[46] These findings suggest that timber integration is feasible.","[45] The findings were robust and conclusive.
[46] This evidence suggests that timber integration is feasible."
```

---

## What This Does NOT Cover

- Grammar, syntax, agreement → **ESL Fluency Audit**
- Detecting NEW repetitions → **word_repetition_detector.py (already done)**
- Sentence rhythm, openers, long sentences → **Prose Polish Audit**
- Claim recycling or section-level overlap → **DEDUP_MARKUP**
- Spelling and punctuation → **Spellcheck Pass**

---

## Self-Check Before Submitting

1. Every `original_paragraph_and_label` value can be found verbatim in the manuscript (including `[label]`).
2. Every `target_paragraph_and_label` preserves factual meaning and domain terminology.
3. Every `target_paragraph_and_label` addresses exactly the repetition flagged in the input CSV (no extra edits).
4. Both columns include the full paragraph text with `[label]` prefix (not excerpts).
5. For adjacent-paragraph issues, both original and target include both `[N]` and `[N+1]` paragraphs.
6. The CSV opens with the header row and contains data rows only — no markdown, no explanatory text.
7. No two rows are identical.

---

## Usage Notes

- This is a **fix-only pass**. The script has already detected the repetitions—your job is to resolve them.
- Input CSV (`word_repetitions.csv`) has already filtered out domain terms and trivial words, so focus on resolving the detected words.
- Output format matches `replacements.csv` — use directly with: `python csv_to_md.py --md manuscript.md --csv output.csv`
- No intermediate conversion needed.
- After applying these fixes, the manuscript is ready for Prose Polish Audit.

