# Archwright Conventions

Applies when working on archwright methodology, archwright skills, or running archwright pipeline phases against any target project.

## Pipeline Phase Discipline

The archwright pipeline (`survey → forces → tensions → resolve → formalize → model → contract → derive → check`) is a sequence of **discrete phases with human checkpoints between them**.

**Check is continuous, not terminal:**
- After contract/derive: run `python3 tools/archwright-validate.py <specs>... && python3 tools/archwright-validate.py --links design/` (spec schema, link resolution)
- After any code change: run `python3 tools/archwright-check.py --static design/specs/` (verify constraint specs against code) — or `--static design/specs/ --changed-only [--base <ref>]` to run only the specs the diff affects (CK-19; CI passes `--base origin/main`). In a target project with a `.archwright-baseline.json`, known debt reports as warnings with `baselined: true` and exit 0 — only NEW violations fail the run; `remaining_delta` is the number being driven to zero (CK-07)
- Evidence ledger (ADR 0009): in a target project with a `.archwright-evidence.json` (bootstrap: `echo '{}' > design/.archwright-evidence.json`), pass/fail check runs auto-append confidence evidence events (demotion/promotion candidates). When output reports `evidence_ledger.events_appended > 0`, surface the new candidates in the span digest — ratification is human, in the artifact, and ★★ moves always HITL-block
- After test suite runs: run `python3 tools/archwright-check.py --trace <spec.yaml> <trace.json>` (verify behavior specs against execution traces)
- Design audits: AI-assisted via `archwright-review` (no dedicated tool flag exists)

**Rules (ADR 0007 — gates block only where human input is needed):**
1. Each skill invocation = one phase. Produce its artifact, validate it, log it to the span digest.
2. **HITL-blocking gates** — always stop and wait for the human:
   - `resolve` (decisions; pre-resolved tensions = ONE batched confirmation, still presented)
   - Inferred product-desire validation (L4/L5) inside `forces`
   - Any ★★ event that survives the research gate (ADR 0010): before escalating a ★★ violation, research it (prior art, related decision records, contrast pair) — check defects/spec noise get proposed fixes, known-and-accepted items get logged with the reference, and only genuine new decisions (tradeoffs, novel security judgment) block, arriving WITH research + recommended disposition. Hard floor always blocks: irreversible, security-material-and-novel, or contradicting a ratified resolution. ★★ assignment beyond what resolve ratified and demotion proposals still block unconditionally
   - Fog: unknown forces / unresolved tension encountered mid-span
   - End of span: present the full digest for acceptance
3. **Flow-through gates** — auto-advance WITHOUT stopping, but only when ALL hold:
   - The human pre-authorized a span (e.g., "run forces through derive"); never advance past the span boundary
   - The phase's artifacts pass `archwright-validate.py` (schema + links); validation failure = stop
   - The digest entry is written
   - No span authorized → fall back to stop-after-each-phase
4. The survey skill explicitly does NOT write patterns, specs, or resolve tensions. It produces an intake outline and dispatch queue.
5. A skill's "Does NOT" section is a hard boundary, not a suggestion.
6. "Proceed" after orientation authorizes the NEXT phase (or the span the agent proposed and the human accepted) — never "run everything silently to completion" without a digest gate at the end.

**Why:** Human checkpoints are for decisions, not ceremony. Mechanical phases are protected by validation gates + the end-of-span digest (batched review), while decision points, ★★ events, and fog still hard-block. Evidence: `.memory/audit/pipeline-dryrun.md` findings 2 and 4; full rationale in `.memory/adr/0007-hitl-only-gates.md`.

## Autonomy Within Phases and Spans

Once inside a single phase, execute sub-steps without pausing unless:
- A sub-step failed and needs user input
- A decision point not covered by the skill arises
- The action is high-risk per safety guardrails

Do not ask "shall I proceed?" between sub-steps of one phase. At phase end: if inside a pre-authorized span and the flow-through conditions hold (ADR 0007), advance; otherwise stop and present.

