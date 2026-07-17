# Research: Per-Language/Per-Stack Adapter Architectures with Capability Registries

Date: 2026-07-17
Question: How do mature systems structure per-language/per-stack adapters with capability registries?

## Summary

Three mature ecosystems solve the "many adapters, one core" problem with three distinct mechanisms: **OpenTelemetry** uses a *static, curated status matrix* (per-language × per-signal maturity levels defined in a spec OTEP) plus a searchable community registry for the long tail; **LSP** uses *runtime capability negotiation* (client and server exchange capability objects at initialize; features degrade gracefully when a capability is absent); **tree-sitter** uses *decentralized package conventions* (each grammar is an independent repo following naming/versioning/publishing conventions, with third-party aggregator registries emerging to catalogue them). The common thread: none require every adapter to support everything — each system has an explicit vocabulary for "this adapter exists but only supports X at maturity Y," and missing adapters fall back to either community/unofficial implementations (OTel), feature omission (LSP), or absence from the catalogue (tree-sitter).

## Details

### 1. OpenTelemetry — curated status matrix + open registry

**How adapters are registered.** Two tiers:
- **Official SDKs** (per language: C++, .NET, Erlang/Elixir, Go, Java, JS, Kotlin, PHP, Python, Ruby, Rust, Swift) are owned by per-language Special Interest Groups (SIGs) and listed in a hand-maintained "Statuses and Releases" table on the docs site. Each language implements a shared language-agnostic specification, so the *contract* is centralized and the *implementations* are federated.
- **The OpenTelemetry Registry** (opentelemetry.io/ecosystem/registry) is a searchable catalogue of instrumentation libraries, collector components, exporters, and utilities. Maintainers self-submit entries; each language's docs has a pre-filtered `registry/` page. This is where the long tail (third-party instrumentations, unofficial language implementations) lives.

**How status/maturity is tracked.** Very explicit and fine-grained:
- Maturity levels are defined in a spec document (**OTEP 0232 "maturity of otel"**): `Stable`, `Beta`, `Alpha/Development`, etc. Every cell in the status table links directly to the level's definition.
- Status is tracked **per language × per signal** (Traces / Metrics / Logs / Profiles), not per language as a whole. E.g., Go is Stable for traces/metrics but Beta for logs; Rust is Beta across the board; Kotlin is Development everywhere. This acknowledges that adapters mature unevenly across capabilities.
- The status page explicitly warns that component status ≠ spec status: "the status of a signal in the specification may not be the same as the signal status in a particular language SDK." Status is scoped to the component you're looking at.
- A second cross-cutting caveat: even a Stable SDK can break you if the *semantic conventions* it relies on are Experimental — stability composes from multiple layers.

**How missing adapters are handled.** An explicit "Other languages" page states the spec is designed to be implementable in any language; unofficial implementations are discoverable via the registry. So the fallback path is: official SDK → community implementation in registry → implement-the-spec-yourself. The spec being language-neutral is what makes the third option viable.

**Takeaway for archwright:** per-adapter × per-capability maturity matrix, with maturity levels defined once in a governing doc and every status cell linking to its definition. Federated ownership (SIG per language) under a centralized contract.

### 2. LSP — runtime capability negotiation

**How adapters are registered.** There is no central registry in the protocol itself — an "adapter" (language server) is registered by the client (editor) at runtime. The editor starts one server per language and performs an `initialize` handshake over JSON-RPC.

**How capabilities are tracked.** The core design insight: *"Not every language server can support all features defined by the protocol. LSP therefore provides 'capabilities.'"*
- A **capability groups a set of language features** (e.g., `textDocument/definition` support, `workspace/symbol` support).
- Both sides announce: the **server** declares which requests it can handle (ServerCapabilities returned from `initialize`); the **client** declares what it can do (ClientCapabilities sent in `initialize`), e.g., willingness to send "about to save" notifications so the server can format before save.
- Capabilities can also be **dynamically registered/unregistered** after startup (`client/registerCapability`), letting servers add features once they've loaded project config.
- The protocol keeps data types simple and language-neutral (URIs, positions) rather than standardizing ASTs — this is what makes one protocol serve N languages × M editors and reduces the integration problem from N×M to N+M.

**How missing adapters/capabilities are handled.** Graceful degradation is built in: if a server doesn't announce a capability, the client simply doesn't offer that feature (no "go to definition" menu item, etc.). No error, no negotiation failure — the feature set is the intersection of what both sides declared. Integration specifics are deliberately left to tool implementors.

**Takeaway for archwright:** when adapters are live components, prefer a declared-capability handshake over an out-of-band registry; design the core protocol so features are individually optional and absence degrades to "feature unavailable," not failure. (MCP explicitly copied this design.)

### 3. tree-sitter — decentralized repos + conventions + aggregator registries

**How adapters are registered.** Maximally decentralized. Each grammar is an independent repo (conventionally named `tree-sitter-<language>`), generated from a `grammar.js` into a C parser with a uniform ABI. There's no single official registry; instead:
- **Publishing conventions** (official docs): publish to GitHub *and* to each language ecosystem's package registry — crates.io (Rust), npm (JS), PyPI (Python) — so consumers in any host language can depend on the grammar. The tree-sitter org provides **reusable CI workflows** that regenerate and publish bindings to all registries on tag push.
- **Versioning conventions**: grammars must follow SemVer so that downstream integrations (queries, tree-traversal code, node-type checks) survive upgrades predictably. `tree-sitter version X.Y.Z` bumps version metadata across all binding manifests at once.
- **Aggregators fill the registry gap**: e.g., `neovim-treesitter/treesitter-parser-registry` — "an editor-agnostic catalogue of tree-sitter parsers and their associated Neovim query repositories" — and bundle projects like `tree-sitter-language-pack` (300+ grammars behind one API, parsers downloaded on demand and cached).

