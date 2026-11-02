# CONLING_DEDUP_Proposal

Flag-only DEDUP consolidation proposal for a thesis or dissertation edit. Produces three deliverables: comment-sheet rows, a unified `.diff` against the editor_tool export (the apply-source), and a supervisor-facing `.docx` memo in simulated track-changes style. Nothing is applied to the thesis; approval authority sits with the supervisor(s), and their per-item decisions are recorded in §1 of the job's edit-instructions file before any pass applies a change.

Run this only when a DEDUP is explicitly requested for the job.

---

## Job

For the named thesis, identify cross-section duplication in the body chapters, decide for each duplication cluster where the single full statement belongs, rewrite every echo as a brief mention with a cross-reference (or condense it to the material only it contributes), and deliver:

1. One `[CONTENT]` row per cluster on the Author comment sheet, plus one `[PENDING-AUTHOR]` row on the Editor sheet.
2. `claude/<Student>_DEDUP_proposal.diff` in the project: the exact apply-source, revisioned (`rev1`, `rev2`, …).
3. `<Student>_DEDUP_proposal.docx`: a memo the editor can forward to the supervisors unmodified, showing each change in revision markup with references the supervisors can find in their own copy.

## Why

Supervisors must approve deletions of their student's text, and they read the thesis as a Word document, not as a labelled export. The editor needs a machine-applicable record of the exact proposed wording, item by item, so that approved items can be applied later without re-deciding anything. Splitting the deliverable in two (diff for the pipeline, memo for the supervisors) serves both readers; the comment-sheet rows keep the audit trail inside the job.

## Guidelines

### Scope

- Work on the editor_tool export (labelled Markdown). Scan the Summary and the body chapters; exclude front matter, the reference list and annexures.
- A cluster is the same point, finding, caveat or mechanism stated **in full** in two or more places. Typical shapes: a cited empirical finding retold per section; a criteria list repeated wherever the topic recurs; a methodological disclaimer appearing in the literature review, methodology and limitations; a caveat group repeated through one results section; the same conclusion drawn twice within one subsection. Confirm each cluster by searching for its distinctive phrases and collect every `[n]`.
- Leave alone: the final chapter's summary sections (a summary restates its material by nature); signposting at chapter openings and closings; restatement the supervisor asked for; verbatim quotations. Name these exclusions in the memo so the supervisors see they were considered.

### Canonical statement and echoes

- The full statement stays where the point belongs to the argument: where it is the topic, or the first full treatment with its citations. Keep that paragraph unchanged, or only lightly smoothed. Where two homes are defensible (concept in the literature review plus a model-specific statement in the methodology), say so and let the supervisor choose.
- Each echo becomes a one-clause mention with a cross-reference ("as explained in Section x.x.x", "discussed further in Section x.x.x", "see Section x.x.x"), or is condensed to the material only that paragraph contributes. No content may be lost: every point remains stated in full exactly once.

### Rewrite checks (verify every rewritten paragraph against all eight)

1. Antecedent: a replacement such as "This deduction…" needs its referent named earlier in the paragraph.
2. No self-references: never "(see Section x.x.x)" from inside Section x.x.x; use "as explained above" or nothing.
3. No dangling connectives: deleting a premise strands its "therefore / consequently / however"; recast.
4. Condensing keeps the NEW material: cut the part duplicated elsewhere, keep the mechanism or evidence unique to that paragraph, never the reverse.
5. Preserve bridges: if the next paragraph builds on a deleted sentence's conclusion, keep a short bridge sentence.
6. Keep citations with findings: when a specific cited finding is invoked, keep "(Author, Year)" even alongside the cross-reference, and do not let a trim turn a hedged, cited claim ("may") into an unsourced stronger one ("often").
7. Hedging and claim scope stay exactly as the author had them.
8. Cross-reference direction: forward pointers from early mentions, backward references from later ones; a one-sentence recap with a cross-reference is acceptable in a results chapter.

### Hard rules

- Never change, add or remove a `[n]` label. Keep every `⟦N|…⟧` token exactly once in its paragraph. Do not touch `[SPECIAL]` lines or TABLE blocks.
- Stray formatting debris (`**`, double stops) inside affected paragraphs is not fixed here: leave it in the diff text and say in the memo that mechanical matters are handled separately.

### Comment-sheet rows

- Author sheet, one row per cluster: Position = `§<section>, para <n>: "…verbatim quote…"` joined with ` | `; Issue = `[CONTENT] DEDUP proposal: <short label>`; Comment = what repeats, the proposed location of the full statement, where each echo becomes a cross-reference, "pending supervisor approval", ending `[ref n, n…]`.
- Editor sheet, one `[PENDING-AUTHOR]` row: rows filed, nothing applied until decisions land in §1 of the instructions file, what was deliberately not flagged, labels need REMAP after step-0 renumbering, and which diff revision is the apply-source.

### Producing the files

Use the scripts in `tools/`:

1. Fill `tools/proposals_TEMPLATE.json` (copy it to the job) with the metadata and, per item, the label, motivation, the retained-statement note, and the full proposed text of every changed paragraph keyed by `[n]`.
2. `python tools/make_dedup_outputs.py <export.md> <proposals.json>` writes the `.diff` and `memo.json` (word-level diff runs, references by section and opening words, Markdown markers stripped).
3. `node tools/build_memo.js` writes the `.docx` from `memo.json`.

### Memo content and style

- Structure: title block (title, student and thesis line, "Prepared by CONLING Language and Translation Consultants · date · Status: proposal only; no change has been applied to the thesis"); Purpose and approach; a legend (deleted text struck through in red, inserted text underlined in blue, unchanged plain); one numbered section per cluster with **Motivation:** and **Retained in full:** lines followed by each changed paragraph as a caption (`Section x.x.x, paragraph beginning "<first words>…"`) and the full word-level diff; a closing "Next step" section asking for per-item decisions and noting that items are independent.
- References by section number and opening words only; `[n]` labels never appear in the memo.
- Revision markup is simulated formatting, not Word tracked changes: the memo is not the thesis, so nothing in it should be acceptable as a revision.
- House style, so the memo reads as the editor's own writing: plain en-GB editorial prose; no em dashes (use commas, colons or parentheses); no "Why:"-style labels (the fixed labels are Motivation and Retained in full); no filler vocabulary (delve, crucial, comprehensive, robust, seamlessly, moreover-chains); no rhetorical triplets; sentences a working editor would write. Check the finished text for these before delivery.

## Done means

- The rendered `.docx` has been converted to images and read page by page: legend correct, every diff paragraph legible, every rewrite passes the eight checks, no em dashes or label leftovers.
- Both files delivered to the editor; the `.diff` saved to the project under `claude/`; comment-sheet rows posted.
- Job records updated: a pending DEDUP slot in §1 of the instructions file ("apply only approved items, from the revN diff"), a running-log row (what was proposed, which revision, labels need REMAP after step-0 renumbering).
- The supervisors can decide per item from the `.docx` alone, and a later session can apply approved items from the `.diff` alone.
