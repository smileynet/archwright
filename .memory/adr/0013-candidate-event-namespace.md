# ADR 0013: Candidate Event Names Are a Checked Global Namespace

Date: 2026-07-25
Status: accepted
Ticket: 050

## Context

`--links` builds one `all_candidate_events` set across every model file and
matches contract-spec coverage by bare event name. Two areas that independently
model a same-named event alias each other: the dp-poc field run (2026-07-22)
had p1 (catalog-interop) and f1 (clean-rooms) both declare `CELL_RESULT`, and
coverage matching produced a spurious "covered by 2 contract specs" error on
unrelated seams. The field fix — manual rename plus a "vet names before
writing" convention — scales badly with area count and relies on agent memory.

Ticket 050 offered two designs:

1. **Collision lint** — same name in 2+ model files = error, with a `shared:
   true` opt-out on every declaration for genuinely cross-area events.
2. **Per-model scoping** — coverage resolves within the declaring model first;
   cross-model coverage only via explicit reference.

## Research (rule 3 — event-name collision handling in schema ecosystems)

Full report: `.scratch/research/event-namespacing.md` (subagent pass,
2026-07-25; ephemeral — load-bearing findings summarized below):

- **No surveyed ecosystem silently scopes boundary-crossing event names.**
  Either names carry ownership prefixes (CloudEvents reverse-DNS `type`,
  protobuf packages + Buf's ≥3-component lint), a registry arbitrates at
  registration time (Buf Schema Registry rejects duplicate type names at push;
  Confluent Schema Registry fails incompatible same-subject registrations), or
  both.
- **Silent aliasing is the documented hazard**, not the safeguard: Confluent's
  RecordNameStrategy lets compatible same-named schemas alias across topics
  unnoticed; protobuf collisions surface late and per-language (C++ compile
  error vs Go init panic vs Python DescriptorPool error).
- **Deliberate sharing is always explicit**: import + fully-qualified reference
  (protobuf), `$ref` to one canonical definition (AsyncAPI), adopting the
  owner's prefixed type verbatim (CloudEvents) — never independent
  redeclaration that happens to match.

## Decision

**Option 1 — collision lint with a mutual `shared: true` opt-out.**

- An event name declared as a contract candidate in 2+ model files is a
  `--links` ERROR naming every declaring file, unless EVERY declaration carries
  `shared: true`.
- `shared: true` on a declaration no other model repeats is a WARNING (stale
  flag or missing counterpart) — non-fatal, because area A legitimately
  declares first during incremental modeling.
- `shared` must be a boolean where present (schema-level error, validate_model).
- The exactly-one-owning-contract-spec rule is unchanged and applies to shared
  events too (reported once per event, not once per declaring model).
- Namespace semantics are otherwise unchanged: one global namespace, matching
  the research consensus and the C7 one-spec-per-event ownership model.

Option 2 (per-model scoping) is REJECTED: silent scoping is the failure mode
the surveyed ecosystems avoid — two areas modeling the SAME real event under
one name would quietly get two divergent contract specs, un-flagged, which is
worse than the spurious error it fixes. Scoping also changes what a bare event
name MEANS in every existing artifact (kind-level semantics change); the lint
only adds a check plus one opt-in field.

## Consequences

- The dp-poc collision shape now fails loudly with a rename-or-declare-shared
  instruction instead of a misleading coverage error. Area-prefixed renames
  (the field fix, `MEASUREMENT_CELL_RESULT`) remain the default remedy,
  matching CloudEvents/Buf prefix practice.
- Genuinely cross-area events (x1's consumer-contract events) declare
  `shared: true` in each model; one contract spec owns the payload.
- The archwright-model skill's name-vetting convention becomes a backstop
  rather than the only defense.
- Conformance: `tests/fixtures/candidate-collision/` (collision, shared-ok,
  half-shared, lone-shared, bad-shared-type) wired into the fixture suite
  § Candidate Event Collisions.
