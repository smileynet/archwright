---
name: repo-maintenance
description: "Usage and output-interpretation contract for archwright's repo-internal scripts: run-fixture-tests.sh (fixture suite) and deploy-skills.sh (skill/steering deployment). Use when running the test suite, interpreting suite results, deploying skills to agent tools, or diagnosing deploy/suite anomalies in THIS repo. Trigger: run the suite, fixture tests, deploy skills, suite green, skipped checks, stale skills, coverage audit, propose updates to skills/AGENTS/tools."
metadata:
  type: process
  invocation: both
  practice: null
---

# Repo Maintenance (archwright-internal)

Project-local skill — never deployed globally. Owns the two repo-internal scripts that deliberately have no global skill (decision 2026-07-18): `tools/run-fixture-tests.sh` and `tools/deploy-skills.sh`.

## run-fixture-tests.sh (fixture suite)

**Invoke:** `mise run test` (preferred — managed toolchain) or `bash tools/run-fixture-tests.sh`.

**Output contract:** final line `=== Results: N passed, N failed, N skipped ===`.

| Reading | Meaning | Action |
|---|---|---|
| `0 failed, 0 skipped` | Suite green — the ONLY healthy state on a fully-hydrated machine | Proceed. Say "suite green" — the count lives ONLY in the AGENTS.md Commands row; never restate it elsewhere |
| `skipped > 0` | Coverage gap, NOT a pass — a dependency is missing (alloy6.jar, java, node, or git); each SKIP prints its reason | Rehydrate (`mise run rehydrate-alloy`, `mise install`), re-run. Never report green with skips without naming them |
| `failed > 0` | A conformance or feature check broke | Read the ✗ lines (each names its scenario). Fix root cause; deliberate-FAIL fixtures are part of the corpus — a violating scenario that PASSES is itself a failure (vacuity guard) |

**When to run:** after ANY merge from upstream (hard rule), after editing any `tools/` script, after adding fixtures, after rehydrating dependencies. Adapter status in `tools/stacks/REGISTRY.yaml` is COMPUTED by this suite — never hand-edit status.

**Windows:** the script has a python3→python guard; run via `mise run test` to avoid the MS Store python stub.

## deploy-skills.sh (skill/steering deployment)

**Invoke:** `mise run deploy-skills` (kiro global, default) or `bash tools/deploy-skills.sh --tool kiro|claude|codex|agy [--project <path>]`.

**What it syncs:** `skills/` + `steering/` + domain overlays (`tools/domains/` → survey references) + glossary, into the target tool's discovery dirs (kiro: `~/.kiro/{skills,steering}`; claude: `~/.claude/{skills,rules}`; codex/agy: `.agents/skills/` — no steering equivalent, the script prints wiring guidance).

**Output contract:** one `✓` line per deployed item (`✓ skill (symlink): <name>` for kiro-global; `✓ skill: <name>` for copy mode; plus `✓ domains: …`, `✓ stacks: …`, `✓ glossary: …` for the generated references, which are always materialized copies). Tools with no native steering home (codex/agy) SKIP steering with printed guidance.

| Reading | Meaning |
|---|---|
| `✓ skill (symlink): <name>` | kiro global is symlinked into this repo — edits are live immediately, NO redeploy needed |
| `✓ skill: <name>` (copy mode: claude/codex/agy/project scope) | Copies go stale silently; redeploy after every skill edit intended for those targets |
| `✓ domains / stacks / glossary` | Generated references — materialized copies even under symlink mode; re-run deploy after editing `tools/domains/`, `tools/stacks/REGISTRY.yaml`, or `docs/glossary.md` |

**When to run:** after ADDING a new skill (symlinks exist per-skill — a new dir isn't linked yet), and after any edit when targeting claude/codex/agy. NOT needed for edits to already-symlinked kiro skills.

## Coverage Audit (run when asked to "propose updates to skills/AGENTS/tools", or after shipping new tools/skills)

Three checks; each caught real drift when first run (2026-07-18: missing script coverage; stale workflow line an hour later):

1. **Tool→skill map completeness.** `ls tools/*.py tools/*.sh tools/*.mjs` vs the AGENTS.md ownership map. Every script needs an owning skill (usage + output-interpretation contract), a project-local owner (this skill), or an explicit "none" rationale (shared module). New templates/artifact contracts count — agents must know where their interpretation rules live.
2. **AGENTS.md staleness against actual behavior.** Verify claims about deploy behavior, file locations, and workflows against the scripts themselves (grep the script, don't trust the doc). Known trap: symlink-vs-copy deploy semantics — kiro edits are live, generated references and other tools are not.
3. **Project-local skill inventory.** `ls .kiro/skills/` — does anything repo-internal lack guidance? Conversely, is anything project-local that should be global (or vice versa)?

Report the delta only; apply small doc fixes immediately (low-risk), ticket anything structural.

## Does NOT

- Cover pipeline tools (`archwright-check.py`, `archwright-validate.py`, etc.) — those contracts live in their owning global skills (map in AGENTS.md)
- Apply outside the archwright repo
