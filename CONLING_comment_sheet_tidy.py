#!/usr/bin/env python3
"""CONLING comment sheet: keep the AUTHOR sheet tidy while editing, and build the grouped
author workbook at delivery. Companion to CONLING_CommentSheet_STANDARD.md.

Usage
  python CONLING_comment_sheet_tidy.py tidy    AUTHOR.tsv
  python CONLING_comment_sheet_tidy.py merge   AUTHOR.tsv --rows 3,7,12 --issue "[REF-MISSING] ..." --comment "..."
  python CONLING_comment_sheet_tidy.py build   AUTHOR.tsv -o <Client>_CommentSheet_AUTHOR.xlsx [--deliver] [--title "..."]
  python CONLING_comment_sheet_tidy.py remarks <Client>_CommentSheet_AUTHOR.xlsx -o AUTHOR_returned.tsv

tidy     Rewrites AUTHOR.tsv in place (standard format), after a backup (AUTHOR.tsv.bak):
         - merges exact duplicates (same category and the same request);
         - merges rows about the same subject (same category and the same Issue label);
           positions are joined with ' | ', [ref n] tags are combined, and only the
           sentences not already present are appended to the kept comment;
         - orders rows by theme, then by first position in the document;
         - renumbers 1, 2, 3 …
         Every merge is appended to AUTHOR_merge_log.tsv (the original row in full, so
         any merge can be undone and author answers map back to every position).
         Rows that ask for the same thing about different subjects (for example ten
         entries without page ranges) are listed in AUTHOR_tidy_report.md as clusters:
         the editor or agent consolidates each cluster with `merge`.
         Editor-only categories in the AUTHOR sheet stop the run (routing error).
merge    Consolidates the given rows into one row with the supplied Issue and Comment.
         Positions and [ref n] tags of all rows are kept; the merge is logged.
build    Writes the author workbook: an Overview sheet and one sheet per theme
         (References; Sources and evidence; Data and content; Quotations; Terms and
         administration), with IDs R1, S1, D1, Q1, T1 … and an empty Remarks column.
         --deliver removes the [ref n] tags and the [CATEGORY] prefix, and warns about
         positions that still lack a page number.
remarks  Reads the returned workbook back into one TSV (ID, Position, Issue, Comment,
         Remarks) for finalisation.

Exit codes: 0 = done, 1 = routing error or warnings that block delivery, 2 = input error.
"""
import argparse
import csv
import datetime
import difflib
import io
import os
import re
import shutil
import sys

THEMES = [  # (sheet name, ID prefix, categories, what the author is asked for)
    ('References', 'R', ['REF-MISSING', 'REF-YEAR'],
     'Missing reference entries, and conflicts between the text and the reference list.'),
    ('Sources and evidence', 'S', ['SOURCE-NEEDED'],
     'Statements that need a source.'),
    ('Data and content', 'D', ['DATA', 'CONTENT'],
     'Figures that disagree, and questions of structure, placement, titles and captions.'),
    ('Quotations', 'Q', ['QUOTE'],
     'Quotations to check against the original.'),
    ('Terms and administration', 'T', ['TERM', 'ADMIN'],
     'Terms only you can choose, and front matter, annexes and other administrative items.'),
]
AUTHOR_CATS = [c for t in THEMES for c in t[2]]
EDITOR_ONLY = {'PIPELINE', 'REMAP', 'REF-CLEANUP', 'ACR-DEF', 'STRUCTURE', 'CHECK', 'LOCKED',
               'PENDING-AUTHOR'}