**"Proceed" disambiguation:** When the user says "proceed" after an orientation report or phase summary, it authorizes the NEXT SINGLE PHASE — unless the agent proposed a span (e.g., "I'll run forces through derive, then present the digest") and the human accepted it, in which case "proceed" authorizes that span. It never means "run all remaining phases" without an end-of-span digest gate.

## Target Project Artifacts

When archwright operates on a target project, it produces:
```
target-project/
  design/
    forces/            # Markdown+frontmatter, one file per force (kind: force) — root of provenance
    patterns/          # Markdown+frontmatter (tensions, resolutions; serves: links to forces)
    models/            # YAML (machine-readable) + MD (human-readable with Mermaid diagrams)
    specs/             # Behavior/contract: YAML. Constraint/dependency: Markdown+frontmatter.
```

These directories are the archwright output. The `.memory/` directory in the target project contains the project's own internal knowledge (grills, ADRs, specs-as-requirements) — archwright reads from `.memory/` and writes to `design/`.

## Run Scoping and Artifact Placement

Operator policy (grill Q06, 2026-07-17), applies to ALL pipeline runs:

1. **Scope by size.** Default: full project / all areas in one run. **Large projects and monorepos** (workspace layouts, multiple apps/packages, or a source corpus far beyond survey sizing guidance) are the exception: break into AREAS, run the full pipeline per area, then an **all-up reconciliation pass** — dedupe forces across areas, surface cross-area tensions, unify models. Area partitioning is for scale, never the norm.

   **Reconciliation deliverables** (first field run: DynamoRush area 4, 2026-07-18 — promote to a skill if a second run needs it):
   - **Dedupe verdicts.** Compare force statements across areas; prefer FAMILIES over merges — forces with the same principle but different who/object/check-target stay separate with the family documented (merging blurs provenance and check targets). Areas that reused earlier ids via `shared_product_forces` create no dupes by construction.
   - **Cross-model seam table.** One row per producer/consumer seam crossing area models: contract involved, verdict (fold / extension / compatible / content-not-code-reuse), and any pattern edits made (scope notes, `completed_by` links).
   - **Experience ownership.** An experience id defined in 2+ models gets ONE owning model; others annotate theirs as a restatement.
   - **`design/models/system-overview.md`** — system composition diagram, the seam table, force families, and any cross-area spine invariant.
   - Verification: `--links` must pass after edits; full static batch re-run with any pre-existing deliberate FAILs called out as unchanged.
2. **Artifacts are live documents in the primary repo/branch space.** Commit `design/` output branch-agnostically to the CURRENT project branch unless the user specifies otherwise. No special design branches by default.

## Discovery Track (ADR 0011)

The pipeline has two tracks of work — one methodology, one agent, one artifact space. The **discovery track** (grill sessions, UI wireframing via `archwright-discover-ui`, WoZ imports, spikes) is HITL-dense and divergent; the **verification track** (survey→check) is the flow-through pipeline above. They meet at ONE seam: `resolve`, where approved discovery decisions enter as pre-resolved tensions through the batched-confirmation path.

**Seam contract:** discovery hands over resolved decisions + evidence + an explicit unresolved list — never bare artifacts. The format is the **decision ledger** (`tools/templates/discovery-ledger.md`): append-only `D{NNN}` entries with category (core 5 + domain overlay extensions), origin (`user | suggested | inferred`), verbatim rationale, alternatives; reversals via `SUPERSEDES`; entries are truth — projections regenerate from them, never the reverse.

**Placement + graduation:** discovery artifacts live in the target project at `design/discovery/<area>/` with `status: proposed | approved | superseded`. Graduation is mandatory on approval: decisions thread into force evidence and model seeds citing their `<artifact-id>#D{NNN}` anchors, and `--links` must pass. Unconfirmed `inferred` entries block graduation. **Conservation principle** on every seam transform: nothing invented (every output element cites an anchor), nothing lost (every active decision consumed or explicitly deferred).

