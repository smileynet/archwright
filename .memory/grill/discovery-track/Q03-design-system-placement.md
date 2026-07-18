# Q3: Design-system artifact placement and nature

**Status:** Decided 2026-07-18
**Decision:** Option C + C1 — layered artifact, permanent home at `design/discovery/ui/design-system.md`.

## Question

Is the design system a discovery doc, a set of patterns, or something layered — and where does it live?

## Research

- Design tokens = "design decisions as data, single source of truth for design and engineering" [martinfowler.com, Design Token-Based UI Architecture, 2024]; W3C Design Tokens spec first stable version Oct 2025 — load-bearing design-system content should be machine-readable.
- Drift is the canonical failure mode: manual propagation "rarely happens consistently" [Boldare 2026]; governance keeps design/code in sync [Miro 2026].
- Decisive G2 warning for agent pipelines: "AI breaks your design system by approximating it instead of reading it — fabricates token names, drifts within a session, forgets between sessions" [superdesign.dev 2026]. Prose-only design systems WILL be approximated by downstream agents; only checkable ones hold.

## Decision Detail (layered)

1. **The doc** (`design/discovery/ui/design-system.md`) is the discovery artifact and permanent human reference — `status: proposed → approved`, never moves (C1). Contains principles, rationale, and the catalog.
2. **Tension-resolving choices** (density vs readability, consistency vs affordance) graduate through `formalize` into `design/patterns/` with `serves:` links — normal seam graduation.
3. **Token/rule tables** are machine-readable data (YAML blocks or sidecar) that **constraint specs check against** — e.g., "all screens use spacing tokens from the table" becomes a checkable rule, defending against downstream-agent approximation.

## Rejected

- Prose-only single doc: uncheckable, guaranteed agent-approximation [superdesign 2026].
- Everything-as-patterns: token tables aren't tension resolutions; fails pattern quality gates; bloat.
- C2 (promote/move on approval): adds a move step + second placement rule for marginal visibility gain.

## Implications

- T4 design-system template gains: machine-readable token table format + a "graduates to patterns" section listing tension-resolving choices.
- Derive phase can emit constraint specs targeting the token data (new check instances flow through the Extension Protocol).
- Audit scan scope (D3) covers doc-vs-pattern consistency.
