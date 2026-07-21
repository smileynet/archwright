---
kind: constraint
id: allclear-discloses-gaps
from_patterns:
  - "pattern:honest-all-clear"
confidence: "★★"
protects_experience: "exp-honest-green"
user_story: "A green page still tells you what it couldn't check and what debt was accepted — trust comes from disclosed limits."
check:
  method: script
  target: "design/report/report.json"
  target_status: pending  # Targets the generated bundle (design/report/, gitignored) — absent on fresh clones. Enforced both-directions in the fixture suite against a suite-generated bundle (ticket 041).
  command: >-
    python3 -c "import json; d=json.load(open('design/report/report.json'));
    gaps=(d.get('skips') or []) or (d.get('baseline_entries') or []);
    posture=(d.get('asks') or {}).get('posture') or d.get('posture');
    html=open('design/report/report.html', encoding='utf-8').read();
    (posture=='all-clear' and gaps and
     ('what isn't verified' not in html.lower() and 'couldn\\'t be checked' not in html.lower())
     and print('all-clear page with skips/baseline entries but no disclosure section'))"
  expect: absent
links:
  - target: "contract:model-view-block"
    type: constrains
---

# All-Clear Discloses Its Gaps

## Rule

Whenever the canonical document carries skips, pendings, or baseline entries
and the posture is all-clear, the rendered page contains the disclosure
sections ("what isn't verified" / accepted known issues) on the surface — never
folded, never omitted.

## Rationale

`honest-all-clear` + the `gaps-share-the-verdict` force (wf-all-clear#D002):
this project's own vacuous-pass history is the evidence — checks that couldn't
run read as checks that passed, for months. Omitting the disclosure is a
generation bug, not a styling choice. Skips render as coverage statements
("couldn't be checked"), never as passes.

## Violations Look Like

A `report.json` with `skips: [...]` or baseline entries, posture all-clear, and
a `report.html` containing only the verdict and diagram — no unverified/debt
sections.

## Correct Usage

The wf-all-clear wireframe: verdict line, diagram, then unfolded
`WHAT ISN'T VERIFIED` (with reasons) and accepted-issues (with dates and cost)
sections at the same prominence as verified content.
