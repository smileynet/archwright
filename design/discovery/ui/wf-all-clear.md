---
kind: discovery
id: wf-all-clear
status: approved
area: ui
serves: []
---

# Wireframe: All-Clear Overview (cold-reader view)

<!-- The overview's state when no decisions or approvals are waiting — job J2's
     primary case. Behavior-first per design-system#D006: the diagram of how the
     app works IS the front door; verification and rationale are drill layers. -->

## Wireframe

```
+---------------------------------------------------------------------------+
| Snackbox — Design Check                       checked 2 min ago · a1b2c3d |
+---------------------------------------------------------------------------+
|                                                                           |
|   ✓  All clear — the app behaves as designed                              |
|                                                                           |
|   HOW SNACKBOX WORKS ---------------------------------------------------- |
|                                                                           |
|                    insert coins                                           |
|      ( Waiting ) ──────────────▶ ( Taking payment )                       |
|          ▲                            │                                   |
|          │                            │ paid in full                      |
|          │  snack delivered           ▼                                   |
|          ├────────────────── ( Dispensing ✓ )                             |
|          │                                                                |
|          │  money returned                                                |
|          └────────────────── ( Cancelled )                                |
|                                    ▲                                      |
|                          cancel pressed (from Taking payment)             |
|                                                                           |
|   every step verified ✓ · click any step or arrow for details            |
|                                                                           |
|   WHAT ISN'T VERIFIED ---------------------------------------------------- |
|   ○ 2 rules can't be checked yet (hardware simulator missing)            |
|   ⚠ 3 known issues accepted on 2026-07-12  ▸ what they cost              |
|                                                                           |
|   STABILITY --------------------------------------------------------------|
|   rules holding 12 runs straight · last failure 2026-07-11               |
|   💡 1 guideline has earned trust (12 straight passes)                    |
|      ▸ consider making it a firm rule                                    |
+---------------------------------------------------------------------------+
```

When items need attention (wf-overview state), the same diagram appears with the
affected step/arrow marked ✗ — the diagram is the map violations pin to.

## Design-System Elements Used

| Element | From design-system | Usage here |
|---------|-------------------|------------|
| Behavior-first IA | design-system#D006 | diagram is the front door; drill = behavior → rules → rationale |
| Plain-language surface | design-system#D002 | state/event names in everyday words ("Taking payment", "cancel pressed") |
| Status chip | design-system (P4) | per-step verification badges on the diagram |
| Ask-type framing | design-system#D003 | trust nudge stays optional (suggestion) |

## Layout Rationale

The diagram answers "what does this app do?" before any check vocabulary appears —
a non-technical reader follows states and arrows as a story of the machine's life.
Verification results attach to the thing they verify (badges on steps) instead of
living in a separate list. The disclosure sections (what isn't verified, stability)
stay on the surface below the diagram. Rendered as pre-generated inline SVG at
report-build time — no client-side diagram library, preserving the zero-build
single-file principle (P5). Alternatives: promise-grouped list (superseded — D004);
diagram behind a tab (rejected — it IS the front door per design-system#D006).

## Decisions

### D001 — Group the all-clear view by promise (goal), not by rule
- **Category:** structure
- **Origin:** suggested
- **Decision:** Passing rules roll up under the product goal they protect; the goal's own phrasing is the row title.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Flat rule list; grouping by spec kind; grouping by code area.

### D002 — "What isn't verified" disclosure is mandatory in all-clear
- **Category:** experience
- **Origin:** suggested
- **Decision:** The all-clear view always discloses unchecked rules and accepted issues with the same prominence as the verified content — never hidden behind a fold.
- **Rationale:** "agree on both" (user approval of researched recommendation, 2026-07-19 — evidence: the project's own vacuous-pass history; unchecked = coverage statement, not a pass)
- **Alternatives:** Fold gaps behind "details" (rejected — an all-green verdict that hides blind spots overstates trust).

### D003 — Third ask-type: optional suggestions
- **Category:** experience
- **Origin:** suggested
- **Decision:** Extends design-system#D003's taxonomy: SUGGESTIONS are optional, non-blocking asks. They never change the all-clear verdict and never auto-execute.
- **Rationale:** "agree on both" (user approval of researched recommendation, 2026-07-19 — without the tier, trust nudges block all-clear or vanish; alarm-fatigue risk)
- **Alternatives:** Treating trust nudges as decisions; dropping them from the report.

### D004 — Behavior diagram is the all-clear front door
- **Category:** structure
- **Origin:** user
- **Decision:** SUPERSEDES D001. The all-clear surface leads with the app's state machine as a plain-language diagram (applies design-system#D006); verification badges attach to diagram elements; promise-grouping moves into the drill (a step's details list the goals it serves). Disclosure sections (unverified, stability) remain on the surface below.
- **Rationale:** "I want to understand what does the app do. The state machine / business logic are core to how the app functions. even a non-technical user should be able to look at the diagram and understand how things will behave."
- **Alternatives:** Promise-grouped surface (D001, superseded); diagram-as-drill (inverted priority).

### D005 — Violations pin to the diagram
- **Category:** structure
- **Origin:** suggested
- **Decision:** In needs-attention states, the same diagram renders with the affected step/arrow marked ✗ — the behavior map is constant across report states; only the badges change.
- **Rationale:** "yes" (user approval of the presented front-door ensemble, 2026-07-19)
- **Alternatives:** Diagram only in all-clear (map disappears exactly when orientation matters most); separate "affected areas" list.

## Not Resolved Here

- [ ] States: first-ever run (no history), empty project, tool-error variant, multi-actor projects (several state machines — which leads? tabs? composition view?)
- [ ] Edge cases: large machines (15+ states), machine with unnamed/technical state labels, project with no behavior model at all (constraint/dependency rules only — what's the front door then?)
- [ ] Interaction rules: diagram click targets, keyboard access to diagram elements, SVG accessibility (roles/labels)
- [ ] Transitions: diagram element → behavior detail anchor

## Hands To

- **Flow edges:** all-clear surface → behavior detail per step/arrow (wf-behavior-detail); suggestion → trust decision card [cites D004, D003]
- **State owned/shown:** model states/transitions with plain-language labels + per-element verification rollup (requires spec → model-element join), skip/pending reasons, baseline entries, streaks [cites D004, D005, D002]
- **Events emitted:** open behavior detail(element), open suggestion, dismiss suggestion [cites D004, D003]
