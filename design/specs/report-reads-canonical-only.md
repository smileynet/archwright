---
kind: dependency
id: report-reads-canonical-only
from_patterns:
  - "pattern:canonical-doc-projections"
confidence: "★★"
protects_experience: "exp-loop-closes"
user_story: "The report could be rebuilt by any tool from the public JSON alone — nothing the human sees depends on checker internals."
check:
  method: grep
  target: "tools/report/"
  pattern: "import archwright|from archwright|archwright_check|archwright_common|import derive_static|check_static"
  include: ["*.py"]
  exclude: ["templates/"]
  expect: absent
links:
  - target: "contract:model-view-block"
    type: constrains
  - target: "contract:asks-block"
    type: constrains
---

# Report Reads the Canonical Document Only

## Rule

Report code (`tools/report/`) never imports checker modules
(`archwright_common`, check internals). Its only inputs are the CK-03 JSON
document, `design/` YAML files (models, vocabulary), and environment config.

## Rationale

Packaging decision (2026-07-21, ticket 041): the report ships in core, but
keeps the separation DISCIPLINE — it must remain buildable by an independent
tool from the public interchange document alone (SARIF model). This dependency
rule is what makes later extraction cheap and proves
`canonical-doc-projections` structurally: a report that reaches into checker
internals could show humans information absent from the canonical JSON.

## Forbidden

- `tools/report/*` → `archwright-check.py` internals (any import)
- `tools/report/*` → `archwright_common`

## Allowed

- `tools/report/*` → CK-03 JSON document (file input)
- `tools/report/*` → `design/models/*.yaml`, vocabulary YAML (file inputs)
- Invoking `archwright-check.py` as a SUBPROCESS at the CLI boundary (consumes
  its public output, not its internals)

## Violations Look Like

```python
# BAD — reaching into checker internals:
from archwright_common import state_events
```

## Correct Usage

```python
# GOOD — consuming the public document:
doc = json.loads(Path(args.check_json).read_text(encoding="utf-8"))
```
