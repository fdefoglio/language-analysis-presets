# CONLING — Acronym Audit (Fix Stage)

## Job

Resolve a list of **already-detected acronym breaches** in a labelled manuscript. The list comes from
`acronym_worklist.py`, which has read the whole thesis: each item is one place where the acronym rules
are not met, together with the facts you need about the rest of the thesis (the unit, the List of
Acronyms' expansion, where the first prose mention or the definition is).

For each item, read the paragraph, decide what the rule requires, and record the result as one finding:
a minimal edit, an Author or Editor row, or a reasoned decision that the item is not an error.

This is a fix-only pass. Detection has already happened, so do not look for new acronym problems or other
prose problems: if something else catches your eye, put it in the notes file for the pass that owns it.
In the CONLING thesis pipeline this pass runs after Passive-to-Active, on the post-P2A manuscript.

---

## Why

Acronyms are checked per unit (the Summary and each chapter), and a unit usually runs across several
ranges of the manuscript. You see one range, so you cannot tell where the first mention in the unit is.
The script can, and it has put that fact in each item. Your job is the judgement the script cannot make:
whether the place is exempt, what the correct expansion is, and whether the fixed sentence still reads
naturally.

The editor reviews every change as a diff, so the value of the pass is precision. A fix changes the
acronym or its expansion and nothing else.

---

## Categories

The category of a finding is the item's `issue_type`:

- **ACR-UNEXPANDED** — the first prose mention in the unit is not "Full name (ABBR)".
- **ACR-REEXPAND** — "Full name (ABBR)" appears again after the unit's first mention.
- **ACR-BARE** — the bare full name is used after the acronym was defined in the unit.
- **ACR-HEADING** — the acronym stands in a heading or caption, which carry the expanded form only.
- **ACR-VARIANT** — the text defines the acronym with wording that differs from the List.
- **ACR-LIST** — a problem in the List of Acronyms itself.

---

## The rules

- **Units:** the Summary (abstract) and each chapter. The List of Acronyms and the front matter are not units.
- **First mention:** the first mention in running prose of the unit is "Full name (ABBR)". Every later mention
  in the unit is the acronym alone, and a bare full name after the definition becomes the acronym.
- **Headings and captions** at every level carry the expanded form only, never the acronym, and never count
  as the first mention: the first running-prose mention after them is expanded even when a heading just above
  already spells the name out.
- **Exempt places** (never counted as the first mention, never expanded or contracted): in-text citations with
  the acronym as author ("(WTO, 2016)", "FAO (2025)"), Source and Note lines, table cells, equations and
  equation legends, direct quotations, and titles of Acts and regulations. The script already skips most of
  them; if an item still sits in one, it is not an error.
- **Expansion text** follows the thesis's own form; official names keep their official spelling. When the List
  and the text disagree, report both (ACR-VARIANT) and change neither.

---

## Guardrails

### Preservation (these always hold)

- A fix touches the acronym and its expansion only. Do not reword the sentence, split or merge it, change a
  citation, a number, a term or a quotation, or move an expansion for any other reason.
- Keep "Full name (ABBR)" intact in the form the List gives it, with the article and number the sentence
  already has ("the Standard Error" becomes "the SE" only if the sentence still reads naturally; otherwise
  the finding is Amber).
- An added expansion must not push the sentence over 34 words, and must not leave a sentence opening with
  This, These, There or a vague It. If it would, give the fix and the alternative in the Remark.
- Never use a first- or second-person pronoun.
- Never edit protected text: the title page, the Declaration, direct quotations.

### Resolution, by item type

- **ACR-UNEXPANDED.** Where `label_2` is empty, replace the bare acronym at `label` by "Full name (ABBR)".
  Where `label_2` is set, the full name stands at `label` as the unit's first prose mention without its
  acronym, and the acronym is used from `label_2`: add " (ABBR)" after the full name at `label`, and leave
  `label_2` alone. Take the expansion from the List unless the item says the text's wording differs.
- **ACR-REEXPAND.** Replace the second "Full name (ABBR)" by the acronym alone. If it is the only mention in
  its sentence, check that the sentence still reads naturally.
- **ACR-BARE.** Replace the bare full name by the acronym, keeping the article. If the full name there is part
  of a longer term or a defined heading-like label, or the replacement would put the acronym twice in one
  sentence, report it as not an error or as Amber with the reason.
- **ACR-HEADING.** Replace the acronym by its expanded form. Keep the heading's casing convention (Title
  Case for chapter and level-2 headings, sentence case below; captions as written).
- **ACR-VARIANT.** Report both wordings in the Remark; Action editor; no edit.
- **ACR-LIST.** The List's entries are single paragraphs. You may correct the wording inside one entry (for
  example a missing word in an expansion, when the text defines it in full elsewhere). You may not add or
  remove an entry: report a missing or unused entry with Action editor (the Word phase does it) and say which
  it is. An entry whose expansion does not spell its acronym: check the text's own definition; if the text
  gives the full wording, correct the entry (Amber); if not, Action author with a plain question to the
  student. An acronym used only in tables or exempt places is a judgement for the editor (Action editor).
