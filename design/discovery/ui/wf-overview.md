---
kind: discovery
id: wf-overview
status: approved
area: ui
serves: []
---

# Wireframe: Report Overview

## Wireframe

```
+---------------------------------------------------------------------------+
| Snackbox — Design Check                       checked 2 min ago · a1b2c3d |
+---------------------------------------------------------------------------+
|                                                                           |
|   1 decision needs you · 2 approvals waiting          auto-approve: off  |
|                                                                           |
|   DECISIONS (1) --------------------------------------------------------- |
|                                                                           |
|   ?  "Refunds happen on cancel" keeps failing — is the rule right?       |
|      This rule has failed 4 runs in a row; the fix was deferred twice.   |
|      Pick one:                                                            |
|        (•) Keep the rule — fix the code now          ← recommended       |
|        ( ) Amend the rule — refunds allowed to batch overnight           |
|        ( ) Accept as a known issue for now                               |
|        ( ) Something else: [________________________________]           |
|      ▸ why we recommend this                                             |
|      ▸ history · why this rule exists                                    |
|                                                                           |
|   APPROVALS (2) --------------------------------------------------------- |
|                                                                           |
|   ✗  Snacks can be dispensed without payment            [firm rule]      |
|      The design says:  dispensing only happens inside a paid session.    |
|      The code does:    src/dispenser.py:41 calls dispense() directly.    |
|      Recommended: fix the code.                     [ Approve Fix ]      |
|                                                                           |
|   ✗  Screen code reaches into the coin hardware         [strong guide]   |
|      The design says:  UI never talks to hardware directly.              |
|      The code does:    src/kiosk_ui.py:12 imports hardware.coin_acceptor |
|      Recommended: fix the code.                     [ Approve Fix ]      |
|                                                                           |
|   THE REST -------------------------------------------------------------- |
|   ✓ 41 rules pass   ⚠ 3 accepted   ○ 2 unchecked   (each expands below)  |
|                                                                           |
+---------------------------------------------------------------------------+
|  3 responses recorded                     [ Save responses for the agent ]|
+---------------------------------------------------------------------------+
```

