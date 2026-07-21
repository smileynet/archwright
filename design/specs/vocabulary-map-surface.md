---
kind: constraint
id: vocabulary-map-surface
from_patterns:
  - "pattern:plain-surface-progressive-disclosure"
confidence: "★"
protects_experience: "exp-glance-verdict"
user_story: "A cold reader never meets methodology jargon on the surface — internal terms live one fold down."
check:
  method: grep
  target: "tools/report/templates/"
  target_status: pending  # Report templates don't exist yet. Activates when they land; packaging decision (ships-with-core vs separate tool) may relocate the target.
  pattern: "remaining_delta|baselined|fix-implementation|fix-spec|fix-check|evidence_ledger|from_force|from_pattern"
  include: ["*.html", "*.j2", "*.tmpl"]
  exclude: ["disclosure", "detail-fold"]
  expect: absent
links:
  - target: "contract:vocabulary-map"
    type: enforces
---

# Internal Vocabulary Stays Off the Surface

## Rule

Surface-layer template files contain no internal-vocabulary tokens (check-output
field names, route enums, methodology terms). Internal terms may appear only in
disclosure-layer partials (files under `disclosure`/`detail-fold` paths), which
render inside `<details>` folds.

## Rationale

`plain-surface-progressive-disclosure`: the surface reads in product language
via the vocabulary map (design-system#D002); precision stays reachable one fold
down. A raw internal token on the surface means a template bypassed the map —
the exact failure the token-table architecture exists to prevent.

Per R1 (exclude analysis): the alternation matches all occurrences; disclosure
partials are the legitimate use, excluded by path substring. On activation,
inspect every match and extend `exclude` only with genuine disclosure partials.

## Violations Look Like

```html
<!-- BAD — canonical-doc field name rendered on the surface: -->
<p>remaining_delta: {{ doc.remaining_delta }}</p>
```

## Correct Usage

```html
<!-- GOOD — vocabulary-map phrase on the surface, term inside the fold: -->
<p>{{ vocab["remaining_delta"] }}: {{ doc.remaining_delta }}</p>
<details class="detail-fold"><summary>check internals</summary> remaining_delta … </details>
```