**Gates:** discovery inherits consequence-based gating — the ★★ hard floor applies to discovery-surfaced decisions. The rubber-stamp guard is calibrated by session type: creative sessions get the strict 3+-consecutive-`suggested` tripwire; grill-type sessions get periodic decision-surfacing (agreement with researched recommendations is never penalized). Discovery queues are prioritized by **risk/uncertainty**, never value/effort.

## Extension Protocol

How archwright extends itself when it encounters a situation its material doesn't cover — a stack without an adapter, a domain without an overlay, a check kind without a method (ADR 0008, grill Q05). A coverage gap is a counterexample against archwright's own abstractions, handled by archwright's own loop: detect → research → generate from existing pattern → verify → register.

Six rules:

1. **Gaps are pending-with-reason, never silent.** The gap artifact names the missing adapter (stack, kind, what it unblocks) — a `pending` registry row, a `target_status: pending` on a spec, or a SKIP-with-reason in check output. Checks that can't run because an adapter is missing SKIP with the declared reason; they never fail and never silently pass.
2. **Two-tier governance.** New INSTANCES of existing kinds (a new stack adapter, a new domain overlay, a new predicate) flow through this protocol. New KINDS, new axes, or format/schema changes bypass it and require an ADR + HITL.
3. **Research before generating.** 2+ independent sources or a spike before writing the new instance. Spike output IS the conformance scenario.
4. **Conformance at birth.** Every new instance ships with a golden corpus (scenario source + expected output) wired into `tools/run-fixture-tests.sh`. No corpus → the instance stays `pending`. **The corpus MUST include at least one violating scenario that produces FAIL** — a checker proven only on passing cases may be vacuous (the Alloy compiler generated transition-less models for months; every check passed until a deliberately-violating spec exposed it, 2026-07-17).
5. **Tiered status by guarantee**, reusing the confidence vocabulary: `pending` (registered, unproven) → ★ (conformance corpus passes) → ★★ (corpus in the fixture suite + measured cost recorded). Status is COMPUTED by the suite, not hand-declared. Demotion is stepwise (★★→★→pending, never cliff-edge) and `since:` history is retained in the registry row.
6. **Activation-gated enforcement + rule-of-two.** An adapter's checks run only where its stack/domain is detected (survey records detection; downstream phases consult it). Build no axis scaffolding (schemas, harnesses, plugin machinery) until ≥2 concrete entries need it.

Registries: `tools/stacks/REGISTRY.yaml` (per-language/engine adapters: trace emitters, ast-grep grammars, check-pattern libraries) and `tools/domains/detect.yaml` (per-domain vocabulary overlays). Stacks and domains are orthogonal axes — a TypeScript game backend is `web` domain + `typescript` stack.


## Pattern Quality Gates

Before committing a pattern:
- Forces section: polarity is clear, each force is one sentence, no solutions disguised as forces
- Evidence substance (recalibrated per ticket 014 — share-of-body measured volume, not quality; 13/13 field patterns failed it while rating "excellent"):
  - **Every Therefore commitment traces to Evidence** — each architectural commitment in the Therefore section is justified by at least one Evidence item (prior art, rejected alternative, or mechanism argument). A commitment with no supporting Evidence item = gate FAILURE (this is how an evidence-free pattern fails).
  - **Citations are locatable** — name the specific source (project, paper, game, engine doc), never "it's standard practice" or "commonly known"
  - **Freshness is visible** — external claims carry a year/version; claims about fast-moving tech (engine features, API behavior) are verified against the current version or explicitly flagged as unverified
- Therefore section: specific enough that two developers would implement the same architecture
- Verification section: names a mechanical check (★★), a heuristic check (★), or — for advisory patterns — states explicitly why no check exists (— is a legitimate confidence, not a missing field; vocabulary map in the deployed `archwright-survey/references/glossary.md`)

## Spec Quality Gates

Before committing a spec:
- `from_patterns` traces to at least one formalized pattern
- Constraint specs: `check` section has a runnable method (grep/semgrep/script) with correct target path
- Behavior specs: states, transitions, and invariants map to observable system behavior
- All specs pass `archwright-check --static` before commit
