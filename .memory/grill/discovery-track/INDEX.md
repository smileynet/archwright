# Grill Session: Discovery Track (ADR 0011 ratification)

**Started:** 2026-07-18
**Topic:** Ratify ADR 0011 (discovery track) — 6 open questions with recommended dispositions
**Inputs:** `.memory/adr/0011-discovery-track.md` (proposed), `.memory/specs/discovery-track.md`, `.memory/research-discovery-*.md` (4 files), `~/code/wizard_of_oz` design corpus

## Questions

| # | Question | Status | Origin | Decision |
|---|----------|--------|--------|----------|
| Q1 | wizard_of_oz relationship: standalone + import/export vs absorb | **decided** | suggested | A — standalone + import/export; imports are cited snapshots ([Q01](Q01-woz-relationship.md)) |
| Q2 | Ledger category enum: fixed core + domain extension vs per-domain | **decided** | suggested | A — core 5 (scope, experience, structure, technical, meta) + overlay extensions ([Q02](Q02-category-enum.md)) |
| Q3 | Design-system artifact placement | **decided** | suggested | C+C1 — layered: doc stays in discovery/ui, tensions graduate to patterns, tokens machine-readable + checkable ([Q03](Q03-design-system-placement.md)) |
| Q4 | Grill sessions adopt the ledger format? | **decided** | suggested-amended | C — field-level unification; guard recalibrated: surfacing not tripwire in grills, tripwire stays for creative sessions ([Q04](Q04-grill-ledger-unification.md)) |
| Q5 | woz-export: skill vs tool | **decided** | suggested | B — exporter in wizard_of_oz (session → neutral JSON, the inter-project contract); archwright skill interprets ([Q05](Q05-woz-export-ownership.md)) |
| Q6 | LEC-equivalent for agent transforms; commit-binding | **decided** | suggested | 6a: golden corpus + conservation check (nothing invented / nothing lost, citation-graph walk); 6b: deferred → ticket 018 ([Q06](Q06-lec-equivalent-commit-binding.md)) |

## Outcome

All 6 questions decided 2026-07-18. ADR 0011 amended to Accepted with grill verdicts. Origin distribution: 5 suggested, 1 suggested-amended (Q4 — guard recalibration was operator-originated). Session closed.
