# Q2: Ledger category enum

**Status:** Decided 2026-07-18
**Decision:** Option A — fixed core of 5 + domain extensions via overlay `discovery:` section.

## Question

Is the decision-ledger `category` enum a single canonical set, a fixed core with per-domain extensions, or fully per-domain?

## Research

- Category's real consumers (from wizard_of_oz corpus): coverage/gap detection and document section mapping. Graduation routing in archwright uses `serves:` links, not categories — so categories exist chiefly for coverage detection, which is domain-shaped by nature.
- Scales precedent ("enum canonical, labels vary") examined and rejected as non-transferable: scales are 4 universal abstraction levels; decision categories are domain vocabulary (`economy`, `progression` have no honest web equivalent).
- Taxonomy warning (G2): the classifier is an LLM — misclassification noise grows with category count and boundary ambiguity; catch-alls get abused. Small core wins.

## Decision Detail

**Core 5 (canonical, all domains):**
- `scope` — what's in/out (MLP filter generalizes)
- `experience` — what the user feels (generalizes wizard_of_oz's `aesthetic`)
- `structure` — layout, hierarchy, flow (the wireframe categories)
- `technical` — platform constraints
- `meta` — process, naming

**Domain extensions** live in the overlay's `discovery:` section. Game overlay extends with: `mechanic, feedback, progression, economy, content, narrative` (ported from wizard_of_oz, minus core dupes).

## Implications

- Validator rule: `category ∈ core ∪ detected-domain extensions`.
- Coverage reports can aggregate cross-domain on the core 5; domain-specific gap detection uses the extended set.
- T2 (ledger template) parameterizes the enum; T3 (overlay `discovery:` sections) carries the extensions.
- wizard_of_oz's own enum is unchanged (it's standalone, per Q1) — the export mapping (T7) translates its categories into core+game-extension terms.
