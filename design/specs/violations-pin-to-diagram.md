---
kind: constraint
id: violations-pin-to-diagram
from_patterns:
  - "pattern:behavior-first-front-door"
confidence: "★"
protects_experience: "exp-know-what-to-do"
user_story: "When something fails, the same map the reader already knows shows where — the diagram never disappears exactly when orientation matters most."
check:
  method: script
  target: "design/report/report.json"
  target_status: pending  # No generated bundle yet. Activates on first generation.
  command: >-
    python3 -c "import json,sys; d=json.load(open('design/report/report.json'));
    mv=d.get('model_view') or {}; asks=(d.get('asks') or {}).get('asks') or [];
    els={e['id'] for e in (mv.get('states') or []) + (mv.get('transitions') or [])};
    [print(f\"ask {a['ask_id']}: diagram_ref {a['diagram_ref']} not in model_view\")
     for a in asks if a.get('source',{}).get('kind')=='violation'
     and a.get('diagram_ref') and a['diagram_ref'] not in els];
    [print(f\"ask {a['ask_id']}: violation ask with no diagram_ref and no model_view fallback note\")
     for a in asks if a.get('source',{}).get('kind')=='violation'
     and not a.get('diagram_ref') and mv.get('front_door')=='behavior-diagram']"
  expect: absent
links:
  - target: "contract:model-view-block"
    type: enforces
  - target: "contract:asks-block"
    type: constrains
---

# Violations Pin to the Diagram

## Rule

In a generated bundle whose front door is the behavior diagram, every
violation-sourced ask carries a `diagram_ref` resolving to a `model_view`
element. The needs-attention page renders the SAME diagram with those elements
marked — never a separate list-only view.

## Rationale

`behavior-first-front-door` + the `fault-location-one-step` force
(wf-all-clear#D005): the behavior map is constant across report states; only
badges change. The rejected alternative — diagram only in all-clear — makes the
map disappear exactly when orientation matters most. The check is a structural
join over the bundle: pins must resolve, and violation asks must be pinned when
a diagram exists (script convention: output = violations, exit per grep rules).

## Violations Look Like

```json
{ "ask_id": "a1b2…", "source": {"kind": "violation"}, "diagram_ref": null }
```
(with `model_view.front_door == "behavior-diagram"` — an unpinned violation)

## Correct Usage

```json
{ "ask_id": "a1b2…", "source": {"kind": "violation"}, "diagram_ref": "taking-payment" }
```
