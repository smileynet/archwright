---
id: "054"
title: "Report: response bar accumulation + response file export"
status: done
blocked_by: ["053"]
priority: high
---

# Report: response bar + response file export

## Problem

The designed report (wf-overview bottom bar) accumulates user responses in-page and exports them as a structured response file the agent consumes on next run. This is the human→agent feedback loop — the entire point of the report being interactive rather than read-only.

Current state: `page.js` has a reducer skeleton and a `saveResponses()` stub, but no actual response accumulation from card interactions, and no file export.

## What to build

1. **Response accumulation**: when user interacts with a decision/approval card (selects an option, clicks approve), the choice is stored in the page reducer state
2. **Response bar**: appears at page bottom once any response is recorded. Shows count ("3 responses recorded") + "Save responses for the agent" button
3. **Response file export**: button triggers download of a JSON file matching `contract:response-file` schema (ask-id reuses aw/v1 fingerprints → choice/approval/freeform + run identity)
4. **Agent consumption**: the archwright-check tool (or a dedicated report skill) reads the response file on next run, applies decisions (update baseline, amend spec, etc.)

## Schema (from contract:response-file)

```yaml
version: 1
run_id: "commit:sha + timestamp"
responses:
  - ask_id: "aw/v1:fingerprint"
    type: "decision | approval | suggestion"
    choice: "selected option text or action"
    freeform: "optional user note"
    timestamp: "ISO8601"
```

## Acceptance criteria

- [x] Clicking a decision option or approval button stores a response in page state
- [x] Response bar appears after first interaction, shows accurate count
- [x] "Save" button downloads a JSON file matching the response-file contract
- [x] Response file includes run_id (commit + check timestamp from the report data)
- [x] Agent can consume the response file on next check run (documented in skill contract)
- [x] Responses survive page scroll (not lost on DOM recycle)
- [x] Multiple responses for the same ask-id: last wins (supersede, not accumulate)
