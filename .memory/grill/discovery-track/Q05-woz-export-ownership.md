# Q5: woz-session-export — skill vs tool, parser ownership

**Status:** Decided 2026-07-18
**Decision:** Option B — exporter tool lives in wizard_of_oz (session → neutral JSON); archwright skill consumes the JSON and does the interpretation.

## Question

Is the wizard_of_oz session export a skill, a tool, or both — and which project owns the mechanical parser?

## Research

- Skill/tool split self-answered by archwright's constitution ("agent IS the system; tools are mechanical servants"): the ledger parse is mechanical and provably parseable — wizard_of_oz's `validate-session.py` already parses entries, supersession refs, and category counts. Pure-skill parsing rejected: agent approximation of a mechanically-parseable format is the drift failure mode [superdesign.dev 2026, same evidence as Q3].
- Parser ownership: Q1 made the session format wizard_of_oz's external contract. A parser in archwright would break silently on format drift — the exact failure the "consumer, never peer" rule avoids.

## Decision Detail

1. **wizard_of_oz gains `tools/export-session.py`** — session markdown → neutral JSON (frontmatter, active decisions post-supersession-filtering, sim log segments, wireframes). Reuses validate-session parsing logic. Generically useful to any consumer, not archwright-specific.
2. **The JSON is the inter-project contract** — versioned, testable from both sides.
3. **Archwright's discovery skill consumes the JSON** for interpretation: decisions → force evidence, sim log → model-seed states/events, wireframes → screen flow, draft behavior spec with `from_woz:` provenance.
4. **Conformance at birth** (Extension Protocol): golden corpus with salvage-run as passing scenario + a deliberately malformed ledger as violating scenario (non-zero exit, never silent partial export).

## Implications

- T7 splits: T7a (wizard_of_oz repo: exporter + corpus — note this crosses into wizard_of_oz's release scope, coordinate with its plan) and T7b (archwright: consuming skill + category mapping per Q2).
- Category translation (woz enum → core-5 + game extensions) lives on the archwright side (consumer owns its own mapping).