The bottom bar appears once any control is used (design-system#D005): choices
accumulate in the page and export as one structured response file the agent
processes. Nothing is sent anywhere — the file is the handoff.

With auto-approve ON (`mise.local.toml`), the APPROVALS section collapses to a log
line: `2 fixes auto-approved (see log)` — DECISIONS never collapse.

## Decision situations (what lands in DECISIONS)

Enumerated from existing machinery — each is ambiguity the system cannot resolve alone:

| Situation | Source signal | Ask shape |
|-----------|--------------|-----------|
| Rule vs code conflict — repeated failure suggests the rule may be wrong | recurring FAIL + deferred fixes / fix-spec route | options: keep rule / amend rule / accept debt |
| Firm-rule violation with design implications | escalate: true surviving research gate | recommendation + explicit sign-off, options if contested |
| Trust change on a rule | evidence-ledger promotion/demotion candidate | "this guideline passed N runs — trust it more?" yes/no/later |
| Accepting new known debt | proposed baseline entry | accept/reject with the debt's cost stated |
| Unchecked rule worth checking | persistent skip/pending | build the checker / accept the gap |
| Ambiguous route | contrast pair doesn't determine code-vs-design | options + freeform + best-effort recommendation with its confidence stated (D005) |

## Design-System Elements Used

| Element | From design-system | Usage here |
|---------|-------------------|------------|
| Approvals/decisions split | design-system#D003 | two zones; verdict line counts each |
| Auto-approve indicator | design-system#D004 | header shows current setting; approvals collapse when on |
| Plain-language surface | design-system#D002 | all copy; options phrased in product terms |
| Contrast-pair card body | (wf-overview#D002) | approval cards |
| Status chip | design-system (P4) | ✗/?/✓ glyphs + words |

## Layout Rationale

Decisions before approvals: decisions are rarer, heavier, and blocking — they're why a human opened the report; approvals are the routine queue below (and vanish entirely under auto-approve). The verdict line counts both ask-types separately so the reader knows the shape of their session before scrolling. Alternatives: approvals-first (rejected — buries the judgment calls under routine); merged list with badges (rejected — D003).

## Decisions

### D001 — Verdict-first, card-per-issue overview
- **Category:** structure
- **Origin:** suggested
- **Decision:** The overview opens with a one-line plain verdict, then one card per issue needing attention; inventory/coverage stats are demoted to an expandable "the rest" strip at the bottom.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Stat-dashboard-first; columnar violations table.

### D002 — Contrast pair as the card body
- **Category:** structure
- **Origin:** suggested
- **Decision:** Each issue card's body is the contrast pair phrased as "The design says: … / The code does: …" followed by one action line.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Raw invariant message + route enum; evidence-lines-first (grep output style).

### D003 — Two-zone overview: decisions above approvals
- **Category:** structure
- **Origin:** user
- **Decision:** SUPERSEDES D001's single "needs attention" zone. The overview splits into DECISIONS (judgment calls, never auto-resolved) above APPROVALS (clear-answer sign-offs with a recommendation and an approve control), then "the rest". Verdict line counts each ask-type. Applies design-system#D003/#D004.
- **Rationale:** "both needs attention cases appear to have a clear right answer, these should be framed as 'approvals needed' and it should be configuratble via local mise settings to auto-approve (off by default). consider situations where user needs to make decision/ resolve ambiguity."
- **Alternatives:** Single zone with badges; approvals-first ordering.

### D004 — Decision cards present options, not recommendations, when ambiguous
- **Category:** experience
- **Origin:** suggested
- **Decision:** A decision card states the situation in one sentence, then 2–3 concrete options in product language (keep rule / amend rule / accept for now). Where research supports a recommendation it is marked as such; genuinely ambiguous items present options only.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Free-text prompt ("what do you want to do?"); always-recommend (rejected — leading on judgment calls).

### D005 — Decision cards: options + freeform + marked recommendation + rationale fold-out
- **Category:** experience
- **Origin:** user
- **Decision:** SUPERSEDES D004. Every decision card offers: the multiple-choice options, a freeform "something else" input, a clearly indicated recommendation among the options, and a fold-out revealing the rationale behind the recommendation.
- **Rationale:** "there should be freeform input for multiple choice entries for user, as well as a clearly indicated recommendation. a fold out should show the user the rationale."
- **Alternatives:** Options-only without recommendation on ambiguous items (superseded D004); recommendation without exposed rationale (rejected — user must be able to audit the reasoning); freeform-only prompt.

### D006 — Response accumulation bar
- **Category:** structure
- **Origin:** suggested
- **Decision:** A bar (bottom of page) appears once any control is used, counting recorded responses, with one action: save the structured response file for the agent. Applies design-system#D005.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Per-card immediate export (rejected — one file per decision is agent-hostile); auto-save to browser storage only (no visible handoff moment).

## Not Resolved Here

- [ ] Response-file format: schema, where it lands, how the agent discovers it (technical spec, not a screen concern) — mechanics direction settled by design-system#D005
- [ ] Auto-approve config shape: exact mise variable name/values; whether scoped (e.g. code-fixes only)
- [ ] States: all-green, no-decisions-only-approvals, tool-error, empty project
- [ ] Edge cases: 100+ approvals, decision with >3 options, conflicting decisions
- [ ] Interaction rules: keyboard nav, what selecting a decision option records
- [ ] Transitions: card "details" target (inline vs detail view) — still open from v1

## Hands To

- **Flow edges:** (entry) → overview; overview → issue detail via "details"; overview → decision detail via "history" [cites D003]
- **State owned/shown:** verdict counts per ask-type; per-approval contrast_pair + recommendation + confidence phrase; per-decision situation + options; auto-approve setting state [cites D003, D004]
- **Events emitted:** approve-fix(item), choose-option(decision, option), freeform-response(decision, text), reveal-rationale(decision), expand bucket [cites D003, D004, D005]
