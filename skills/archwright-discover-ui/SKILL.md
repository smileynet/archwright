---
name: archwright-discover-ui
description: "Run a UI discovery session: research-backed design system proposal + ASCII wireframes, reviewed one-by-one with decisions captured in a provenance ledger, graduating into archwright forces/patterns/model seeds. Use when designing screens or UI for a project, proposing a design system, wireframing, or reviewing UI direction. Trigger: ui session, wireframes, design the ui, mock up screens, design system, what should this screen look like."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Discover UI

Discovery-track skill (ADR 0011): turn UI intent into approved, evidence-carrying decisions that feed the verification pipeline at the `resolve` seam. The wireframes are evidence; the **decisions are the deliverable**.

**Stance is mandatory:** read `references/facilitation-stance.md` before the session. This is a **creative session** — the strict rubber-stamp guard applies (3+ consecutive `suggested` decisions → stop and ask what the USER thinks). No internal vocabulary to the user — never say "forces", "ledger", "artifact gap", "graduation" in conversation; just talk about their screens.

## Artifacts

All in the target project under `design/discovery/ui/`:

| Artifact | Template | Notes |
|----------|----------|-------|
| `design-system.md` | `tools/templates/design-system.md` (archwright repo) | Permanent home — never moves (grill Q3). Token tables machine-readable |
| `wf-<screen>.md` (one per screen) | `tools/templates/wireframe.md` | Ledger + artifact gap + hands-to sections required |
| `INDEX.md` | — | Session log + regenerable decision-table projection (entries are truth) |

Ledger rules (append-only, origin, verbatim rationale, `SUPERSEDES`): `tools/templates/discovery-ledger.md`. Category enum: core 5 + the domain overlay's `discovery: category_extensions`.

## Process

### 1. Orient

- Domain: from the survey intake outline if one exists; else apply `../archwright-survey/references/domains/detect.yaml` (explicit override wins).
- Load the domain's `discovery.yaml` overlay (deployed at `../archwright-survey/references/domains/<domain>/`) — its frameworks supply the opening questions; its `category_extensions` extend the ledger enum.
- **Anchor the job first:** walk the overlay's FIRST coverage gate (the job — who uses this, to get what done) in ONE exchange before proposing anything. Artifact-fast (stance §4) bounds the upfront interview at 2–3 questions, never zero — a design system proposed before the job is anchored gets reworked (field-hit 2026-07-19: report-ui session's overview rebuilt after the user had to inject JTBD themselves).
- Read existing `design/forces/` and `design/discovery/ui/` if present — never re-derive decided things; a changed mind is a `SUPERSEDES` entry, not a re-litigation.

### 2. Research (agent-side, before proposing)

Dispatch subagents per the research-dispatch mandate — one per topic (e.g., "UI conventions for <domain/genre>", "design systems in comparable products", "accessibility baseline for <platform>"). Consult the domain overlay's framework sources first. Every design-system element you later propose needs a locatable citation with a year (pattern quality gates — no "standard practice").

Research is invisible to the user; do not interview them about what research should find.

### 3. Propose the design system — compactly, with a sketch

Draft `design-system.md` from the template: principles (cited, force-linked), machine-readable tokens, component guidance. Present it in plain language **alongside a first example wireframe** — the stance's artifact-fast rule applies to this phase too: don't lecture abstract principles; show what they produce. Record system-level choices as ledger entries in the design-system file as the user reacts.

### 4. Wireframe the screens

- Screen list from the overlay's coverage gates (e.g., web red routes; game first-contact moment) plus what the user names. Propose an order; the user can jump (propose-don't-force).
- One file per screen from the template. **Show the ASCII sketch within 2–3 exchanges**, then ask max 1–2 questions per screen, always after showing. Early sketches end with the direction check.
- Every choice that survives an exchange becomes a ledger entry with honest origin. Watch the tripwire guard.

### 5. Review loop — one by one

For each wireframe: present sketch + which design-system elements it uses + why this layout (plain language). Discuss. On the user's approval:

- Flip `status: proposed → approved`
- Record the approval and any amendments as ledger entries
- Fill the **Not Resolved Here** section honestly — states, edge cases, interaction rules this sketch deliberately omits. An empty gap list is a claim you must be able to defend, not a default
- Fill **Hands To** with flow edges/state/events, each citing its `D{NNN}` anchor

Periodically (every ~5 decisions) surface progress in plain terms: "locked in so far: X, Y, Z — sound right?"

### 6. Graduate (the seam)

When the session's wireframes are approved:

1. **Force evidence:** for each force a decision serves, append the evidence to the force file (rationale text verbatim, cited as `wf-<screen>#D{NNN}`). New desires surfaced by the session → flag for the forces phase, don't silently create.
2. **Model seed:** compile the Hands-To sections into `design/discovery/ui/model-seed.md` — screen-flow graph + per-screen state/events, every element citing its ledger anchors (conservation: nothing invented). Active decisions not consumed by the seed get an explicit "Unconsumed decisions" list with reasons (nothing lost).
3. **Model TODOs:** compile all Not-Resolved-Here lists into the seed's TODO section — this is the model phase's input.
4. **Design-system graduation:** rows in its Graduates-to-Patterns table go to `archwright-formalize` (separate phase — this skill only fills the table).
5. **Validate:** per-file schema + conservation, then links: `python3 tools/archwright-validate.py design/discovery/ui/*.md && python3 tools/archwright-validate.py --links design/` — both must pass. Per-file checks the discovery schema (status enum, ledger entry structure) and that every Hands-To / Graduates-to-Patterns element cites a ledger anchor (nothing invented); `--links` checks citations resolve and every active entry is consumed or explicitly deferred (nothing lost). Conservation gates on approval: `proposed` artifacts get warnings, `approved` get errors — so run it at graduation, fix before closing the session.

Unconfirmed `inferred` entries block graduation — surface them for confirmation first.

## Does NOT

- Write behavior/contract/constraint/dependency specs (derive/contract phases own those)
- Create or modify `design/models/` (the model phase consumes the seed; this skill only seeds)
- Skip the per-wireframe approval — no batch-approving screens the user hasn't seen individually
- Surface internal vocabulary or machinery to the user
- Make creative decisions for the user — when they're stuck, narrow the question, never fill the blank

## Fidelity Ceiling

ASCII wireframes answer structure (layout, hierarchy, flow). When the open questions become spacing precision, color feel, or affordance subtleties — say so and stop: that's higher-fidelity territory (design tools, prototypes), out of this skill's scope. Record such questions in Not Resolved Here.
