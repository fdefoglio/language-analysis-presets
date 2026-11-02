# CONLING_DEDUP

Template for the flag-only DEDUP consolidation proposal used in thesis and dissertation edits (CONLING Track A). Run it only when a DEDUP is explicitly requested for the job; supervisor approval is required before anything is applied.

| File | What it is |
|---|---|
| `CONLING_DEDUP_Proposal.md` | The protocol (JWGD form): scope, exclusions, the eight rewrite checks, comment-sheet rows, deliverable specifications and the memo house style. |
| `tools/proposals_TEMPLATE.json` | Copy per job and fill in: metadata plus, per item, the label, motivation, retained-statement note and the full proposed text of every changed paragraph, keyed by `[n]`. |
| `tools/make_dedup_outputs.py` | `python make_dedup_outputs.py <export.md> <proposals.json>` writes the `.diff` (apply-source) and `memo.json`. Refuses missing labels, unchanged paragraphs and em dashes. |
| `tools/build_memo.js` | `node build_memo.js <Student>_DEDUP_proposal.docx` builds the supervisor memo from `memo.json` (requires the `docx` npm package; available in Claude sessions). |

Deliverables per job: `claude/<Student>_DEDUP_proposal.diff` in the Claude project, `<Student>_DEDUP_proposal.docx` for the supervisors, and the comment-sheet rows described in the protocol. Verify the rendered memo page by page before delivery.

First used on the Mia Louw MSc edit (October 2026); the eight rewrite checks come from the defects corrected in that job's first revision.