CAT_RX = re.compile(r'^\s*\[([A-Z][A-Z-]+)\]\s*')
REF_RX = re.compile(r'\s*\[ref\s+([^\]]+)\]')
INFER = [  # used only when the Issue has no [CATEGORY]; logged as inferred
    ('QUOTE', r'\bquot(?:e|ed|ation)'),
    ('REF-YEAR', r'\byear discrepancy|\bdiffers? between (?:the )?text and|\bdate[sd]? (?:differ|conflict)'),
    ('REF-MISSING', r'\b(?:no|missing|without) (?:a )?reference entr|\breference entr(?:y|ies)\b.*\b(?:missing|lack)|\bnot in the (?:reference )?list'),
    ('SOURCE-NEEDED', r'\buncited\b|\bwithout (?:a )?(?:source|citation)|\bsource(?:s)? (?:needed|for)|\bno source\b|\bcitation coverage'),
    ('DATA', r'\bfigure[s]? (?:disagree|discrepan)|\bdiscrepanc|\bcount\b|\btable\b.*\bdisagree|\breconcile\b'),
    ('CONTENT', r'\broadmap\b|\bstructure\b|\bheading\b|\btitle\b|\bcaption\b|\bplacement\b|\babstract\b|\bsection\b'),
    ('ADMIN', r'\bkeywords?\b|\bannex|\bappendix|\bfront matter|\breceipt'),
    ('REF-YEAR', r'\breference\b|\bentr(?:y|ies)\b|\bpage range|\bDOI\b|\bURL\b|\bplace of publication|\bjournal title'),
]


# ---------------------------------------------------------------- reading and writing TSV
def read_sheet(path):
    with open(path, encoding='utf-8-sig', newline='') as fh:
        text = fh.read()
    dialect = 'excel-tab' if text.count('\t') >= text.count(',') else 'excel'
    rows = list(csv.reader(io.StringIO(text), dialect=dialect))
    rows = [r for r in rows if any(c.strip() for c in r)]
    hi = next((i for i, r in enumerate(rows)
               if len(r) >= 4 and r[2].strip().lower() == 'issue' and r[3].strip().lower() == 'comment'), None)
    if hi is None:
        sys.exit(f'{path}: no header row with Issue and Comment in columns 3 and 4')
    header = rows[hi]
    items = []
    for r in rows[hi + 1:]:
        r = (r + [''] * len(header))[:len(header)]
        if not (r[2].strip() or r[3].strip()):
            continue
        items.append({'no': r[0].strip(), 'position': r[1].strip(), 'issue': r[2].strip(),
                      'comment': r[3].strip(), 'extra': r[4:]})
    return header, items


def write_sheet(path, header, items):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter='\t', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
    w.writerow(header)
    for it in items:
        w.writerow([it['no'], it['position'], it['issue'], it['comment']] + list(it['extra']))
    with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
        fh.write(buf.getvalue())


# ---------------------------------------------------------------- analysis helpers
def category(it):
    m = CAT_RX.match(it['issue'])
    if m:
        return m.group(1), False
    text = it['issue'] + ' ' + it['comment']
    for cat, rx in INFER:
        if re.search(rx, text, re.I):
            return cat, True
    return 'CONTENT', True


def label(issue):
    return CAT_RX.sub('', issue).strip()


def norm(s):
    s = REF_RX.sub('', s).lower()
    s = re.sub(r'[‘’“”"\']', '', s)
    return re.sub(r'\s+', ' ', s).strip(' .')


def template(s):
    """The request with its subject masked: quotations, citations, names, numbers."""
    s = REF_RX.sub('', s)
    s = re.sub(r'[‘“"][^’”"]{0,200}[’”"]', 'Q', s)
    s = re.sub(r'\([^()]*\d{4}[^()]*\)', 'C', s)
    s = re.sub(r'\b[A-Z][\w’\'-]+(?:\s+(?:and|&|et al\.?)\s+[A-Z][\w’\'-]+)*', 'N', s)
    s = re.sub(r'\d+(?:[–-]\d+)?', '#', s)
    return re.sub(r'\s+', ' ', s).lower()


def refs(it):
    out = []
    for m in REF_RX.finditer(it['comment']):
        for part in re.split(r'[,;]\s*', m.group(1)):
            if part.strip() and part.strip() not in out:
                out.append(part.strip())
    return out


