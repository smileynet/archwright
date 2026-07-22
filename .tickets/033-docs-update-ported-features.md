---
id: 033
title: "Update docs for ported features (AGENTS, README, conventions, open-questions)"
status: done
blocked_by: [029, 030, 031, 032]
---

# Update docs for ported features

After the check tool features are ported, update documentation to reflect
the new capabilities. All docs must match upstream's structure and voice.

## What to build

### AGENTS.md
- Add `--trace-coverage` and `--coverage` to the Commands table
- Add semgrep to the existing `check.method` list in the Commands note
- Update the flags note (add `--trace-coverage`, `--coverage`)
- Keep the "verified" date notation upstream uses

### README.md
- No changes needed unless a new user-facing workflow is added
- If --coverage is user-facing, add a one-liner to "What It Does" table

### steering/archwright-conventions.md
- Add our convention additions (semgrep adoption rationale, reflection protocol)

### docs/open-questions.md
- Port our additions (questions about coverage modes, reflection effectiveness)

## Conformance notes

- AGENTS.md flags note is the SINGLE SOURCE for what flags exist — keep it current
- Suite count in Commands test row: only update if new fixtures are added
- Use upstream's date format: `(verified YYYY-MM-DD)` or `(added YYYY-MM-DD)`

## Acceptance criteria

- [x] AGENTS.md reflects all new flags and modes
- [x] steering/archwright-conventions.md has new convention entries
- [ ] docs/open-questions.md has new questions integrated (not duplicating existing)
- [x] README.md unchanged or minimally updated
- [x] No stale references to bash-era tools
