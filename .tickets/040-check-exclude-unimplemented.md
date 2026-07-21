---
id: "040"
title: "Constraint check `exclude` field is documented but unimplemented"
status: done
blocked_by: []
---

# Constraint check `exclude` field is documented but unimplemented

Field report from the crew-research tkt build (2026-07-21).

## Why

`steering/archwright-conventions.md` § Check Method Conventions documents `exclude`
("string or list of path substrings. Matches in files containing any exclude substring
are removed before interpretation") — but `archwright-check.py` never reads the field:
`grep -n exclude` finds no check-path implementation. A spec relying on
`exclude: ["test_"]` silently gets NO filtering; matches in test files fail the check.

Observed: crew-research `stage-only-ticket-file` spec excluded `test_` fixtures; the
check failed on `tools/tkt/tests/test_tkt.py` anyway. Worked around by narrowing
`target:` to the source package dir (the better spec anyway, per reflection R2), but the
silent no-op is the defect: a documented field that does nothing is worse than a
rejected one.

## What to build

Either implement `exclude` in `_python_grep`/`_check_grep` (filter matched paths by
substring before interpretation) or reject specs that use it (validation error) until
implemented. Conformance corpus must include: a spec whose exclude removes a real match
(passes) and the same spec without exclude (fails) — vacuity rule.

## Acceptance criteria

- [ ] `exclude` filters grep/semgrep matches, or validate rejects the field loudly
- [ ] Conformance fixture with passing AND violating variants
- [ ] Conventions doc and reality agree
