# CONLING — Passive-to-Active Voice Audit Prompt

## Job

Perform a voice pass on a labelled academic manuscript: find the passive constructions that do no
useful work (they hide an actor the reader needs, inflate the sentence, or flatten the prose) and
convert those to active voice. Where the active version would not improve the prose, leave the
passive alone.

The same pass also rewrites imperatives and second- or first-person address (*Consider the case…*,
*you can see…*, *we find…*) into impersonal academic prose, because they raise the same question of
who acts in the sentence.

This is a self-contained pass: it performs its own detection and resolution, applying the Golden Rule
test (see Guardrails) to every candidate. Report each conversion as one finding in the findings table
described under *What done looks like*.

---

## Why

The passive voice is a normal, correct and often superior English construction; in formal registers
it is sometimes the only appropriate choice. This is not a grammar pass, and no rule says that passive
is wrong. The task exists because passives sometimes do real work (methods sections, keeping a topic
chain, keeping a heavy subject out of the way) and sometimes do not (hiding an actor the reader needs,
stacking into flat prose, inflating a simple action into a weak-verb phrase). Only a reader-level
judgement can tell the two apart.

The usual failure of this kind of pass is over-conversion: a model told to "fix passives" converts
mechanically, and the manuscript ends up reading as less professional where passive is the convention,
with broken topic chains and buried subjects elsewhere. A smaller number of well-chosen conversions is
worth more than many mechanical ones. Every guardrail below exists to hold that line.

---

## Guardrails

### The Golden Rule — improvement, not conversion

> **A passive construction is not a defect. If the active version is demonstrably more natural to
> read, convert it; if it is not, leave the passive in place.**

Before recording a finding, apply this test in order:

1. **Write out the active version.** Actually construct it; do not assume it will be better.
2. **Read both aloud.** Which one would a fluent native reader move through without pausing?
3. **Check what was gained.** The active version must deliver at least one of: a named actor where the
   actor matters, fewer words with no loss of meaning, better information flow, or a stronger verb.
4. **Check what was lost.** If the active version needs a vague or invented subject, a personal
   pronoun, buries the sentence's real topic, breaks the link to the previous sentence, or shifts the
   emphasis in a way the author did not intend, abandon the conversion.

If steps 3 and 4 do not clearly favour the active version, record no finding.

### No personal pronouns

Academic prose in this pipeline uses no first- or second-person pronouns (*I, we, our, us, my, you,
your*). A conversion that would need one is not available: the passive stays. The same applies to the
imperative and personal-address rewrites (Trigger 7): they remove personal pronouns, never add them.

### Counter-criteria — do not convert when any of these apply

If a counter-criterion applies, the passive stays, even when a trigger criterion (*Reference — Trigger
criteria*) also applies.

**A. The actor is unknown, irrelevant or deliberately unstated.** If you would have to invent a
subject, guess at one, or fall back on a vague placeholder (*someone*, *the relevant party*, *one*),
the passive is correct. If the actor is unknown and the reader needs it, that is an author query
(Action author), not an edit.

**B. The passive is the convention of the genre.** Methods sections (*Samples were incubated at
37 °C*), statutory drafting and formal definitions use the agentless passive by convention. Converting
these, typically into *The study…* or *The analysis…* as an artificial subject, makes the text read as
less professional. This is the most common way a voice pass goes wrong.

**C. The passive preserves the topic chain.** English prefers given information first and new
information last. If the grammatical subject is the topic carried over from the previous sentence,
converting breaks that thread.

**D. The passive keeps a long or heavy subject out of the way.** If the active version would open with
a long noun phrase before the verb, the passive is doing real work.

**E. The passive is in a direct quotation, a cited statutory provision or a verbatim extract.** Never
alter quoted or statutory text.

**F. The passive softens an attribution the author may have softened deliberately.** *Concerns have
been raised about the allocation* may be a deliberate choice not to name who raised them. If it reads as
evasion rather than discretion, that is an author query.

**G. The conversion would change terminology, add information not in the text, or alter the scope of
the claim.** The replacement carries exactly the same information as the original. Converting is a
syntactic operation, not a licence to add facts.

### Register calibration

The threshold shifts with the register (see *Reference — Register calibration table*). When in doubt
about which threshold applies to a passage, apply the more conservative one.

### Scope

Do not record findings for, or silently fix, any of the following. They belong to other passes.

- Sentence length, weak openers (*This/There/It*), rhythm → **Prose Polish Audit**
- Grammar, agreement, articles, prepositions → **ESL Fluency Audit**
- L1 transfer patterns → **L1 Interference Analysis**
- Word repetition → **Repetition Resolution**
- Content duplication → **DEDUP_MARKUP**
- Citation format, reference lists → **Citation Audit**
- Nominalisations that involve no passive verb (*the implementation of* → *implementing*)

**One bounded exception:** where converting a passive would leave the sentence grammatically broken
unless an adjacent word changes (an article, a preposition, or agreement with the new subject), make
that minimal adjustment as part of the conversion, and nothing beyond it.

A conversion must not create a sentence that opens with *This/These/There* + verb or a vague *It*:
those are Prose Polish's targets.

### When to stop and ask

