---
name: prompt-jwgd-framework
description: >-
  Restructure or draft prompts, system instructions, and SKILL.md files using the four-part Job → Why → Guardrails → What-done-looks-like framework, with a built-in instruction for the model or agent to interview the user whenever it lacks the information it needs to proceed. Trigger this whenever the user asks to "convert this prompt to the new framework," "restructure this prompt," "put this in Job/Why/Guardrails format," mentions "JWGD," or hands over an existing prompt or SKILL.md and asks for it to be brought in line with the newer four-part structure — even if they only describe the shape without naming it. Also trigger when drafting a brand-new prompt from scratch and the user wants it built directly in this structure, or when converting a batch of existing prompts one at a time. Complements calibrate-prompt-language (which tightens word-level absolutes like MUST/NEVER) — reach for both together when a rewrite calls for structural reorganisation as well as line-level tightening; this skill handles the structure, that one handles the wording.
---

# Job → Why → Guardrails → Done (JWGD) Framework

## What the framework is

Every prompt gets reorganised under four headings, in this order:

1. **Job** — the concrete task, stated as an outcome. Not a persona ("You are an expert editor…"), a task ("Edit this manuscript so that…").
2. **Why** — the purpose this serves: who it's for, what's at stake if it's done well or badly. This is what lets the model reason correctly about a case the prompt never explicitly anticipated, instead of pattern-matching blindly to the literal instruction.
3. **Guardrails** — the hard constraints: invariants that must hold regardless of context, scope boundaries, format rules, and — always — an explicit instruction to ask the user rather than guess when something needed is missing.
4. **What done looks like** — a concrete, checkable description of the finished deliverable, specific enough that the model (or Frans, reviewing the output) can verify against it without re-reading the whole prompt.

Detail that doesn't belong at the top level — step-by-step procedures, terminology tables, worked examples, column conventions — doesn't get discarded. It nests underneath, usually as a "Method" or "Reference" subsection after Guardrails or Done. The four headings are the orientation a model reads first; they are not a size limit on the prompt.

## Why this order, specifically

Job before Why: state the task before justifying it, so the model isn't holding an unresolved question ("what am I being asked?") while it reads the reasoning.

Why before Guardrails: reasoning explained before constraints listed means the model understands *what a constraint is protecting* by the time it hits it, rather than meeting a bare "never do X" with no sense of why X is off-limits — which is exactly the condition that causes a model to either over-apply the rule somewhere it doesn't belong, or quietly drop it under pressure from a later instruction.

Guardrails before Done: the model should know its boundaries before it's told what success looks like, so "what done looks like" reads as the target within those boundaries, not a separate checklist competing with them.

## The interview clause

Every converted prompt's Guardrails section includes an instruction to interview the user when something material is missing — but write it specific to that prompt, not generic. A generic "ask if you're unsure" gives the model no sense of *what kinds of things* are worth pausing for versus what it should just get on with.

**Weak (generic):**
> If you're unsure about anything, ask the user before proceeding.

**Strong (specific to the task):**
> If the source document doesn't specify [the particular thing this prompt actually depends on — e.g. target register, which terminology list takes precedence, the client's house spelling convention], ask before proceeding. Don't guess at these; do proceed on everything else the prompt already specifies.

The second version tells the model which gaps are worth stopping for and confirms that everything else should proceed without hand-holding — that second half matters as much as the first. A prompt that says "ask when unsure" with no scoping tends to either interrupt constantly or never trigger at all, depending on how the model reads "unsure." Naming the actual dependency points is what makes the instruction actionable.

To find the right dependency points for a given prompt, ask: what does this task need from the user that isn't already in the prompt or the input material? Client-specific preferences, ambiguous source material, a choice between two valid approaches the prompt doesn't resolve — these are interview points. Things the prompt already answers are not; don't manufacture a question the prompt already settles.

## Converting an existing prompt

1. **Read the source prompt in full before touching it.** Frans's existing prompts (GSA, Kverneland, Honda, FAO, dissertation, edu-translation) carry terminology tables, column conventions, and audit-trail steps that are load-bearing — the conversion reorganises structure, it does not trim content. If anything looks safe to cut, it isn't; move it into a subsection instead.
2. **Sort the existing content into the four buckets** using this rough map:
   - Role/persona framing ("You are…") → usually folds into Job (restated as the outcome) or Why (restated as the standard the work is held to).
   - Rationale, "the reason this matters," context about the client or use case → Why.
   - MUST / NEVER / ALWAYS statements, scope limits, forbidden actions, format rules → Guardrails.
   - Output format specs, "return only X," acceptance criteria → What done looks like.
   - Step-by-step procedures, terminology/replacement tables, worked examples → keep as a Method or Reference subsection; reference it from Job rather than inlining it there.
3. **Add or tailor the interview clause** in Guardrails, scoped to this prompt's actual dependency points (see above).
4. **Flag anything that doesn't map cleanly** rather than forcing it into a bucket or inventing a Why that wasn't in the original — ask Frans what he intended for that piece. Silently inventing rationale the source prompt never stated is worse than leaving a gap for him to fill.
5. **Produce a short before/after summary** — which sections moved where, what (if anything) was flagged for his input — so he can review the mapping before accepting it, in keeping with the audit-trail habit the rest of his editorial tooling already follows. This doesn't need to be a line-by-line diff; a few lines per file naming what happened is enough.
6. **Hand off to `calibrate-prompt-language` afterward if it hasn't already run.** That skill tightens word-level absolutes (MUST/NEVER/ALWAYS) once the structure is settled; doing structure first and wording second avoids re-tightening language that then gets moved and reworded again.

When converting a batch, do this one prompt at a time rather than in one pass across all of them — each one has different dependency points for its interview clause, and batching invites copy-pasting a generic version across all of them.

## Worked example

**Before** (a typical single-block prompt):
> You are a meticulous copyeditor. Edit the attached manuscript for grammar and clarity. Never change direct quotations. Always preserve the author's meaning. Return the edited manuscript as a clean Word document with a change log at the end.

**After:**

```markdown
## Job
Edit the attached manuscript for grammar and clarity.

## Why
The author needs a manuscript that reads cleanly to a general audience without
losing their own voice or introducing claims they didn't make — the edit
should be invisible except in how much easier it is to read.

## Guardrails
- Never alter direct quotations — this is a fidelity invariant, not a
  judgment call.
- Preserve the author's meaning; a clearer sentence that shifts the claim is
  not an improvement.
- If the manuscript's target audience or register isn't stated, ask before
  editing rather than assuming a default. Everything else — grammar,
  clarity, structure — proceed on directly.

## What done looks like
A clean Word document with all edits applied, plus a change log at the end
listing each substantive change and the reason for it.
```

Notice the two `Never`/`Always` lines survive unchanged — they're invariants, not decisions, so `calibrate-prompt-language` would leave them alone too. The only new material is the scoped interview clause, which the original prompt didn't have at all.

## When drafting a new prompt from scratch

Write the four headings in order and fill each one before moving to the next — don't draft Guardrails or Done first and retrofit a Job around them. If a genuine dependency point exists but you don't know what it is yet (because the prompt is new and untested), say so to Frans rather than guessing at what the interview clause should name.
