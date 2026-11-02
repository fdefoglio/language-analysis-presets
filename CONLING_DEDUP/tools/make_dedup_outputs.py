#!/usr/bin/env python3
"""CONLING DEDUP proposal generator.

Usage: python make_dedup_outputs.py <export.md> <proposals.json>

Reads the editor_tool export (lines of the form "[n] text") and a filled-in
proposals JSON (see proposals_TEMPLATE.json). Writes, next to proposals.json:

  <stem>.diff   unified diff of every proposed paragraph (apply-source)
  memo.json     input for build_memo.js (word-level diff runs, references
                by section and opening words, Markdown markers stripped)

Rules enforced here: every target label must exist in the export and the
proposed text must differ from the original. [n] labels are never altered.
"""
import difflib
import json
import re
import sys
from pathlib import Path

LOCATOR_WORDS = 8


def strip_md(s: str) -> str:
    s = s.replace("**", "")
    return re.sub(r"\s+", " ", s).strip()


def wdiff(a: str, b: str):
    A, B = a.split(" "), b.split(" ")
    sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
    runs = []

    def push(kind, words):
        if not words:
            return
        txt = " ".join(words)
        if runs and runs[-1][0] == kind:
            runs[-1][1] += " " + txt
        else:
            runs.append([kind, txt])

    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            push("eq", A[a1:a2])
        elif op == "delete":
            push("del", A[a1:a2])
        elif op == "insert":
            push("ins", B[b1:b2])
        else:
            push("del", A[a1:a2])
            push("ins", B[b1:b2])
    return [{"k": kind, "t": txt + (" " if i < len(runs) - 1 else "")}
            for i, (kind, txt) in enumerate(runs)]


def main() -> None:
    export_path, prop_path = Path(sys.argv[1]), Path(sys.argv[2])
    prop = json.loads(prop_path.read_text(encoding="utf-8"))
    meta, items = prop["meta"], prop["items"]

    lab = {}
    for i, line in enumerate(export_path.read_text(encoding="utf-8").splitlines()):
        m = re.match(r"^\[(\d+)\] (.*)$", line)
        if m:
            lab[int(m.group(1))] = (i, m.group(2))

    new, sections = {}, {}
    for it in items:
        for n_str, txt in it["changes"].items():
            n = int(n_str)
            if n not in lab:
                sys.exit(f"ERROR: label [{n}] not found in the export.")
            if lab[n][1] == txt:
                sys.exit(f"ERROR: proposed text for [{n}] is identical to the original.")
            new[n] = txt
            sections[n] = it["sections"][n_str]

    # ---- unified diff; adjacent changed paragraphs share one hunk ----
    out = [f"--- a/{meta['export_name']} (v0, unedited)",
           f"+++ b/DEDUP proposal {meta['rev']}, {meta['date']} (NOT APPLIED, pending supervisor approval)"]
    labels = sorted(new)
    groups, cur = [], [labels[0]]
    for n in labels[1:]:
        if lab[n][0] == lab[cur[-1]][0] + 2:   # next paragraph, one blank line between
            cur.append(n)
        else:
            groups.append(cur)
            cur = [n]
    groups.append(cur)
    for g in groups:
        start = lab[g[0]][0] + 1
        count = 2 * len(g) - 1
        out.append(f"@@ -{start} +{start} @@" if count == 1
                   else f"@@ -{start},{count} +{start},{count} @@")
        for side, texts in (("-", {n: lab[n][1] for n in g}), ("+", new)):
            for j, n in enumerate(g):
                out.append(f"{side}[{n}] {texts[n]}")
                if j < len(g) - 1:
                    out.append(side)
    diff_path = prop_path.with_name(meta["file_stem"] + ".diff")
    diff_path.write_text("\n".join(out) + "\n", encoding="utf-8")

    # ---- memo.json ----
    memo_items = []
    for it in items:
        changes = []
        for n_str in it["changes"]:
            n = int(n_str)
            old = strip_md(lab[n][1])
            words = old.split(" ")
            locator = " ".join(words[:LOCATOR_WORDS]) + ("…" if len(words) > LOCATOR_WORDS else "")
            changes.append({
                "ref": f"Section {sections[n]}, paragraph beginning “{locator}”",
                "runs": wdiff(old, strip_md(new[n])),
            })
        memo_items.append({"num": it["num"], "label": it["label"],
                           "why": it["motivation"], "kept": it["retained"],
                           "changes": changes})
    memo = {"meta": {"title": meta["memo_title"],
                     "subtitle": meta["memo_subtitle"],
                     "byline": meta["memo_byline"],
                     "motivation_label": "Motivation: ",
                     "retained_label": "Retained in full: "},
            "items": memo_items}
    prop_path.with_name("memo.json").write_text(
        json.dumps(memo, ensure_ascii=False), encoding="utf-8")

    for it in memo_items:                      # house-style guard
        for f in ("label", "why", "kept"):
            if "—" in it[f]:
                sys.exit(f"ERROR: em dash in item {it['num']} field '{f}'. House style forbids em dashes.")
    print(f"written {diff_path.name} ({len(groups)} hunks, {len(labels)} paragraphs) and memo.json ({len(memo_items)} items)")


if __name__ == "__main__":
    main()
