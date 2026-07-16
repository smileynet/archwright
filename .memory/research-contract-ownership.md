# Research Synthesis: Contract Spec Ownership & Granularity (C7)

2026-07-16. Three parallel research tracks (raw: `.scratch/research/{contract-ownership,contract-granularity,spec-addressability}.md`). Feeds the C7 decision: who emits contract specs, and does one-spec-per-file bend for event groups?

## Findings

### F1 — A dedicated contract phase is the industry norm; modeling never owns contracts
No surveyed methodology (DDD context mapping, event storming, contract-first/API design-first, Pact CDC) places contract production in the domain-modeling phase. Modeling identifies message **identity, direction, and semantics**; a dedicated phase between modeling and implementation formalizes **payload shapes** (OpenAPI/AsyncAPI/Avro/Pact). Event-storm artifacts are discovery scaffolding that *link to* schemas — they never restate them. [contract-ownership]

### F2 — Duplication is avoided by direction, not deduplication
The universal anti-pattern is a shared "common types" artifact edited by two layers. Instead: each layer references the other one way (model → names the event; contract → defines the payload, links back), downstream artifacts are *generated/derived from* the contract rather than restating it, and registries enforce evolution on the contract alone. Ownership is directional: **publishers own event contracts**; consumers verify (CDC) but don't own. [contract-ownership]

### F3 — File granularity follows the unit of independent evolution
Cross-ecosystem consensus (protobuf 1-1-1 rule, AsyncAPI file-per-application, OpenAPI multi-file + bundle, Kafka subject-per-event-type): the unit that **evolves and is depended-on independently gets its own file**; grouping happens via directories/packages, never file concatenation; a mechanical bundle layer serves single-artifact consumers. Protobuf's 1-1-1 explicitly allows an exception for **tightly-coupled messages that evolve in lockstep**. Open edX chose per-topic+type registry granularity specifically to preserve independent evolution — and rejected grouped Avro unions for killing it. [contract-granularity]

### F4 — Addressability decides whether one-per-file is *required*
Where identity is language-level (Terraform addresses, Rego packages, K8s kind/name), communities group freely; where the file IS the addressing scheme (Helm templates), one-per-file is a hard rule. Archwright's `kind:id` gives language-level addressability — so one-per-file is not needed for *referencing* — but each spec's independent check/validate/confidence lifecycle makes specs Helm-like. The load-bearing requirement either way: a **deterministic `kind:id` → file-path mapping**. [spec-addressability]

## Recommendation (updates C7)

**R1 — Contract phase solely owns contract specs.**
- `archwright-model`: stop emitting contract specs (Step 10). Instead emit a **contract-candidates list** (event name, producer actor, consumers, direction) — identity and semantics only, no payloads.
- `archwright-contract`: formalizes each candidate into a contract spec, organized **per owning producer actor**, each spec carrying `from_model:` provenance back to the model entry (F1, F2).
- `archwright-derive`: delete its contract-derivation subsection entirely; behavior specs reference contract specs via `consumes` links and never restate payload fields (already partially stated — make it the only text).

**R2 — One spec per file stands; the spec unit is the independently-evolving contract.**
- Default: **one contract spec per event type** (independent evolution, per-file lifecycle — F3).
- Sanctioned exception (protobuf-style): a **tightly-coupled protocol cluster** from ONE producer whose messages evolve in lockstep (e.g., request/accept/reject of one transfer protocol) may be a single spec, named for the *protocol*, not the system. The fixture's `ball-possession-events.yaml` (possession_changed + transfer_rejected, one producer, one protocol) is legal under this exception.
- Prohibited: per-system grand event files (`<system>-events.yaml` as a dumping ground) — that's the shared-artifact anti-pattern (F2) and kills independent evolution (F3). The contract skill's current guidance must change.
- Naming rule (F4): file path = `design/specs/<spec-id>.yaml` always — deterministic `kind:id` → path mapping stays absolute.

**R3 — Gap worth noting (future):** no surveyed methodology mechanically detects semantic drift between contract and domain model. `archwright-check` could — contract `from_model:` links make it checkable. Candidate for Phase 5 backlog.

## Skill Edits Required (once ratified)
1. `archwright-model` Step 10: contract specs → contract-candidates list.
2. `archwright-contract`: per-producer organization; protocol-cluster exception replaces `<system>-events.yaml` guidance; add `from_model:` provenance field.
3. `archwright-derive`: remove contract derivation subsection; keep only the cross-reference rules.
4. `tools/templates/spec-contract.yaml` + contract-schema.yaml: add `from_model:` field.
