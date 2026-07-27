---
kind: discovery
id: wf-screen-slug            # file: design/discovery/ui/wf-<screen-slug>.md
status: proposed              # proposed | approved | superseded (026 schema enforces)
area: ui
serves: []                    # bare force ids this screen serves (resolve against design/forces/)
supersedes: ""                # optional: id of the wireframe this replaces
---

# Wireframe: Screen Name

<!-- One file per screen/view state. Decisions recorded per tools/templates/discovery-ledger.md
     (file-scoped D{NNN}; cross-file refs as `wf-screen-slug#D{NNN}`). This artifact is
     EVIDENCE — the decisions are the deliverable that graduates (ADR 0011). -->

## Wireframe

```
+----------------------------------------------------------+
|  [logo]   Screen Title                        (o) profile |
+----------------------------------------------------------+
|                                                          |
|   +------------------+   +---------------------------+   |
|   | primary content  |   |  secondary panel          |   |
|   +------------------+   +---------------------------+   |
|                                                          |
|                [ Primary Action ]                        |
+----------------------------------------------------------+
```

<!-- Show FIRST, then ask (facilitation stance §4). Early wireframes end with a
     direction check before any detail question. Legend grows per session. -->

## Design-System Elements Used

<!-- CONSERVATION: every table row must cite ≥1 ledger anchor (D{NNN} or artifact#D{NNN}).
     The validator enforces this — rows without citations FAIL.
     Example: "| `accent_green` | design-system#D001 | Progress fill color | D003 |" -->

| Element | From design-system | Usage here | Anchor |
|---------|-------------------|------------|--------|
| (token/component id) | design-system#D00N | (how it appears on this screen) | D001 |

## Layout Rationale

Why THIS arrangement — the choice made, in terms a non-technical reviewer can follow. Name the alternative arrangements considered (they also appear in the ledger's Alternatives fields).

## Decisions

<!-- Format + rules: tools/templates/discovery-ledger.md (append-only, origin recorded,
     rationale verbatim, SUPERSEDES for reversals). Creative session → strict
     rubber-stamp guard (3+ consecutive `suggested` → stop and ask).

     VALID CATEGORIES — core: experience, meta, scope, structure, technical
     Game domain extensions: mechanic, feedback, progression, economy, content, narrative
     Web domain extensions: see tools/domains/web/discovery.yaml
     "interaction" is NOT a valid category — use "experience" or "mechanic" instead. -->

### D001 — Decision title
- **Category:** structure
- **Origin:** user
- **Decision:** …
- **Rationale:** "…"
- **Alternatives:** …

## Not Resolved Here

<!-- The artifact gap (ADR 0011 Decision 5) — what wireframes deliberately omit.
     NEVER delete this section; an empty gap list is a claim, not a default.
     This list compiles into the model phase's TODO. -->

- [ ] States: (loading / empty / error / partial for this screen)
- [ ] Edge cases: (overflow, long text, zero items, permissions)
- [ ] Interaction rules: (validation, focus, keyboard, touch targets)
- [ ] Transitions: (how the user arrives here / leaves; animation intent)

## Hands To

<!-- Model-phase seed. Every claim cites its D{NNN} anchor (grill Q6 — conservation:
     downstream transforms must cite these; unconsumed decisions get listed with reason). -->

- **Flow edges:** (from-screen) → this screen on (event) [cites D00N]
- **State owned/shown:** (data visible or entered here) [cites D00N]
- **Events emitted:** (what user actions here mean to the system) [cites D00N]
