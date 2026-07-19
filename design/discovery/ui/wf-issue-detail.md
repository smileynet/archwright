---
kind: discovery
id: wf-issue-detail
status: approved
area: ui
serves: []
---

# Wireframe: Issue Detail

<!-- In a single-file static report (design-system#D005) this is an in-page
     section reached by anchor from an overview card — same layout whether
     the source card was an approval or a decision. -->

## Wireframe

```
+---------------------------------------------------------------------------+
|  ← back to overview                                                       |
|                                                                           |
|  ✗  Snacks can be dispensed without payment              [firm rule]     |
|                                                                           |
|  The design says:  dispensing only happens inside a paid session.        |
|  The code does:    calls dispense() outside any session.                 |
|                                                                           |
|  WHERE ----------------------------------------------------------------- |
|    src/dispenser.py:41                                                    |
|      39 |  def request(self, item):                                       |
|      40 |      if self.stock[item] > 0:                                   |
|    > 41 |          self.dispense(item)          ← flagged                 |
|      42 |      return False                                               |
|    (+ 2 more locations ▸)                                                 |
|                                                                           |
|  WHY THIS RULE EXISTS --------------------------------------------------- |
|    Because:  "Customers must pay before receiving snacks."     (the goal)|
|    Decided:  payment gate — all dispensing goes through a paid           |
|              session (decided 2026-07-15)                    (the design)|
|    So:       this rule watches every dispense call            (the check)|
|    ▸ read the full design note                                            |
|                                                                           |
|  WHAT WE RECOMMEND ------------------------------------------------------ |
|    Fix the code: route request() through the payment session.            |
|    ▸ why we recommend this                                                |
|                            [ Approve Fix ]  [ Review / Amend Rule → ]    |
|                                                                           |
|  HISTORY ---------------------------------------------------------------- |
|    first seen this run · rule has held for 12 prior runs                  |
+---------------------------------------------------------------------------+
```

## Design-System Elements Used

| Element | From design-system | Usage here |
|---------|-------------------|------------|
| Plain-language surface | design-system#D002 | chain phrased as goal/design/check, no methodology terms |
| Contrast-pair body | wf-overview#D002 | header repeats the card's pair |
| Provenance breadcrumb | design-system | "why this rule exists" — force › pattern › spec chain, in plain words with disclosure to full docs |
| Recommendation + rationale fold-out | wf-overview#D005 | recommend section |
| Response recording | design-system#D005, wf-overview#D006 | approve/reroute controls feed the response file |

## Layout Rationale

Top-to-bottom mirrors the triage question order: what's wrong → where exactly (code with context) → why the rule exists (the design chain, phrased as goal/design/check — a cold reader learns the methodology implicitly, never by name) → what to do → how stable this rule has been. The "It's the rule →" escape reroutes the item from approval to a decision card (the rule may be wrong) without leaving the page. Alternatives: tabbed detail (SonarQube Where/Why style) — rejected for a static page, vertical scan is simpler; evidence-first layout — rejected, the verdict sentence must lead.

## Decisions

### D001 — Goal/design/check chain phrasing
- **Category:** structure
- **Origin:** suggested
- **Decision:** The provenance chain renders as three plain lines — Because (the goal, quoting the force's desire), Decided (the design decision + date), So (what the check watches) — each linking to the underlying document.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Breadcrumb of artifact ids (jargon); omit chain from detail (loses the "is the rule right?" context).

### D002 — Escape hatch: reroute approval → decision
- **Category:** structure
- **Origin:** suggested
- **Decision:** Every approval detail carries an "It's the rule" control that reclassifies the item as a decision (rule may be wrong), recording that reroute in the response file.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Freeform-only disagreement; requiring the user to leave the report and open a conversation.

### D003 — Action labels state intent: "Approve Fix" / "Review / Amend Rule"
- **Category:** experience
- **Origin:** user
- **Decision:** SUPERSEDES D002's control label. The two detail actions are labeled by the intent they carry: "Approve Fix" (accept the recommended code fix) and "Review / Amend Rule" (reclassify — the rule itself needs review). No idiom labels like "It's the rule".
- **Rationale:** "IT should be 'Approve Fix' or something that is more indicative of intent 'Review / Amend Rule' or something"
- **Alternatives:** "It's the rule →" (superseded — cute but not self-describing); icon-only controls.

## Not Resolved Here

- [ ] States: multi-location issues (n locations pager), behavior-trace violations (no file:line — a trace excerpt instead), skipped/pending rule detail variant
- [ ] Edge cases: chain missing links (spec without pattern/force), very long design notes, no history data (first run ever)
- [ ] Interaction rules: code-context depth (±2 lines?), keyboard next/prev issue
- [ ] Transitions: anchor navigation behavior, scroll restore on back

## Hands To

- **Flow edges:** overview card → this section (anchor); back → overview; "It's the rule" → decision card for same item [cites D002]
- **State owned/shown:** evidence lines + code context, provenance chain (from_force, from_pattern, spec), recommendation + rationale, history (pass-streak from evidence ledger) [cites D001]
- **Events emitted:** approve-fix(item), reroute-to-decision(item), open design note [cites D002]
