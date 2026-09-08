CONLING EDITORIAL PIPELINE — README
=====================================
Reference for sequencing the JWGD-converted prompts in this repository.
Based on each prompt's own stated Required Inputs, output files, and
"What This [Pass] Does NOT Cover" sections — not invented from scratch.

-------------------------------------------------------------------------
0. TWO SEPARATE TRACKS
-------------------------------------------------------------------------

The prompts in this repo serve two different kinds of work and do not all
belong on one line:

  TRACK A — Academic manuscripts (theses, journal articles)
            Starts with LANG_EVAL. This is the track with the most passes,
            because manuscript language quality is judged on many axes at
            once (grammar, register, rhythm, structure, citations).

  TRACK B — Standalone / mechanical passes
            CONLING_Repetition_Resolution, ToC_hyperlinking, and
            DEDUP_MARKUP are each usable on their own, outside the academic
            sequence, whenever their specific trigger condition is met
            (a repetition CSV exists; fields need QA; a duplication report
            exists). They are described separately in Section 3.

Confirmed with Frans: LANG_EVAL is used only for Track A (academic work) —
it is not part of any financial/economic-report workflow. The
Passive-to-Active Audit and Prose Polish Audit are generic enough to be run
on non-academic documents too (financial/economic reports), but in that
case they run standalone, without a LANG_EVAL pass ahead of them — see
Section 4.

