---
name: archwright-report
description: "Generate and consume archwright design reports — interactive HTML diagrams, vocabulary overrides, response handling. Use when generating a project report, publishing report output, overriding vocabulary for domain events, or consuming report responses (asks). Trigger: generate report, run report, publish report, report vocabulary, report asks, design report."
metadata:
  type: workflow
  invocation: explicit
  practice: null
---

# archwright-report

Generate, publish, and consume archwright design reports for a target project.

## When to use

- Generating a report for a project that has design/ specs
- Publishing a report (commit + push to the target project)
- Setting up vocabulary overrides for domain-specific events
- Consuming report responses (asks that the report surfaces)
- Diagnosing report generation failures

## Prerequisites

Before generating a report, the target project needs:
1. `design/specs/` — at least one spec (behavior, contract, constraint, or dependency)
2. `design/models/` — optional but needed for the interactive diagram
3. A working `archwright-check` run (the report reads its JSON output)

## Generate a report

```bash
mise run report -- --project <path>
```

This:
1. Runs `archwright-check --all <specs-dir> --target <project> --json` to produce the canonical document
2. Feeds it to `generate.py` which derives model_view, asks, and stability blocks
3. Writes the bundle: `report.html` (interactive ELK diagram), `REPORT.md`, `report.json`

Output lands in `<project>/.scratch/report/` by default (or `--out <dir>`).

## Publish a report

```bash
mise run report-publish -- --project <path> [--name <display>]
```

Same generation step, then commits `design/report/` in the target project and pushes. The report goes in `design/report/` (gitignored in archwright itself, committed in the target).

## Postures

The report renders in one of four postures based on the check results:

| Posture | Condition | What it means |
|---------|-----------|---------------|
| `all-clear` | No blocking asks | The app behaves as designed |
| `needs-attention` | Decisions or approvals waiting | Human input needed |
| `tool-error` | Check run errored | Results incomplete — fix the tooling |
| `empty-project` | No specs found | Nothing to check yet |

## Vocabulary overrides

The report translates internal terms to surface phrases using a vocabulary map. The base map lives at `tools/report/vocabulary.yaml`. A target project can override or extend it.

### Setting up a project override

Create `design/vocabulary.yaml` in the target project:

```yaml
tokens:
  # Domain events — appear as arrow labels in the state diagram
  "event BALL_PASSED": "ball passed"
  "event TACKLE_ATTEMPTED": "tackle attempted"
  "event GOAL_SCORED": "goal scored"
  # Override existing terms if desired
  violation: "rule broken"
```

The override merges into the base map — project tokens win on conflict.

### Vocabulary completeness rules

- **Structural terms** (violation, skip, pending, etc.): missing = `GenerationError` (generation halts). These are non-negotiable — the base map covers them all.
- **Event terms** (`event <NAME>`): missing = humanized fallback + warning. The event name is lowercased and underscores become spaces. A warning prints which events fell back, with a hint to add them to the override.

### Fixing vocabulary warnings

When the report prints:
```
warning: 3 event(s) fell back to humanization (no vocabulary override):
  BALL_PASSED → "ball passed"
```

Add these to `design/vocabulary.yaml`:
```yaml
tokens:
  "event BALL_PASSED": "ball passed to teammate"
```

Re-run the report to verify the warning disappears.

## Asks (report responses)

The report surfaces three types of asks:

| Type | What it is | Blocking? |
|------|-----------|-----------|
| DECISIONS | Genuine ambiguity — options presented, you pick | Yes |
| APPROVALS | Clear right answer with recommendation — sign off | Yes (auto-approvable via config) |
| SUGGESTIONS | Optional nudges (trust promotions, etc.) | No |

### Auto-approve configuration

Set `ARCHWRIGHT_AUTO_APPROVE` environment variable:
- `off` (default) — all asks require human response
- `code-fixes` — auto-approve asks where the fix is clear code
- `all` — auto-approve everything (use for CI/unattended runs only)

## Field cases

| Scenario | Report behavior |
|----------|-----------------|
| First run, no model | `empty-project` posture — short report, diagram absent |
| Partial model, some specs | Diagram renders what's modeled; unmodeled areas absent |
| Full pipeline output | Complete diagram with all actors, transitions, violations pinned |
| Check errors | `tool-error` posture — reports what worked, flags what didn't |

## Does NOT

- Modify design artifacts (read-only over design/)
- Run checks itself (consumes the CK-03 document produced by archwright-check)
- Deploy or host the HTML (writes local files only)
- Make decisions (surfaces asks — human decides)
