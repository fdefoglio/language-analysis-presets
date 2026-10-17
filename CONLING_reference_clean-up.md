# CONLING Reference Check (Agrekon, Range R)

Model: Sonnet 5.5 (Extra). One chat for the whole range.

## Job
Check the reference list [120]–[183] of the Agrekon article (Gimo and Jordaan) against the body. Reference check only: no language edits, no changes to the reference format, no changes to body text.

Inputs (attached):
- Revised Paper1 Gimo and Danie_v0_for_ai.md: the full current master, read-only context for matching reference entries to in-text citations
- ref_audit_report.txt: the output of ref_audit.py. Verify each finding against the master before reporting it.
- Agrekon_edit_instructions.md: the rules file
- The AUTHOR sheet: check new questions against existing rows

## Tasks
1. Verify the audit report. For each finding, confirm it against the master and mark it "confirmed" or "not confirmed". Do not report an unconfirmed finding as a fault.
2. Malformed italics: check [121], [134], [155] and [181]. Describe each one, so the XML fix is clear.
3. Stray comma: check [179].
4. Citation match: for each in-text citation in [0]–[119] that should have an entry in [120]–[183], confirm the entry exists. For each entry in [120]–[183], confirm at least one in-text citation points to it. Report any mismatch in either direction.
5. Year suffixes: check that the year and any letter suffix (2016a, 2019b, and so on) in each in-text citation matches its entry.
6. Duplicates: if two entries look like the same work, report the pair with both labels. Do not decide which to keep. Log it.
7. Missing details: note any entry without a publisher, journal, volume or URL where the house format needs one. Do not supply it.

## Why
The reference list is a Word field structure, like a table of contents, so it cannot be fixed in the Markdown. Findings go to the EDITOR sheet with a note that the fix is made in the XML at hand-off. The body must match the list before the article goes back to the author.

## Guardrails
- Check range [120]–[183] only. Labels [0]–[119] are read-only context.
- Never change, add or remove a [n] label.
- Do not return a CSV. Do not propose changes to the reference list in the Markdown.
- Do not create a reference entry from memory or by web search. If a citation has no entry, say so and log it. Do not write the entry.
- Do not change titles, journal names or author names. They are third-party text.
- Do not resolve a year mismatch by guessing. Report both values and the source of each.
- Do not change the reference format. The house format is still open (handover section 9, item 4).
- Do not repeat items already on the AUTHOR sheet, including the uncited references and the Cochran and Greenacre year queries.
- No first person. No inline comments.

## Done means
1. Summary table: label | issue | status (confirmed / not confirmed) | in-text status (matched / unmatched / n/a).
2. EDITOR sheet block, four columns: "", Position, Issue, Comment. Each Comment ends with [ref n] and the words "fix in XML at hand-off". Category REF-CHECK for every item.
3. A short list of anything that needs Frans's decision, such as a possible duplicate or a house-format question. Do not add these to the AUTHOR sheet. Frans decides whether they go there.
