# Q4: Do grill sessions adopt the ledger format?

**Status:** Decided 2026-07-18
**Decision:** Option C — field-level unification, with the rubber-stamp guard recalibrated for grill context (operator caveat: agreement with recommendations is normal, not a violation).

## Question

Should grill-with-docs sessions restructure their Q-files into decision-ledger format, keep their format, or adopt the ledger's fields?

## Research / Live Evidence

- Q-files are richer than ledger entries (embedded research, options tables, implications) and field-proven; full format adoption would flatten them.
- What Q-files lacked: origin taxonomy, the rubber-stamp guard, supersession discipline — demonstrated live when Q1–Q3 of this very session were all `origin: suggested` and nothing counted them.
- Operator refinement on the guard: in a grill, the entire format is research → recommendation → decide. **Accepting a well-researched recommendation is the system working, not agency erosion.** The wizard_of_oz guard targets creative sessions where the AI filling blanks displaces the user's design; a grill recommendation is prepared analysis, not creative substitution.

## Decision Detail

1. **Origin recorded** on every grill decision (`user | suggested | inferred`) — measurement is free and honest.
2. **Guard recalibrated for grills:** no tripwire on consecutive `suggested`. Instead, periodic **decision surfacing** (the other facilitated-agency mechanism): every ~5 decisions, batch-confirm in plain terms ("locked in so far: X, Y, Z — anything you'd steer differently?"). Fires as a summary, not an interruption; never implies agreement is wrong.
3. **Tripwire retained where it belongs:** artifact-producing creative sessions (wireframes, WoZ, brainstorms) keep the strict 3+-consecutive-suggested guard — there, AI-originated content displacing user creativity is the actual failure mode.
4. **Supersession discipline:** re-grilling a decided question appends (`SUPERSEDES Q{n}` row + new Q-file section), never edits history.
5. Q-file structure otherwise unchanged; a Q-file decision row is semantically a ledger entry (tooling can read both).

## Implications

- Grill INDEX decision tables gain an `origin` column (this session's INDEX adopts it from Q5 forward; Q1–Q3 retroactively: suggested, suggested, suggested; Q4: suggested-amended).
- T2 ledger template documents the two guard calibrations (grill vs creative session).
- The facilitation-stance reference (T1) carries the distinction: guard strength follows session type.