-------------------------------------------------------------------------
1. TRACK A — ACADEMIC MANUSCRIPT SEQUENCE (recommended order)
-------------------------------------------------------------------------

  PASS 0  LANG_EVAL (unconverted — left in its DSL preset form; not broken,
          not touched in this exercise)
          --------------------------------------------------------------
          Purpose : first-pass triage. Produces the baseline scores,
                    ranked issues, and quotation/volume information Frans
                    uses for pre-flight assessment and quoting.
          Reads   : doc_path (+ optional cover_letter_path, styleguide)
          Writes  : LANG-EVAL_report.md
                    LANG-EVAL_findings.csv
                    LANG-EVAL_metrics.json
                    LANG-EVAL_compliance.tsv
          Note    : Academic/scientific documents ONLY, per Frans.
                    Everything downstream in Track A depends on this
                    pass's outputs existing.

  PASS 1  ESL Fluency & Register Audit  (CONLING_ESL_Fluency_Audit)
          --------------------------------------------------------------
          Purpose : register and native-speaker-fluency pass — the eight
                    trigger criteria (awkward phrasing, register mismatch,
                    non-standard formulations, weak openers, grammatical
                    errors with stylistic impact, factual flags,
                    first-person pronouns).
          Reads   : manuscript_for_ai.md, LANG-EVAL_report.md,
                    LANG-EVAL_findings.csv, LANG-EVAL_metrics.json,
                    scan_report.csv
          Writes  : a findings CSV (label/original/remark/solution)
          Depends on Pass 0's outputs explicitly — this is stated as
          "Pass 2 of the CONLING edit session" in the prompt itself.

  PASS 2  L1 Interference Pre-Edit Screening  (L1 interference analysis)
          --------------------------------------------------------------
          Purpose : flags phrasing shaped by the author's native
                    language(s) — structural interference, not
                    register/fluency in general.
          Reads   : the manuscript. ASKS Frans for the author's native
                    language(s) before scanning if not already given —
                    do not skip this by assuming a default.
          Writes  : a Flagged Items table + severity summary.
          Sequencing note: this prompt does not itself declare a required
          position relative to ESL Fluency Audit, but the two are
          complementary — ESL Fluency looks for fluency/register issues
          broadly, L1 Interference looks specifically for patterns
          attributable to a named native language. Running L1 Interference
          alongside or immediately after Pass 1 (before Prose Polish) means
          Prose Polish's own L1-intensifier trigger (Trigger 8) sees a
          cleaner manuscript with the bulk of structural interference
          already addressed.

  PASS 3  Prose Polish Audit  (CONLING_Prose_Polish_Audit)
          --------------------------------------------------------------
          Purpose : sentence rhythm and readability — weak openers,
                    close-proximity repetition (author names, structural
                    words, or full repetition if the detector script
                    wasn't run — see below), overlong sentences, duplicate
                    citations, stacked qualifiers, L1 intensifiers at the
                    word level.
          Reads   : the manuscript. Checks whether word_repetitions.csv
                    (from word_repetition_detector.py) already exists.
          Writes  : a findings CSV.
          Explicitly stated in the prompt: "Run this pass AFTER the ESL
          Fluency Audit and AFTER the L1 Interference Analysis so that
          residual issues not caught by those passes surface here."
          This is the one hard, stated ordering rule across the whole
          Track A sequence — Prose Polish is designed to run last among
          the three fluency-adjacent passes, not first.

  [OPTIONAL, IF RUN]  word_repetition_detector.py → Repetition Resolution
          --------------------------------------------------------------
          If the detector script has been run on the manuscript (producing
          word_repetitions.csv), run CONLING_Repetition_Resolution to
          generate the actual fixes BEFORE Prose Polish, so Prose Polish's
          repetition trigger can detect that the CSV already exists and
          skip re-detecting general repetition (see Prose Polish's own
          Guardrails). If the detector was NOT run, Prose Polish's built-in
          fallback covers general repetition on its own — no separate step
          needed. See Section 3 for Repetition Resolution's own details.

  PASS 4  Passive-to-Active Voice Audit  (CONLING_Passive_to_Active_Audit)
          --------------------------------------------------------------
          Purpose : converts passive constructions only where the active
                    version is demonstrably better (Golden Rule test);
                    register-calibrated threshold (academic/policy/
                    legal/general/technical).
          Reads   : the manuscript. Self-contained — does not require any
                    other pass's output. ASKS for document register if not
                    already established in conversation (do not assume
                    "academic" by default — see the prompt's own Guardrails,
                    updated per Frans's instruction).
          Writes  : passive_to_active_findings.csv +
                    passive_author_queries.tsv
          Sequencing note: the prompt does not declare a required position
          in the academic sequence. Because it is self-contained and its
          Golden Rule test is sensitive to sentence-level phrasing, running
          it AFTER Prose Polish (so sentence rhythm is already settled)
          avoids the voice pass working against wording that Prose Polish
          would have changed anyway.

  PASS 5  DEDUP_MARKUP  (Dedup_Claude_prompt)
          --------------------------------------------------------------
          Purpose : conceptual deduplication — structural echo, claim
                    recycling, abstract/body mirroring, phrase-level
                    repetition across sections (not sentence-level, see
                    Section 3 below).
          Reads   : doc_path + optionally a prior LANG_EVAL duplication
                    report (generates its own analysis if absent).
          Writes  : DEDUP_partN.md markup files.
          Sequencing note: this is a structural/section-level pass, most
          useful once sentence-level language quality is already settled —
          it is naturally a late-stage pass, run after Passes 1-4, since
          restructuring content before the language itself is finalised
          risks re-introducing sentence-level issues in the merged/rewritten
          passages.

  PASS 6  ToC Hyperlinking / Document Navigation Pass  (ToC_hyperlinking)
          --------------------------------------------------------------
          Purpose : QA pass on heading styles and caption formatting so
                    Word's ToC/List of Tables/List of Figures fields
                    (already injected locally) resolve correctly on F9.
          Reads   : the already-field-coded document.
          Writes  : nothing — in-place formatting only, then a reminder
                    to press Ctrl+A then F9.
          Sequencing note: this is a final-format pass, since it depends on
          headings and captions being in their FINAL wording — running it
          before content-level passes (Prose Polish, DEDUP) risks having to
          redo caption or heading text that a later pass then changes.
          Run this last, once no further text changes are expected.

  SUMMARY — TRACK A ORDER:
    LANG_EVAL → ESL Fluency Audit → L1 Interference Analysis →
    [word_repetition_detector.py → Repetition Resolution, if used] →
    Prose Polish Audit → Passive-to-Active Audit → DEDUP_MARKUP →
    ToC Hyperlinking

  ONE RULE STATED EXPLICITLY IN THE PROMPTS THEMSELVES (not inferred):
    Prose Polish MUST run after ESL Fluency Audit and after L1
    Interference Analysis. Everything else above is Frans's/Claude's
    reasoned default ordering, not a hard dependency declared in any
    prompt — deviate from it where a specific manuscript calls for it.

-------------------------------------------------------------------------
2. STARTING POINT — WHICH PASS TO INVOKE FIRST
-------------------------------------------------------------------------

  Academic manuscript, first time through  → LANG_EVAL
  Academic manuscript, LANG_EVAL already run this session
                                            → ESL Fluency Audit
  Financial/economic/policy report (no LANG_EVAL involved)
                                            → see Section 4
  Just need repetition fixed from an existing script output
                                            → Repetition Resolution
  Just need Word fields QA'd before delivery
                                            → ToC Hyperlinking
  Just need dedup markup on an already-analysed document
                                            → DEDUP_MARKUP

-------------------------------------------------------------------------
3. STANDALONE PASSES (not tied to the Track A sequence)
-------------------------------------------------------------------------

  CONLING_Repetition_Resolution
    Fix-only. Consumes word_repetitions.csv (from
    word_repetition_detector.py) + manuscript_for_ai.md. Does not detect
    new issues. Run whenever the detector script has already been run and
    fixes are needed — whether inside the Track A sequence (see Pass 3
    note above) or independently.
    OPEN ITEM (flagged, unresolved): the "Retain" resolution option has no
    column in the current output schema (only original/target columns; no
    identical-row output permitted). If a genuine Retain case comes up in
    practice, the model is instructed to stop and ask rather than silently
    dropping or forcing the row. Decide before this recurs often:
      (a) add a remark column and permit identical rows for Retain, or
      (b) log Retain decisions outside the CSV, or
      (c) drop Retain as an option entirely.

  ToC_hyperlinking (Document Navigation & Polish Pass)
    QA-only, in-place. No file inputs beyond the document itself, no CSV/
    TSV output. Independent of every other pass — can run on any document
    with already-injected Word field codes, academic or not.

  DEDUP_MARKUP
    Can run standalone (generates its own duplication analysis) or after
    a LANG_EVAL duplication report exists. Works on any document type in
    principle, though in practice used on the same academic manuscripts as
    Track A.

-------------------------------------------------------------------------
4. NON-ACADEMIC WORK (financial / economic / policy reports)
-------------------------------------------------------------------------

  LANG_EVAL is not used here (academic-only, per Frans).

  Applicable passes, run standalone, in this order if multiple are needed:

    1. Passive-to-Active Audit — fully self-contained; register
       calibration table already covers policy/legal/general/technical
       thresholds. Will ask for document register if not already
       established in conversation.
    2. Prose Polish Audit — also usable standalone (its own repetition
       trigger falls back to full detection automatically when no
       detector CSV exists — see the prompt's Guardrails).

  Both prompts work without any prior pass. Order between them is not
  load-bearing — either can run first — but running Passive-to-Active
  before Prose Polish avoids the voice pass working against sentence
  rewording Prose Polish might otherwise introduce.

-------------------------------------------------------------------------
5. PROMPTS DELIBERATELY LEFT UNCONVERTED
-------------------------------------------------------------------------

  LANG_EVAL_preset_v1_3N_neutral.md — a DSL config preset, not a prose
    instruction; reliable as-is; JWGD's narrative structure doesn't suit a
    declarative config block. Left untouched per Frans's instruction.

  CommentsList — a .tsv structural exemplar Frans shows the model to
    demonstrate desired comment-sheet output. Not a prompt; stays in .tsv
    format. Left untouched per Frans's instruction.

-------------------------------------------------------------------------
6. QUICK REFERENCE TABLE
-------------------------------------------------------------------------

  Pass                          | Depends on            | Feeds into
  -------------------------------|------------------------|------------------
  LANG_EVAL                     | (nothing)              | ESL Fluency Audit
  ESL Fluency Audit             | LANG_EVAL outputs      | (manuscript state)
  L1 Interference Analysis      | native language(s)     | (manuscript state)
                                 | (asked, not read)      |
  Repetition Resolution         | word_repetitions.csv   | (manuscript state)
                                 | (from detector script) |
  Prose Polish Audit            | ESL Fluency Audit +    | Passive-to-Active
                                 | L1 Interference        |   (recommended)
                                 | (stated in prompt)     |
  Passive-to-Active Audit       | (nothing — self-       | DEDUP_MARKUP
                                 | contained)             |   (recommended)
  DEDUP_MARKUP                  | (nothing required;     | ToC Hyperlinking
                                 | optional LANG_EVAL     |   (recommended)
                                 | duplication report)    |
  ToC Hyperlinking              | final text/headings/   | (delivery —
                                 | captions               |    Ctrl+A, F9)

-------------------------------------------------------------------------
Last updated: conversion pass completed and pushed to GitHub, per Frans's
confirmation each prompt renders correctly in the repository.
