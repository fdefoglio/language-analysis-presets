# CONLING comment sheet — standard (all academic editing)

Template: `CONLING_CommentSheet_TEMPLATE.tsv`. Every working comment sheet uses exactly this structure, with no extra or renamed columns. The AUTHOR sheet is kept tidy with `CONLING_comment_sheet_tidy.py` while editing, and is delivered as a grouped workbook (see "Keeping the AUTHOR sheet tidy" and "Delivery").

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

## Keeping the AUTHOR sheet tidy

Author sheets can grow to 50 rows or more. A sheet that long discourages the author from answering, and it tempts the editor to put off dealing with it. So the AUTHOR sheet is tidied while the work goes on, not at the end:

```
python CONLING_comment_sheet_tidy.py tidy <Client>_CommentSheet_AUTHOR.tsv
```

**When to run it:**
- after each editing phase;
- whenever the editor asks to tidy the comment sheet;
- always before delivery.

**What it does:**
- **Duplicates:** rows with the same category and the same request are merged. Positions are joined with ` | `, and the `[ref n]` tags are combined.
- **Same subject:** rows with the same category and the same Issue label are merged. Only sentences not already in the kept comment are added.
- **Order and numbering:** rows are put in theme order, then document order, and renumbered.
- **Clusters:** rows that ask for the same thing about different subjects are listed in `<sheet>_tidy_report.md`. Ten entries without page ranges is a typical cluster.
- **Routing check:** an editor-only category in the AUTHOR sheet stops the run. That row belongs in the EDITOR sheet.

**Consolidating a cluster.** Merge each cluster into one row with `merge --rows …`:
- one Issue that names the pattern;
- one request;
- every subject listed with its position.

The script keeps all positions and `[ref n]` tags.

**The merge log.** Every merge is recorded in `<sheet>_merge_log.tsv`, which keeps each original row in full. Merges can therefore be undone, and an author answer can be traced back to every place it covers.

**The aim:** one row per decision the author has to make, not one row per place in the text.

## Paragraph labels and page numbers

1. While editing, every row ends with `[ref n]`, the label of the paragraph in the current working Markdown (editor_tool export). If labels shift (re-export, structural changes), remap them.
2. Labels stay until the edit is complete.
3. At delivery, the AUTHOR sheet is converted: page numbers from a PDF of the final document exported from Word go into `Position`, and the `[ref n]` tags are removed. The EDITOR sheet keeps its labels.

## Delivery: the grouped author workbook

The AUTHOR sheet goes to the author as an Excel workbook, not as a single list:

```
python CONLING_comment_sheet_tidy.py build <Client>_CommentSheet_AUTHOR.tsv -o <Client>_CommentSheet_AUTHOR.xlsx --deliver --title "<document title>"
```

**Sheets:**
- **Overview:** how to answer, plus the number of questions in each group.
- **One sheet per theme, in this order:**
  - **References** (`REF-MISSING`, `REF-YEAR`), IDs R1, R2 …
  - **Sources and evidence** (`SOURCE-NEEDED`), IDs S1 …
  - **Data and content** (`DATA`, `CONTENT`), IDs D1 …
  - **Quotations** (`QUOTE`), IDs Q1 …
  - **Terms and administration** (`TERM`, `ADMIN`), IDs T1 …

  A sheet appears only if it has rows.

**Columns on each theme sheet:** `ID`, `Position`, `Issue`, `Comment` and a shaded `Remarks` column for the author's answer.

**`--deliver` mode:**
- removes the `[ref n]` tags and the `[CATEGORY]` prefix, since the sheet name already shows the group;
- stops with a warning if a Position still has no page number.

The working TSV and the EDITOR sheet stay as they are.

## Issue categories

AUTHOR sheet: `REF-MISSING` (cited, not in the list) · `REF-YEAR` (year, author or spelling conflict between text and list; duplicate entries with different years) · `SOURCE-NEEDED` (a statement left without support) · `DATA` (text vs tables or data) · `QUOTE` (participant quotation to verify) · `CONTENT` (placement, structure, titles, captions) · `TERM` (terminology the author must choose) · `ADMIN` (annexures, receipts, front matter).

EDITOR sheet: `PIPELINE` · `REMAP` · `REF-CLEANUP` · `ACR-DEF` · `TERM` · `STRUCTURE` · `CHECK` · `LOCKED` (non-negotiable house rule) · `PENDING-AUTHOR` (editor action waiting on an author reply).

New categories are added here first, never invented per job.

## Return and finalisation (AUTHOR sheet)

1. The author answers in the `Remarks` column of each sheet. The remark is the instruction. `CONLING_comment_sheet_tidy.py remarks <workbook>.xlsx -o <Client>_CommentSheet_AUTHOR_returned.tsv` turns the returned workbook back into one TSV (`ID`, `Position`, `Issue`, `Comment`, `Remarks`) for finalisation. A remark on a merged row applies to every position it lists; the merge log shows the original rows.
2. At finalisation the editor appends `Status` (`Implemented` · `Implemented — author query` · `Implemented editorially` · `Flagged — no change`) and `Implementation note` (what was done, where).
3. Fixes found outside the sheet during finalisation are appended as rows `E1`, `E2`, …

`ID`, `Position`, `Issue` and `Comment` are never edited or reordered after the workbook is sent.
