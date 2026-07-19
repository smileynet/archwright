---
kind: discovery
id: design-system
status: proposed
area: ui
serves: []
---

# Design System: Archwright Report

<!-- Layered artifact (grill Q3): permanent human reference; tension-resolving
     choices graduate to design/patterns/ on approval; token tables are
     machine-readable. Ledger rules: tools/templates/discovery-ledger.md. -->

## Jobs (anchor for every screen)

| Job | Performer | Circumstance | Done when |
|-----|-----------|--------------|-----------|
| J1: "Something failed — what do I do?" | developer | a check run / CI just flagged the project | they know the action (fix code / revisit a design rule / check is broken) without reading archwright docs |
| J2: "Is this project's design in good shape?" | reviewer/lead, cold reader | opening the report with no archwright knowledge | a trust verdict in one glance, exceptions explained in plain words |

## Principles

| # | Principle | Prior art | Serves |
|---|-----------|-----------|--------|
| 0 | Plain-language surface: the primary layer uses no archwright vocabulary — outcomes and actions only; methodology terms appear solely inside progressive-disclosure details | plain-language error message research (NN/g error-message guidelines, 2024); progressive disclosure (NN/g, 2006) | design-system#D002 |
| 1 | JSON is canonical; web and markdown are one-way projections regenerated from it — never edited, never merged sideways | ESLint formatter architecture (docs, 2025); Playwright blob→html/json merge pipeline (2023); SARIF as canonical interchange (OASIS 2.1.0, 2020) | (three-surface decision, D001) |
| 2 | Three-level drill-down: overview → filterable list → item detail; never deeper | Playwright HTML report (2024); SonarQube issues UI (2024); Allure 2 (2024) | — |
| 3 | Counts are controls — every summary number filters or highlights the list below it | coverage.py htmlcov keyboard toggles (7.x, 2024); Playwright stat-chip filters (2024) | — |
| 4 | Status is never color alone: every status pairs color + glyph/label (works in grayscale, meets WCAG SC 1.4.1) | WCAG 2.2 SC 1.4.1 Use of Color (W3C, 2023); GitHub Primer status colors (2024) | — |
| 5 | Self-contained single-file HTML: zero build, no webfonts, no JS beyond native `<details>` + optional filter toggles; travels as a CI artifact | Playwright self-contained report (2024); coverage.py static htmlcov (2024); single-file report pattern (research 2026-07-19) | — |
| 6 | Vertical budget goes to the payload (violations, evidence, provenance), not header chrome | SonarQube SONAR-27483 complaint history (2024) | — |

## Tokens (machine-readable)

```yaml
tokens:
  type:
    prose: "system-ui"
    code: "ui-monospace stack; tabular-nums on count columns"
    scale: { body: "15", heading: "20/26", caption: "12.5" }
  spacing: { unit: "8px grid", allowed: [8, 16, 24, 32] }
  status_roles:            # color + glyph + label, always together (P4)
    pass:    { color_role: success,  glyph: "✓" }
    fail:    { color_role: danger,   glyph: "✗" }
    warn:    { color_role: warning,  glyph: "⚠", note: "baselined debt lands here" }
    skip:    { color_role: neutral,  glyph: "○", note: "coverage statement, not a pass" }
    pending: { color_role: info,     glyph: "…" }
  confidence_glyphs: { high: "★★", medium: "★", advisory: "—" }   # detail layer ONLY (D002) — surface uses vocabulary map below
  vocabulary:              # machine-readable translation map (D002) — surface term per internal term
    violation:            "needs attention"
    baselined:            "known issue (accepted)"
    skip:                 "couldn't be checked"
    pending:              "check not built yet"
    remaining_delta:      "issues to fix"
    fix-implementation:   "fix the code"
    fix-spec:             "revisit this design rule"
    fix-check:            "the check itself is broken"
    "confidence ★★":      "firm rule — needs your sign-off to change"
    "confidence ★":       "strong guideline"
    "confidence —":       "advisory"
    force:                "why this rule exists"
    evidence_ledger:      "rules earning (or losing) trust"
  themes: "light + dark via CSS custom properties, prefers-color-scheme; AA contrast verified per theme"
```

## Component Guidance

### Status chip
- **Use when:** any pass/fail/warn/skip/pending signal appears
- **Not when:** decorative accents
- **States it must have:** default only (chips are read-only)