**How status/maturity is tracked.** Weakly, compared to OTel. There's no central maturity taxonomy; quality signals are per-repo (test corpus pass rates, "actively maintained" claims in READMEs, whether official CI workflows are used) plus curation decisions by aggregators (nvim-treesitter historically marked parsers as maintained/experimental). SemVer is the main formal maturity signal.

**How missing adapters are handled.** If no grammar exists for a language, there's simply nothing to load — consumers detect absence at dependency-resolution time. The mitigation is that the barrier to creating an adapter is deliberately low (grammar DSL + generator + CI templates), so the community fills gaps; bundles like language-pack make discovery/installation uniform.

**Takeaway for archwright:** if adapters are static artifacts (per-language grammars/predicates rather than live services), the leverage points are (a) strong naming + repo-layout + versioning conventions, (b) scaffolding/CI templates that make a conforming adapter cheap to produce, and (c) a thin catalogue layer (even a single YAML manifest) rather than heavyweight central governance. Note tree-sitter's weak maturity tracking is a known pain point — aggregators had to reinvent it.

### Cross-cutting patterns

| Concern | OpenTelemetry | LSP | tree-sitter |
|---|---|---|---|
| Registration | Curated table (official) + self-serve registry (community) | Runtime handshake per session | Independent repos + package registries + third-party catalogues |
| Capability granularity | Per language × per signal | Per feature (capability flags), dynamically updatable | Per grammar (whole-language); node types define the "contract" |
| Maturity vocabulary | Formal levels (Stable/Beta/Development) defined in one OTEP, linked from every status cell | None — binary supported/unsupported per capability | SemVer only; aggregators add curation |
| Missing adapter | Fall back to registry/community impl, or implement the spec | Feature silently unavailable (graceful degradation) | Absent from catalogue; low barrier to author new one |
| Central contract | Language-agnostic specification | Protocol spec (JSON-RPC + simple neutral types) | Parser ABI + grammar DSL + node-type schema |

Design implications for an archwright domain-overlay / per-stack adapter system:
1. Track maturity **per adapter × per capability** (like OTel's language × signal matrix), with levels defined once and referenced everywhere.
2. Make capabilities individually optional with graceful degradation semantics (LSP): a check that a domain overlay can't run should SKIP with a declared reason, not fail.
3. Keep the adapter contract small and neutral (LSP's "URIs and positions, not ASTs") so adapters stay cheap to write.
4. Provide templates/scaffolding + a manifest (`detect.yaml` already plays the catalogue role) rather than heavyweight registration (tree-sitter).
5. Distinguish "official/curated" from "community/experimental" tiers explicitly (OTel's two-tier model).

## Sources

- [L4:verified] OpenTelemetry — Language APIs & SDKs (status matrix, per-language × per-signal): https://opentelemetry.io/docs/languages/
- [L4:established] OpenTelemetry — component status scoping ("look for the status from the right component page"): https://opentelemetry.io/status/
- [L4:established] OpenTelemetry Registry (self-serve catalogue for instrumentation libraries/components): https://opentelemetry.io/ecosystem/registry/ (per-language view e.g. https://opentelemetry.io/docs/languages/python/registry/)
- [L2:established] OTEP 0232 — maturity level definitions: https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0232-maturity-of-otel.md
- [L4:established] OpenTelemetry — Other languages (unofficial implementations path): https://opentelemetry.io/docs/languages/other/
- [L4:verified] LSP Overview (capabilities section read directly): https://github.com/microsoft/language-server-protocol/blob/gh-pages/_overviews/lsp/overview.md
- [L4:established] Microsoft — Language Server Protocol overview: https://docs.microsoft.com/en-us/visualstudio/extensibility/language-server-protocol
- [L4:verified] tree-sitter — Publishing Parsers (registries, reusable workflows, SemVer guidance): https://tree-sitter.github.io/tree-sitter/creating-parsers/6-publishing.html
- [L6:reported] neovim-treesitter parser registry (editor-agnostic catalogue): https://github.com/neovim-treesitter/treesitter-parser-registry
- [L6:reported] tree-sitter-language-pack (305 grammars, one API, on-demand parser download): https://github.com/kreuzberg-dev/tree-sitter-language-pack
- [L5:reported] MCP capability negotiation (LSP-inspired, corroborates the negotiation pattern): https://apxml.com/courses/getting-started-model-context-protocol/chapter-1-architecture-and-fundamentals/capabilities-negotiation

## Open Questions

1. **Dynamic capability registration details** — LSP's `client/registerCapability` mechanism (registering features after init) wasn't read in depth; relevant if archwright overlays ever need to add checks after project scanning rather than at load time.
2. **How OTel governs promotion** — the process by which a signal in a language SDK moves Development → Beta → Stable (who signs off, what criteria) is in SIG process docs not reviewed here; relevant if archwright wants promotion criteria for domain overlays.
3. **Aggregator curation criteria** — what quality bar nvim-treesitter/registry applies before listing a parser (tests? maintenance activity?) would inform how a lightweight overlay catalogue vets entries.
4. **Capability granularity trade-off** — LSP has ~50+ fine-grained capabilities; OTel has 4 coarse signals. Where should archwright domain overlays sit on that spectrum (per-predicate vs per-check-kind)?
