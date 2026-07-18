<!--
DISCOVERY DECISION LEDGER — entry format + rules (ticket 020, ADR 0011)

This is NOT a standalone file template. It defines the "## Decisions" section
embedded in every ledger-bearing discovery artifact (wireframe files, design-system
docs, WoZ imports, grill-adjacent captures). Artifact templates (wireframe.md,
design-system.md) embed this section and inherit these rules.

Adapted from wizard_of_oz `contract:decision-entry` (cited snapshot, 2026-07-18,
wizard_of_oz/design/specs/decision-entry.yaml — grill Q1). One deliberate
adaptation: wizard_of_oz numbers D{NNN} globally because its ledger is a single
session file; archwright discovery artifacts are DISTRIBUTED, so numbering is
FILE-SCOPED and cross-file references are qualified (`<artifact-id>#D{NNN}`).
This preserves append-only monotonicity per file with no central counter to drift.
-->

## Decisions

<!-- ═══ ENTRY FORMAT — every field required ═══ -->

### D001 — Short decision title
- **Category:** structure          <!-- see CATEGORY ENUM below -->
- **Origin:** user                 <!-- user | suggested | inferred — see ORIGIN below -->
- **Decision:** What was decided, in one or two sentences.
- **Rationale:** "In the user's words, quoted verbatim — never paraphrased by the agent."
- **Alternatives:** What was considered and rejected, and why.

### D002 — A reversal example
- **Category:** structure
- **Origin:** user
- **Decision:** SUPERSEDES D001. The new decision text. <!-- cross-file: SUPERSEDES wf-title-screen#D003 -->
- **Rationale:** "Why the user changed their mind, verbatim."
- **Alternatives:** Keeping D001 as decided.

<!--
═══ CATEGORY ENUM (grill Q2) ═══
Core 5 — valid in every domain:
  scope       what's in/out of this version (the MLP filter generalizes)
  experience  what the user feels (generalizes wizard_of_oz's `aesthetic`)
  structure   layout, hierarchy, flow — the wireframe categories
  technical   platform constraints, implementation bounds
  meta        process, naming, conventions
Domain extensions — from the detected domain overlay's `discovery:` section
(tools/domains/<domain>/). Game extends with: mechanic, feedback, progression,
economy, content, narrative. Validator rule: category ∈ core ∪ detected-domain
extensions (enforced by ticket 026's discovery schema).

═══ ORIGIN TAXONOMY + GUARD CALIBRATION (grill Q4) ═══
  user       the human explicitly stated it
  suggested  the agent proposed it, the human accepted
  inferred   derived from context WITHOUT explicit confirmation — carries an
             obligation: surface for confirmation before the artifact graduates
             to `approved`. Unconfirmed inferred entries block graduation.

Guard strength follows session type — agreement with researched recommendations
is NEVER penalized:
  Creative sessions (wireframes, WoZ, brainstorm):
      strict tripwire — 3+ consecutive `suggested` → STOP and ask
      "what do YOU think should happen here?" (AI content displacing user
      creativity is the failure mode here)
  Grill-type sessions (options researched, human ratifies):
      periodic decision-surfacing instead — every ~5 decisions, batch-confirm
      in plain terms ("locked in so far: X, Y, Z — anything you'd steer
      differently?"). Summary, not interruption.

═══ LEDGER RULES (the wizard_of_oz core, unchanged) ═══
1. APPEND-ONLY. Entries are never edited, renumbered, or deleted. A changed
   mind is a NEW entry whose Decision begins `SUPERSEDES D{NNN}` (or
   `SUPERSEDES <artifact-id>#D{NNN}` across files). The superseded entry stays
   but is excluded from every projection.
2. ENTRIES ARE TRUTH — one repair direction. Counts, INDEX tables, briefs,
   model seeds, and force evidence are projections that regenerate FROM entries.
   On any disagreement the ledger wins; never invent entries to match a counter.
3. RATIONALE IS VERBATIM. The user's words, not the agent's summary — projections
   quote it directly, and it is the evidence text that graduates into force files.

═══ CITATION OBLIGATION (grill Q6 — conservation anchors) ═══
Every downstream transform consuming this ledger (model seeds, force evidence,
draft specs) MUST cite the entries it consumed as `<artifact-id>#D{NNN}`.
The conservation check verifies both directions:
  - nothing invented: every transform output element cites ≥1 entry
  - nothing lost: every ACTIVE (non-superseded) entry is either cited by an
    output or explicitly listed under "Unconsumed decisions" with a reason
An entry id is therefore load-bearing — it is the source anchor the whole
provenance chain hangs from.

═══ INDEX PROJECTION (per area, e.g. design/discovery/ui/INDEX.md) ═══
The area INDEX carries a regenerable summary table — a projection, never the truth:
| Entry | Artifact | Title | Category | Origin | Status |
|-------|----------|-------|----------|--------|--------|
| wf-title-screen#D001 | wf-title-screen.md | Skip title, drop into play | structure | user | active |
-->