def first_pos(it):
    nums = [int(x) for r in refs(it) for x in re.findall(r'\d+', r)[:1]]
    if nums:
        return min(nums)
    m = re.search(r'\bpp?\.\s*(\d+)', it['position']) or re.search(r'\d+', it['position'])
    return int(m.group(1) if m.lastindex else m.group(0)) if m else 10 ** 6


def join_positions(*ps):
    out = []
    for p in ps:
        for part in re.split(r'\s*\|\s*', p):
            if part and part not in out:
                out.append(part)
    return ' | '.join(out)


def sentences(s):
    return [x for x in re.split(r'(?<=[.?!])\s+(?=[A-Z‘“(])', REF_RX.sub('', s).strip()) if x]


def combine(keep, other):
    """Merge `other` into `keep`: positions, [ref n] tags and new sentences only."""
    base = REF_RX.sub('', keep['comment']).strip()
    have = {norm(x) for x in sentences(base)}
    add = [x for x in sentences(other['comment']) if norm(x) not in have]
    if add:
        base = base + ' ' + ' '.join(add)
    tags = refs(keep) + [r for r in refs(other) if r not in refs(keep)]
    keep['comment'] = base + (f' [ref {", ".join(tags)}]' if tags else '')
    keep['position'] = join_positions(keep['position'], other['position'])


def theme_index(cat):
    for i, t in enumerate(THEMES):
        if cat in t[2]:
            return i
    return len(THEMES) - 1


# ---------------------------------------------------------------- merge log
LOG_HEADER = ['When', 'Action', 'Kept as (Issue)', 'Original no.', 'Original Position', 'Original Issue',
              'Original Comment']


def log_paths(sheet):
    stem = re.sub(r'\.(tsv|csv)$', '', sheet, flags=re.I)
    return stem + '_merge_log.tsv', stem + '_tidy_report.md'