- **Not an error** (an exempt place, or the script misread the text): one row with Action none and the
  reason in the Remark. Every item still gets a row.

### Scope

You see one range, and the work list holds the only items you resolve. Stay inside the EDIT RANGE fence.
If you notice something the work list does not show, write it in the notes file with its `[n]` label.

---

## What done looks like

A findings table with one row per work-list item, columns:

| Column | Content |
|---|---|
| `id` | Your finding id (the run tells you the prefix). |
| `Location` | `§x.y, [n]`: section, then the label of the paragraph whose wording changes (the item's `label`). |
| `Original Text` | The words to be changed, copied exactly from paragraph `[n]`. For an item that is not an error, the acronym or full name as it appears. |
| `Category` | The item's `issue_type`. |
| `Severity` | Medium for ACR-UNEXPANDED, ACR-HEADING and ACR-VARIANT; Low for ACR-REEXPAND, ACR-BARE, ACR-LIST and every row that is not an error. |
| `Suggestion` | The replacement for `Original Text`. Empty when no edit is made. |
| `Remark` | Starts with the work-list id(s), e.g. `W12:`; then what you did or why not, in a few words. |

### Self-check before submitting

1. Every work-list item appears in exactly one row, named by its id at the start of the Remark.
2. Every `Original Text` is verbatim in the paragraph its Location names.
3. Every edit changes the acronym or its expansion only; quotations, citations, numbers and terms are as they were.
4. No expansion differs from the List's, unless the item says the text's wording differs (then no edit).
5. No fixed sentence is over 34 words or opens with This, These, There or a vague It.
6. No row raises anything that is not on the work list.

---

## Reference — Required inputs

| File | Role |
|------|------|
| Work list (the WORK LIST section of the range file) | Items to resolve: id, range, label, label_2, issue_type, stems (the acronym), sentence_1 (the sentence or entry at `label`), sentence_2 (the unit, the List's expansion, and what the script found) |
| Labelled manuscript (the range file) | Full paragraphs for context and verbatim text |
| List of Acronyms (a range's paragraphs, when it holds them) | The expansion for every acronym; also the item `sentence_2` |

---

## Reference — Worked example

**Work list:**

```csv
"id","range","label","label_2","issue_type","stems","sentence_1","sentence_2"
"W1","R02","91","","ACR-UNEXPANDED","ABC","The ABC applies to all sellers.","Unit: CHAPTER 2: LITERATURE REVIEW. List: Alpha Beta Council. First prose mention in the unit, not expanded."
"W2","R02","94","92","ACR-UNEXPANDED","XYZ","The Xylo Yield Zone covers the district.","Unit: CHAPTER 2: LITERATURE REVIEW. List: Xylo Yield Zone. The full name here is the first prose mention in the unit and is not followed by (XYZ); the acronym is used from [92]."
"W3","R02","95","","ACR-REEXPAND","ABC","Alpha Beta Council (ABC) rules were revised.","Unit: CHAPTER 2: LITERATURE REVIEW. List: Alpha Beta Council. Expanded again; first prose mention at [91]."
"W4","R02","97","","ACR-BARE","ABC","The Alpha Beta Council set the rate.","Unit: CHAPTER 2: LITERATURE REVIEW. List: Alpha Beta Council. The full name stands after the acronym was defined at [91]."
"W5","R02","99","","ACR-VARIANT","XYZ","The Xylo Zone (XYZ) was surveyed.","Unit: CHAPTER 2: LITERATURE REVIEW. List: Xylo Yield Zone. The text defines it with different wording."
```

**Findings:**

```csv
"id","Location","Original Text","Category","Severity","Suggestion","Remark"
"M1","§2.1, [91]","The ABC applies","ACR-UNEXPANDED","Medium","The Alpha Beta Council (ABC) applies","W1: expanded at the unit's first prose mention, List wording"
"M2","§2.1, [94]","The Xylo Yield Zone covers","ACR-UNEXPANDED","Medium","The Xylo Yield Zone (XYZ) covers","W2: defined at the full name; the acronym is used from [92]"
"M3","§2.1, [95]","Alpha Beta Council (ABC) rules","ACR-REEXPAND","Low","ABC rules","W3: second expansion in the unit removed"
"M4","§2.1, [97]","The Alpha Beta Council set","ACR-BARE","Low","The ABC set","W4: bare full name after the definition"
"M5","§2.2, [99]","The Xylo Zone (XYZ)","ACR-VARIANT","Medium","","W5: text says 'Xylo Zone', List says 'Xylo Yield Zone'; both reported, neither changed (Action editor)"
```
