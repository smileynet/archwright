---
kind: discovery
id: design-system             # file: design/discovery/ui/design-system.md — permanent home (grill Q3/C1)
status: proposed              # proposed | approved | superseded (026 schema enforces)
area: ui
serves: []                    # bare force ids the system-level choices serve
---

# Design System: Project Name

<!-- Layered artifact (grill Q3): this doc is the permanent human reference; its
     tension-resolving choices graduate to design/patterns/ on approval; its token
     tables are MACHINE-READABLE so constraint specs can check against them —
     prose-only design systems get approximated away by downstream agents
     [superdesign.dev 2026]. Decisions ledger rules: tools/templates/discovery-ledger.md. -->

## Principles

<!-- 3-6 principles. Each: one sentence, a named prior-art citation WITH year/version
     (pattern quality gates — no "it's standard practice"), and the force it serves. -->

| # | Principle | Prior art | Serves |
|---|-----------|-----------|--------|
| 1 | (e.g., One primary action per screen) | (source, year) | (force id) |

## Tokens (machine-readable)

<!-- The checkable layer. Downstream constraint specs target this block (Q3).
     Keep it small — tokens the wireframes actually use, not a speculative palette. -->

```yaml
tokens:
  spacing: { unit: "8px grid", allowed: [8, 16, 24, 32, 48] }
  type_scale: { body: "16", heading: "24/32", caption: "13" }
  color_roles: [primary-action, surface, surface-raised, danger, success, text, text-muted]
  interaction: { min_touch_target: "44px", focus: "visible always" }
```

## Component Guidance

<!-- Per recurring component: when to use, when NOT to, one ASCII sketch if shape matters. -->

### Component Name
- **Use when:** …
- **Not when:** …
- **States it must have:** (default / hover-focus / disabled / loading — per screen wireframes only reference, never redefine)

## Decisions

<!-- Ledger (tools/templates/discovery-ledger.md). System-level choices live HERE;
     per-screen applications live in that screen's wireframe file. -->

### D001 — Decision title
- **Category:** experience
- **Origin:** user
- **Decision:** …
- **Rationale:** "…"
- **Alternatives:** …

## Graduates to Patterns

<!-- On approval: the tension-resolving choices below go through archwright-formalize
     (each row cites its D{NNN} — the conservation anchors). Catalog content
     (tokens, component inventory) stays here; only genuine tension resolutions graduate. -->

| Tension resolved | Ledger entry | Pattern (filled at graduation) |
|------------------|--------------|-------------------------------|
| (e.g., density vs readability) | design-system#D00N | pattern:… |

## Not Resolved Here

- [ ] (system-level gaps: theming, dark mode, responsive breakpoints, motion language, accessibility beyond tokens)
