// CONLING DEDUP supervisor memo builder.
// Usage: node build_memo.js [<Student>_DEDUP_proposal.docx]  (reads memo.json from the current directory)
// Revision markup is simulated formatting on purpose: the memo is not the thesis,
// so nothing in it should be acceptable as a Word revision.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, BorderStyle,
} = require("docx");

const { meta, items } = JSON.parse(fs.readFileSync("memo.json", "utf8"));

const DEL = { strike: true, color: "B42318" };
const INS = { underline: {}, color: "1D4ED8" };

const p = (opts) => new Paragraph(opts);
const t = (text, extra = {}) => new TextRun({ text, size: 22, font: "Calibri", ...extra });

const body = [];

// ---- Title block ----
body.push(p({ children: [t(meta.title, { size: 36, bold: true })], spacing: { after: 60 } }));
body.push(p({ children: [t(meta.subtitle, { italics: true, color: "444444" })], spacing: { after: 60 } }));
body.push(p({
  children: [t(meta.byline, { size: 20, color: "666666" })],
  spacing: { after: 240 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "BBBBBB", space: 6 } },
}));

// ---- Purpose ----
body.push(p({ heading: HeadingLevel.HEADING_1, children: [t("Purpose and approach", { size: 28, bold: true })], spacing: { before: 120, after: 120 } }));
[
  "During the baseline language evaluation of the unedited thesis, several passages were found to restate the same point, finding or caveat in full in two to four places. This document sets out the proposed consolidation (“DEDUP”) for approval before any of it is applied.",
  "The approach is the same throughout: one full statement is kept at the place where the point belongs to the argument, and each repetition elsewhere is shortened to a brief mention with a cross-reference to that section. No content is lost: every point remains stated in full exactly once, and the cross-references tell the reader where.",
  "Two kinds of repetition were left alone on purpose: the Chapter 5 summaries, since a summary chapter restates its material by nature, and the signposting at chapter openings and closings, which orients the reader. Only repetition that adds no new information within or across the body chapters is proposed for consolidation.",
].forEach((txt) => body.push(p({ children: [t(txt)], spacing: { after: 120 } })));

// ---- Legend ----
body.push(p({
  children: [
    t("How to read the proposed changes: ", { bold: true }),
    t("deleted text is struck through", DEL),
    t(" and "),
    t("inserted text is underlined", INS),
    t("; unchanged text appears in plain type. Paragraphs are identified by their section number and opening words in the thesis document."),
  ],
  spacing: { after: 240 },
}));

// ---- Items ----
for (const item of items) {
  body.push(p({
    heading: HeadingLevel.HEADING_2,
    children: [t(`${item.num}. ${item.label}`, { size: 24, bold: true })],
    spacing: { before: 240, after: 100 },
  }));
  body.push(p({ children: [t(meta.motivation_label, { bold: true }), t(item.why)], spacing: { after: 100 } }));
  body.push(p({ children: [t(meta.retained_label, { bold: true }), t(item.kept)], spacing: { after: 140 } }));

  for (const ch of item.changes) {
    body.push(p({
      children: [t(ch.ref, { bold: true, size: 20, color: "555555" })],
      spacing: { before: 100, after: 40 },
    }));
    const runs = ch.runs.map((r) =>
      r.k === "del" ? t(r.t, DEL) : r.k === "ins" ? t(r.t, INS) : t(r.t)
    );
    body.push(p({
      children: runs,
      indent: { left: 360 },
      spacing: { after: 140, line: 276 },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: "CCCCCC", space: 12 } },
    }));
  }
}

// ---- Closing ----
body.push(p({ heading: HeadingLevel.HEADING_1, children: [t("Next step", { size: 28, bold: true })], spacing: { before: 240, after: 120 } }));
body.push(p({
  children: [t("Please indicate, per numbered item, whether the consolidation may be applied as shown or should be adjusted. The items are independent of one another and can be approved individually. Nothing will be changed in the thesis until your decisions are received; approved items are then applied as part of the language edit, and all changes will be visible in the edited document. Purely mechanical matters visible in the quoted passages (stray formatting marks, cross-reference numbering) are handled separately in the formatting pass and do not form part of this proposal.")],
  spacing: { after: 120 },
}));

const doc = new Document({
  styles: { default: { document: { run: { font: "Calibri", size: 22 } } } },
  sections: [{ properties: {}, children: body }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = process.argv[2] || "DEDUP_proposal.docx";
  fs.writeFileSync(out, buf);
  console.log("written", out, buf.length, "bytes");
});