def append_log(path, entries):
    new = not os.path.exists(path)
    with open(path, 'a', encoding='utf-8-sig' if new else 'utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
        if new:
            w.writerow(LOG_HEADER)
        for e in entries:
            w.writerow(e)


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')


# ---------------------------------------------------------------- commands
def check_routing(items):
    bad = [it for it in items if category(it)[0] in EDITOR_ONLY]
    for it in bad:
        print(f'ROUTING ERROR: row {it["no"]} is an EDITOR item in the AUTHOR sheet: {it["issue"]}')
    return bad


def cmd_tidy(a):
    header, items = read_sheet(a.sheet)
    if check_routing(items):
        sys.exit(1)
    shutil.copyfile(a.sheet, a.sheet + '.bak')
    log, report = log_paths(a.sheet)
    entries, kept = [], []
    for it in items:
        cat, inferred = category(it)
        it['cat'], it['inferred'] = cat, inferred
        target = None
        for k in kept:
            if k['cat'] != cat:
                continue
            if norm(k['comment']) == norm(it['comment']):
                target, how = k, 'merged: exact duplicate'
                break
            if norm(label(k['issue'])) == norm(label(it['issue'])):
                target, how = k, 'merged: same subject'
                break
        if target is None:
            kept.append(it)
            continue
        entries.append([now(), how, target['issue'], it['no'], it['position'], it['issue'], it['comment']])
        combine(target, it)
    kept.sort(key=lambda k: (theme_index(k['cat']), first_pos(k)))
    for i, k in enumerate(kept, 1):
        k['no'] = str(i)
    write_sheet(a.sheet, header, kept)
    if entries:
        append_log(log, entries)
    # pattern clusters: same category, same request, different subjects
    clusters, seen = [], set()
    for i, k in enumerate(kept):
        if i in seen:
            continue
        group = [i]
        for j in range(i + 1, len(kept)):
            if j in seen or kept[j]['cat'] != k['cat']:
                continue
            if difflib.SequenceMatcher(None, template(k['comment']), template(kept[j]['comment'])).ratio() >= a.similarity:
                group.append(j)
        if len(group) > 1:
            seen.update(group)
            clusters.append(group)
    inferred = [k for k in kept if k['inferred']]
    with open(report, 'w', encoding='utf-8') as fh:
        fh.write(f'# Comment sheet tidy report\n\n*Sheet:* `{os.path.basename(a.sheet)}` · *Run:* {now()}\n\n')
        fh.write(f'- Rows before: {len(items)}; after: {len(kept)}; merged in this run: {len(entries)} '
                 f'(log: `{os.path.basename(log)}`).\n')
        counts = {t[0]: sum(1 for k in kept if theme_index(k['cat']) == n) for n, t in enumerate(THEMES)}
        fh.write('- By theme: ' + '; '.join(f'{n} {c}' for n, c in counts.items() if c) + '.\n\n')
        fh.write('## Clusters to consolidate\n\n')
        if not clusters:
            fh.write('None: no two rows ask for the same thing about different subjects.\n')
        for g in clusters:
            rows = ', '.join(kept[x]['no'] for x in g)
            fh.write(f'- **Rows {rows}** ({kept[g[0]]["cat"]}): ' +
                     '; '.join(label(kept[x]['issue']) for x in g) + '\n')
        fh.write('\nConsolidate each cluster into one row with `merge --rows …`: one Issue that names '
                 'the pattern, one request, and every subject listed with its position.\n')
        if inferred:
            fh.write('\n## Categories inferred (the Issue has no [CATEGORY] prefix)\n\n')
            for k in inferred:
                fh.write(f'- Row {k["no"]}: {k["cat"]} — {label(k["issue"])}\n')
    print(f'{os.path.basename(a.sheet)}: {len(items)} → {len(kept)} rows; {len(entries)} merged; '
          f'{len(clusters)} cluster(s) to consolidate; report: {os.path.basename(report)}')


def cmd_merge(a):
    header, items = read_sheet(a.sheet)
    nos = [x.strip() for x in a.rows.split(',') if x.strip()]
    chosen = [it for it in items if it['no'] in nos]
    if len(chosen) != len(nos) or len(chosen) < 2:
        sys.exit(f'rows not found or fewer than two: {a.rows}')
    cats = {category(it)[0] for it in chosen}
    if len(cats) > 1:
        sys.exit(f'rows belong to different categories ({", ".join(sorted(cats))}); merge within one category')
    shutil.copyfile(a.sheet, a.sheet + '.bak')
    tags, pos = [], ''
    for it in chosen:
        tags += [r for r in refs(it) if r not in tags]
        pos = join_positions(pos, it['position'])
    new = dict(chosen[0])
    new['issue'] = a.issue
    parts = re.split(r'\s*\|\s*', pos)
    parts.sort(key=lambda x: int(re.search(r'\d+', x).group(0)) if re.search(r'\d+', x) else 10 ** 6)
    new['position'] = a.position or ' | '.join(parts)
    new['comment'] = REF_RX.sub('', a.comment).strip() + (f' [ref {", ".join(tags)}]' if tags else '')
    log, _ = log_paths(a.sheet)
    append_log(log, [[now(), 'consolidated: same request', a.issue, it['no'], it['position'], it['issue'],
                      it['comment']] for it in chosen])
    out = []
    for it in items:
        if it is chosen[0]:
            out.append(new)
        elif it not in chosen:
            out.append(it)
    for i, it in enumerate(out, 1):
        it['no'] = str(i)
    write_sheet(a.sheet, header, out)
    print(f'merged rows {a.rows} into one; {len(out)} rows remain')


def cmd_build(a):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    header, items = read_sheet(a.sheet)
    if check_routing(items):
        sys.exit(1)
    wb = Workbook()
    ov = wb.active
    ov.title = 'Overview'
    bold, wrap = Font(bold=True), Alignment(wrap_text=True, vertical='top')
    answer = PatternFill('solid', fgColor='FFF2CC')
    title = a.title or os.path.basename(re.sub(r'\.(tsv|csv)$', '', a.sheet, flags=re.I))
    ov['A1'] = title
    ov['A1'].font = Font(bold=True, size=13)
    ov['A3'] = ('Each sheet below holds one group of questions. Please answer in the Remarks column '
                '(shaded) of each row, and leave the other columns unchanged. Where a row lists several '
                'places, one answer covers all of them.')
    ov['A3'].alignment = wrap
    ov.merge_cells('A3:C3')
    ov.row_dimensions[3].height = 48
    ov.append([])
    ov.append(['Sheet', 'Questions', 'What we need'])
    for c in ov[5]:
        c.font = bold
    warnings, total = [], 0
    for name, prefix, cats, need in THEMES:
        rows = sorted([it for it in items if category(it)[0] in cats], key=first_pos)
        if not rows:
            continue
        ws = wb.create_sheet(name)
        ws.append(['ID', 'Position', 'Issue', 'Comment', 'Remarks'])
        for c in ws[1]:
            c.font = bold
        for n, it in enumerate(rows, 1):
            issue, comment = it['issue'], it['comment']
            if a.deliver:
                issue = label(issue)
                comment = REF_RX.sub('', comment).strip()
                if not re.search(r'\bpp?\.\s*\d', it['position']):
                    warnings.append(f'{prefix}{n}: Position has no page number ({it["position"][:60]})')
            ws.append([f'{prefix}{n}', it['position'], issue, comment, ''])
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = wrap
            row[4].fill = answer
        for col, width in zip('ABCDE', (7, 24, 34, 80, 45)):
            ws.column_dimensions[col].width = width
        ws.freeze_panes = 'A2'
        ov.append([name, len(rows), need])
        total += len(rows)
    ov.append(['Total', total, ''])
    ov[ov.max_row][0].font = bold
    for col, width in zip('ABC', (26, 11, 80)):
        ov.column_dimensions[col].width = width
    for row in ov.iter_rows(min_row=6):
        for c in row:
            c.alignment = wrap
    wb.save(a.output)
    print(f'{a.output}: {total} questions in {len(wb.sheetnames) - 1} sheet(s)')
    for w in warnings:
        print('WARNING:', w)
    if warnings and a.deliver:
        sys.exit(1)


def cmd_remarks(a):
    from openpyxl import load_workbook
    wb = load_workbook(a.workbook, read_only=True)
    out = [['ID', 'Position', 'Issue', 'Comment', 'Remarks']]
    for ws in wb.worksheets[1:]:
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0 or not row or not row[0]:
                continue
            out.append([('' if v is None else str(v)) for v in (list(row) + [None] * 5)[:5]])
    buf = io.StringIO()
    csv.writer(buf, delimiter='\t', quoting=csv.QUOTE_ALL, lineterminator='\r\n').writerows(out)
    with open(a.output, 'w', encoding='utf-8-sig', newline='') as fh:
        fh.write(buf.getvalue())
    answered = sum(1 for r in out[1:] if r[4].strip())
    print(f'{a.output}: {len(out) - 1} rows, {answered} answered')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    t = sub.add_parser('tidy')
    t.add_argument('sheet')
    t.add_argument('--similarity', type=float, default=0.72,
                   help='threshold for reporting rows that ask for the same thing (default 0.72)')
    m = sub.add_parser('merge')
    m.add_argument('sheet')
    m.add_argument('--rows', required=True)
    m.add_argument('--issue', required=True)
    m.add_argument('--comment', required=True)
    m.add_argument('--position')
    b = sub.add_parser('build')
    b.add_argument('sheet')
    b.add_argument('-o', '--output', required=True)
    b.add_argument('--deliver', action='store_true')
    b.add_argument('--title')
    r = sub.add_parser('remarks')
    r.add_argument('workbook')
    r.add_argument('-o', '--output', required=True)
    a = ap.parse_args()
    {'tidy': cmd_tidy, 'merge': cmd_merge, 'build': cmd_build, 'remarks': cmd_remarks}[a.cmd](a)


if __name__ == '__main__':
    main()
