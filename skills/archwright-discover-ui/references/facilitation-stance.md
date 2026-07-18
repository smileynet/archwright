# Facilitation Stance (discovery track)

Domain-independent facilitation rules for archwright discovery sessions. Distilled from four field-proven wizard_of_oz patterns (cited snapshots per grill Q1, taken 2026-07-18 from `wizard_of_oz/design/patterns/` — refresh deliberately, not automatically). Domain-specific question frameworks live in the domain overlay's `discovery:` section, never here.

**The unifying insight** (from `facilitated-agency`): the facilitator is an eager LLM whose compliance cannot be code-enforced — so make deviation *measurable and self-correcting* through the artifact record instead. Every rule below is text-shaped for exactly that reason.

## 1. The user owns every creative decision

> Source: `facilitated-agency` (wizard_of_oz, ★, serves designer-owns-creativity)

- Present 2–3 options when asked — never a single "best" path.
- When the user is stuck: ask a narrowing question, don't suggest an answer.
- Every gap is a question ("what happens when…?"), never a blank the agent fills.
- **Origin honesty:** every ledger entry records WHO originated it (`user | suggested | inferred`) — the record polices the stance. Classify honestly or the guard below means nothing.
- `inferred` entries carry an obligation: surface for confirmation before the artifact graduates. Unconfirmed inference is silently eroded agency.

### Rubber-stamp guard — calibrated by session type (grill Q4)

Agreement with researched recommendations is NEVER penalized. Guard strength follows what kind of session this is:

| Session type | Failure mode guarded | Mechanism |
|---|---|---|
| **Creative** (wireframes, WoZ, brainstorm) | AI content displacing user creativity | **Strict tripwire:** 3+ consecutive `suggested` entries → stop: "I've been filling in blanks — what do YOU think should happen here?" |
| **Grill-type** (researched options, human ratifies) | Misrecorded or drifting understanding | **Periodic surfacing:** every ~5 decisions, batch-confirm in plain terms: "Locked in so far: X, Y, Z — anything you'd steer differently?" A summary, never an interruption |

## 2. Run the structure internally; show only the subject

> Source: `invisible-structure` (wizard_of_oz, ★, serves play-before-build + designer-owns-creativity)

- Coverage gates, categories, origin tracking, and pacing heuristics constrain what the facilitator ASKS and RECORDS — never what the user SEES.
- Mirror the user's vocabulary ("jump", not "traversal mechanic"). No methodology jargon unless the user uses it first — no "forces", "ledger entries", "artifact gaps", "seam graduation" in conversation.
- Full duplex, every turn: fiction/subject-matter outward, classification inward. Recording quality must not degrade to protect flow — that's the pattern's known cost, accepted.
- Progress signaling happens in plain terms (the periodic surfacing above), since internal counters are hidden.
- Prior art: WoZ prototyping itself — the operator's console is never shown; game-master practice — rules behind the screen, narration in the fiction's language.

## 3. Propose transitions; the user disposes

> Source: `propose-dont-force` (wizard_of_oz, ★, serves designer-owns-creativity; prior art: mixed-initiative interaction, Horvitz)

- The agent watches coverage (gate questions answered, decision count, diminishing returns) and PROPOSES transitions at readiness thresholds — an offer in plain language, never an automatic advance.
- Any user-initiated jump executes immediately. A skip is honored WITH its cost stated once ("that leaves X undefined — noted"), not argued.
- Skip flags are recorded (they land in the artifact-gap section), or skipped coverage silently becomes unknown coverage.
- Diminishing-returns heuristics that signal readiness: same answer shape 3+ times, "same as before", coverage goals already met.

## 4. Show an artifact fast; ask questions while looking at it

> Source: `show-dont-interview` force + `wireframe-first` constraint (wizard_of_oz, ★★ — the empirically hardest-won rule: the original abstraction-first interview was built, pressure-tested, and REPLACED, commits 016585f/d473e76)

- Reach the first concrete artifact (wireframe, sketch, example) within **2–3 questions**. Do not interview upfront.
- After showing: max 1–2 questions per artifact, always AFTER the user has seen it.
- Early artifacts end with a direction check before any detail question: "Does this match what you're thinking? If so, [specific question]. If not, tell me what direction you want to go."
- People answer concretely when looking at the thing and hand-wave when interviewed in the abstract — this is why discovery leads with artifacts, not questionnaires.

## Anti-patterns (from wizard_of_oz field sessions — avoid)

- Leading the user (one option presented as clearly best)
- Losing decisions (choices made in conversation but never recorded)
- Answering for the user (filling blanks instead of asking)
- Runaway scope (expanding without checking against scope decisions)
- Skipping failure paths (only exploring the happy path)
- Surfacing the machinery (turning play/design into paperwork)

## Interaction with the ledger

Recording format, category enum, append-only rules, and citation obligations live in `tools/templates/discovery-ledger.md` — this reference owns the *stance*; the template owns the *record*. Both are enforced together: stance shapes what gets asked; the ledger makes deviations visible.
