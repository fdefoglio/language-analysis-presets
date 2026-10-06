# CONLING comment sheet — standard (all academic editing)

Template: `CONLING_CommentSheet_TEMPLATE.tsv`. Every comment sheet uses exactly this structure, with no extra or renamed columns.

## File format

- Tab-separated (`.tsv`), UTF-8 with BOM, so it opens correctly in Excel.
- Every field is enclosed in double quotes. A double quote inside a field is doubled (`""`).
- One header row, exactly: `""	"Position"	"Issue"	"Comment"`. The first header cell is empty.
- One row per issue, numbered 1, 2, 3 … in the first column.

## Columns

| Column | Content |
|---|---|
| `""` (no name) | Running row number. |
| `Position` | Where it is, in a form the reader can find: the section number plus a short verbatim quote, e.g. `§2.7.2, para 3: "…Dolatabad et al., 2022…"`. Several places are separated by ` \| `. In the version sent to the author, the page number comes first: `p. 54, §2.7.2, para 3: "…"`. For documents without section numbers (e.g. reports), use page and paragraph: `p.11, para 2`. |
| `Issue` | `[CATEGORY] short label`, e.g. `[REF-MISSING] McKinney (2017)`. |
| `Comment` | What the problem is and exactly what is needed from the reader, as a question or request. While editing, end with `[ref n]`: the paragraph label(s) of the working Markdown. |

## Two sheets per job

| Sheet | Reader | Contains |
|---|---|---|
| `<Client>_CommentSheet_AUTHOR.tsv` | The author | **Only** items the editor has no authority to resolve: missing or conflicting reference details, data that contradict tables, content placement, quotations to check against transcripts, titles, captions and terms only the author can decide, administrative items (annexures, receipts). Written to the author, in plain language. |
| `<Client>_CommentSheet_EDITOR.tsv` | The editor (internal) | Processing reminders, pipeline decisions, fixes within the editor's authority, items waiting on an author reply. **Never** sent to the author, and nothing from it is copied into the author sheet. |

Anything the editor may fix freely is fixed, not queried. If a fix needs the author's approval or information, it goes in the AUTHOR sheet.

## Paragraph labels and page numbers

1. While editing, every row ends with `[ref n]`, the label of the paragraph in the current working Markdown (editor_tool export). If labels shift (re-export, structural changes), remap them.
2. Labels stay until the edit is complete.
3. At delivery, the AUTHOR sheet is converted: page numbers from a PDF of the final document exported from Word go into `Position`, and the `[ref n]` tags are removed. The EDITOR sheet keeps its labels.

## Issue categories

AUTHOR sheet: `REF-MISSING` (cited, not in the list) · `REF-YEAR` (year, author or spelling conflict between text and list; duplicate entries with different years) · `SOURCE-NEEDED` (a statement left without support) · `DATA` (text vs tables or data) · `QUOTE` (participant quotation to verify) · `CONTENT` (placement, structure, titles, captions) · `TERM` (terminology the author must choose) · `ADMIN` (annexures, receipts, front matter).

EDITOR sheet: `PIPELINE` · `REMAP` · `REF-CLEANUP` · `ACR-DEF` · `TERM` · `STRUCTURE` · `CHECK` · `LOCKED` (non-negotiable house rule) · `PENDING-AUTHOR` (editor action waiting on an author reply).

New categories are added here first, never invented per job.

## Return and finalisation (AUTHOR sheet)

1. The author adds a fifth column, `Remarks`, with an answer per row. The remark is the instruction.
2. At finalisation the editor appends `Status` (`Implemented` · `Implemented — author query` · `Implemented editorially` · `Flagged — no change`) and `Implementation note` (what was done, where).
3. Fixes found outside the sheet during finalisation are appended as rows `E1`, `E2`, …

The first four columns are never edited or reordered after the sheet is sent.