- If the manuscript or range is missing, say so and wait.
- If the target language variant or the register has not been given (in the run parameters or earlier
  in the conversation), ask before beginning: the register changes the threshold.
- Otherwise, proceed: the Golden Rule, the criteria and the output format settle every other case.

---

## What done looks like

A findings table, one row per conversion, with these columns:

| Column | Content |
|---|---|
| `Location` | `§x.y, [n]`: section, then the paragraph label. The `[n]` label is the key. |
| `Original Text` | The exact clause or sentence containing the passive (or the imperative / personal address), copied verbatim from paragraph `[n]`: long enough to locate it once, no longer. |
| `Category` | One of the categories below. |
| `Severity` | Medium where the passive clearly weakens the sentence; Low where the gain is small. |
| `Suggestion` | The active (or impersonal) replacement for `Original Text`: grammatically complete, the same meaning, terminology, hedging and scope. For an author query, the question for the author instead. |
| `Remark` | The trigger met and what the conversion gains, in one sentence; for an author query, what the passive obscures. |

### Categories

- **ACTOR-KNOWN** (Trigger 1: agentless passive, actor known from context and needed)
- **BY-PHRASE** (Trigger 2: actor already named in a *by* phrase)
- **STACKING** (Trigger 3: passive stacking)
- **WEAK-VERB** (Trigger 4: inflated passive on a weak verb)
- **OBLIGATION** (Trigger 5: passive that obscures who is responsible)
- **DOUBLE-PASSIVE** (Trigger 6: two passives chained)
- **PERSONAL-ADDRESS** (Trigger 7: imperative, second- or first-person address)

**Author queries.** Where converting would need information only the author has (the actor is unknown
but the reader needs it; responsibility would be assigned to a party not stated; the passive may be
deliberate discretion; the same unattributed passive recurs as a pattern), record the finding with the
trigger's category and say in the Remark that the author must supply the actor. Each instance is either
a conversion or a query, never both.

### Self-check before submitting

1. Every `Original Text` is verbatim in the paragraph its Location names.
2. Every replacement keeps the exact meaning, scope, terminology and hedging: no facts added, none removed.
3. Every replacement is grammatically complete and could be pasted in without further editing.
4. No row converts an instance that meets a counter-criterion. Re-read the counter-criteria against the
   rows: this is where a voice pass most often overreaches.
5. No conversion introduces an invented or vague subject, or a personal pronoun.
6. No conversion breaks the topic chain with the preceding sentence or alters quoted text.
7. Every PERSONAL-ADDRESS rewrite removes the imperative or pronoun without adding another.

---

## Reference — Session parameters

**Target language variant: [SPECIFY: en-GB | en-US | other]** — applied to all lexical choices and
spelling in the replacement.

**Document register: [SPECIFY: academic | policy | legal | technical | general]** — changes the
intervention threshold; see the calibration table.

---

## Reference — Trigger criteria

Convert when the passive shows one or more of these, and the Golden Rule favours the active.

**1. Agentless passive where the actor is known and matters.** The sentence hides who acts, but the
actor is identifiable from context and the reader needs it.

> *The questionnaire is sent to trust administrators.* → *The Division sends the questionnaire to trust
> administrators.*

**2. `by`-phrase passive with the actor already named.** Converting usually shortens the sentence and
puts the actor where the reader expects it.

> *The report is compiled annually by the NAMC.* → *The NAMC compiles the report annually.*

**3. Passive stacking.** Two or more passives in one sentence, or three or more consecutive passive
sentences. Even where each instance is defensible, the accumulation flattens the prose. Apply the Golden
Rule to each instance: convert those where the active is better, and leave the rest.

**4. Inflated passive with a weak verb.** *is made*, *is given*, *is done*, *is carried out*, *is
undertaken*, *is provided*, *is conducted*, where a single active verb replaces the phrase.

> *A submission is made by the Division.* → *The Division submits.*

**5. Passive that obscures obligation or responsibility.** *Records must be kept* leaves it unclear who
is liable. Where the responsible party is identifiable, name it.

> *Records must be kept for five years.* → *Trust administrators must keep records for five years.*

**6. Double passive.** Two passives chained through an infinitive or participle.

> *The report is required to be submitted by the trustees.* → *The trustees must submit the report.*

**7. Imperative and personal address.** Commands to the reader and *you/we/I* in academic prose.
Rewrite impersonally, keeping the claim and its strength; prefer a real subject from the text over
a passive where one exists.

> *Consider the case of a producer who…* → *In the case of a producer who…*
> *As you can see in Table 4.2, …* → *As Table 4.2 shows, …*
> *We find that yields fell.* → *Yields fell.* / *The results show that yields fell.*

---

## Reference — Register calibration table

| Register | Threshold | Notes |
|---|---|---|
| `general`, `technical` | Low — convert where the active is better | Reader-facing prose benefits most from active voice |
| `academic` | Moderate — convert in introduction, literature review, results and discussion where the active is better; be conservative in methods | Methods-section passives are conventional (Counter-criterion B) |
| `policy` | Moderate — favour conversion in procedural passages, where naming the responsible party has practical value | Definitions and legal provisions stay passive |
| `legal` | High — convert only inflated and double passives (Triggers 4 and 6) | Statutory drafting convention dominates |