### Count-filter chip
- **Use when:** a summary count has a corresponding list on the same page
- **Not when:** the count has nothing to drill into (then it's plain text)

### Provenance breadcrumb
- **Use when:** showing a violation's chain (force → pattern → spec → check)
- **Not when:** listing artifacts without a chain

## Decisions

### D001 — Three-surface output architecture
- **Category:** structure
- **Origin:** user
- **Decision:** The web report is the primary structure for users to consume archwright's information; markdown is the secondary user-documentation source and a source for agents; JSON is for agents/scripts.
- **Rationale:** "run a ui design to consider a web report as the primary structure for users to consume information provided by archwright, with markdown as secondary user documentation source and a source for agents, and json for agents/scripts."
- **Alternatives:** Markdown-primary (current de-facto state); terminal-output-primary; interactive SPA dashboard.

### D002 — Plain-language, low-cognitive-load surface
- **Category:** experience
- **Origin:** user
- **Decision:** The report's UX uses no archwright jargon on its primary surface; reporting is low cognitive-complexity and actionable without understanding archwright. Methodology vocabulary (forces, specs, baselines, ★★) appears only inside progressive-disclosure details. Anchored on jobs J1/J2.
- **Rationale:** "consider the jtbd, and that we want to ux to focus on non-jargon, low cognitive-complexity reporting that is actionable to users without requiring them to understand archwright specifically"
- **Alternatives:** Archwright-vocabulary-verbatim surface (rejected — requires methodology literacy); two separate reports for expert vs cold readers (rejected — one artifact, layered disclosure instead).

### D003 — Approvals vs decisions: two distinct ask-types
- **Category:** experience
- **Origin:** user
- **Decision:** Items with a clear right answer (recommendation attached) are framed as "approvals needed" — the report proposes, the user signs off. Items with genuine ambiguity are framed as "decisions needed" and are never auto-resolvable. Every actionable item belongs to exactly one of the two.
- **Rationale:** "both needs attention cases appear to have a clear right answer, these should be framed as 'approvals needed' ... consider situations where user needs to make decision/ resolve ambiguity."
- **Alternatives:** Single undifferentiated "needs attention" list (rejected — mixes routine sign-offs with judgment calls, raising cognitive load on both).

### D004 — Auto-approve, configurable locally, off by default
- **Category:** technical
- **Origin:** user
- **Decision:** Approvals (never decisions) can be auto-approved via local mise settings (e.g. `mise.local.toml`), off by default. Decisions are excluded from auto-approval unconditionally — the ★★ hard floor and ambiguity items always wait for a human.
- **Rationale:** "it should be configuratble via local mise settings to auto-approve (off by default)."
- **Alternatives:** Global config file (rejected — approval appetite is per-developer/per-machine, mise.local.toml is gitignored by convention); per-run CLI flag only (rejected — repetitive for the routine case).

### D005 — Static HTML first; responses recorded agent-readable; live GUI backlogged
- **Category:** technical
- **Origin:** user
- **Decision:** The report ships as static, self-contained HTML. Its interactive controls (approve, option choice, freeform text) record state into an artifact an agent or script can process (a structured response file the user saves/hands back). A live served GUI is an explicit backlog item, not part of this design.
- **Rationale:** "let's start with static html that records state to something an agent can process, as a backlog item we'll explore a live gui"
- **Alternatives:** Local companion server (`--serve` + localhost endpoint) — deferred to the live-GUI backlog item; agent-only interaction without a report artifact.

### D006 — Behavior-first information architecture
- **Category:** structure
- **Origin:** user
- **Decision:** The report leads with what the app DOES: the state machine / business logic rendered as a diagram a non-technical reader can follow. Drill order from there: (1) the behavior and its details → (2) the rules that verify it → (3) optionally, how we arrived at those conclusions (the decision story). Rationale/provenance is the deepest layer, never the surface.
- **Rationale:** "I want to understand what does the app do. The state machine / business logic are core to how the app functions. even a non-technical user should be able to look at the diagram and understand how things will behave. consider how, from there, a user might want to drill in to understand the details behind each, first understanding the behavior and it's details, and from there _possibly_ wanting to know how we arrived at those conclusions"
- **Alternatives:** Promise-grouped surface (superseded wf-all-clear#D001 direction); check-status-first surface (remains the posture only when items need attention — wf-overview).

## Graduates to Patterns

| Tension resolved | Ledger entry | Pattern (filled at graduation) |
|------------------|--------------|-------------------------------|
| human-readability vs machine-canonicality | design-system#D001 | — |

## Not Resolved Here

- [ ] Print stylesheet
- [ ] Trend/run-over-run display in a static report (needs a data decision first)
- [ ] Warn/amber AA-compliance exact values on light theme
- [ ] Whether the report ships with archwright core or as a separate projection tool
