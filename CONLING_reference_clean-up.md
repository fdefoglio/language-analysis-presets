# CONLING Reference Clean-Up (Range R)

Model: Sonnet 5.5 (Extra). One chat for the whole range.

## Job
Clean the reference list [1327]–[1892] of the Parau thesis. Reference clean-up only: no language edits.

Inputs (attached):
- excerpt_1327-1892 (cut fresh: extract_range.py master.md 1327 1892 --margin 10)
- Parau_edit_instructions.md: §1.2, §1.3, range notes, comment-sheet standard
- Parau_CommentSheet_AUTHOR.tsv (check new questions against existing rows)

Tasks:
1. Delete the placeholder [1415] (Campos et al., 2022). It duplicates Sarmiento-Campos at [1767].
2. Remove duplicates. Keep one entry per pair: the one that matches the in-text citations and is the fuller entry. If unsure, log it instead of deciding.
   - Busetto [1411]/[1412]; Briceño [1403]/[1404]; Chen et al. [1437]/[1438]; Creswell 2018 [1452]/[1453]; Denny & Weckesser [1466]/[1467]; Sah & Li [1757]/[1759]; Vygotsky 1978 [1836]/[1838]
   - Dankwa-Apawu [1459], [1879], [1891]: keep one
   - Makalela 2022 [1629]/[1630] (with and without "a")
   - [1632] 2016a and [1627] 2016 are the same article; [1634] 2019a and [1628] 2019 are the same book
   Check year suffixes against the in-text citations before merging.
3. Delete the §1.2 entries: [1343], [1378], [1555], [1477], [1785], [1831], [1682], [1724], [1680], [1740], [1526], [1484], [1639].
   - Delete an entry only when its in-text citation is gone from the master. Report each as "confirmed" or "pending body removal".
   - [1639] Mardiana et al. 2022 has no in-text citation: delete.
   - [1555] Jiang 2022 goes; keep [1501] Fang, Jiang & Yang 2023.
4. Re-alphabetise [1869]–[1891]. Move Zhang et al. 2026 from [1474] (in the D section) to its alphabetical place. Output as a move list.
5. Year mismatches (§1.3): Baker 2001 vs 2011; Omidire & Ayob 2022 vs 2020. Confirm against the entry. Change the entry only if it is internally inconsistent. Otherwise log a REF-YEAR row with both values.
6. Typographic fixes (CSV):
   - [1775] "Teachersâ€™" → "Teachers’" (encoding damage)
   - [1527], [1718], [1335]: remove stray bold markers. [1527] gives the gloss twice; keep one.
   - [1658], [1676]–[1677]: remove double spaces; use Harvard style as in [1413] and [1697]
   - [1473], [1470], [1629]: "Available at: … [Accessed …]" (Harvard), only where the change is mechanical
   - [1507], [1830]: merge the translated title onto one line (house rule: no manual line breaks)
7. Log, do not fix:
   - [1705] truncated entry "Obilor, E., & , I., 2023": second author missing
   - [1829] drafting note "[Volume/issue not specified]"
   - [1366] "Arslan, Y., 2023. (n.d.)": year and n.d. together
   - [1456] Cummins 2007, [1514] García & Kleyn 2016: missing publisher or journal
   - [1629] "Available on Google Books": no URL or date

## Why
The reference list must match the body before the thesis goes to the author and the examiners. Duplicates, orphan entries, encoding damage and mixed styles are the problems the author cannot see. Every change must leave the in-text citations intact, because the body is not edited in this pass.

## Guardrails
- Edit range [1327]–[1892] only. Context paragraphs are read-only. Never change, add or remove a [n] label. Do not touch the annexures ([1893] onward).
- Do not edit in-text citations; they sit in the body.
- No language edits. The L1 screen of this range found nothing to fix.
- Do not create a reference entry from memory or by web search. Anything missing goes to the AUTHOR sheet as REF-MISSING.
- Do not change titles, journal names or author names; they are third-party text.
- Do not apply teachers → educators to titles. Flag for a source check: [1861] "among educators of Chinese" vs [1474] "among teachers of Chinese"; [1866] "ESL educators' use" vs [1650] "ESL teachers' use"; [1710] "Educators' and students'" vs [1890] "teachers' and students'".
- Do not resolve a REF-YEAR or REF-MISSING row without checking the source.
- Do not delete a §1.2 entry while its in-text citation remains.

## Done means
1. Summary table: label | action | reason | in-text status (confirmed / pending body removal / n/a).
2. Paragraph actions (delete, move, re-sort) as a list for hand application. csv_to_md.py cannot empty or move a paragraph.
3. CSV (downloadable, UTF-8, all fields quoted, header current,to_replace): in-paragraph text fixes only. `current` is verbatim from the EDIT RANGE and occurs once in the excerpt. `to_replace` is never empty. No [n] labels or # marks.
4. AUTHOR sheet block (four columns: "", Position, Issue, Comment), with [ref n] at the end of each Comment. Categories: REF-MISSING, REF-YEAR, SOURCE-NEEDED, DATA, QUOTE, CONTENT, TERM, ADMIN.
5. EDITOR sheet block (same four columns), category REF-CLEANUP for everything the editor did (duplicates removed, entries deleted, sorting, typographic fixes), and PENDING-AUTHOR for anything waiting on Ricky. Never sent to the author.

Then: csv_to_md.py on the excerpt → merge_range.py → check_master.py against master_baseline_2026-10-06.md. Apply the paragraph actions by hand, then rerun check_master.py.
