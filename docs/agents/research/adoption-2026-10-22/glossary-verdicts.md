> Recorded at `ea37928`, before adoption: paths cite the old `.memory/` layout.

# Archwright CONTEXT.md Glossary — Verdicts

Cross-checked each of the 49 bold terms in `~/code/archwright/.memory/CONTEXT.md` against code (tools/*.py, tools/check/, tools/*-schema.yaml), skills/*/SKILL.md, steering/archwright-conventions.md, docs/glossary.md, and .memory/adr/. Code evidence preferred. Read-only; no edits made in archwright.

| Term | Verdict | Evidence |
|------|---------|----------|
| Archwright | confirmed | .memory/adr/0001-agent-is-the-system.md:12 — "The AI agent IS the system … Tools are mechanical servants" |
| Force | confirmed | tools/archwright-validate.py:34 — `force` in VALID_KINDS; :123 `validate_force` |
| Desire | confirmed | docs/glossary.md:8 — attractive force, functional/emotional/social jobs |
| Constraint | confirmed | tools/archwright-validate.py:142 — constraint forces require `hardness` (hard\|soft) |
| Tension | confirmed | tools/pattern-schema.yaml:40 — fog = unresolved tension; docs/glossary.md:11 |
| Pattern | confirmed | tools/pattern-schema.yaml (pattern status enum :38) + docs/glossary.md:12 serves link |
| Resolution | confirmed | .memory/adr/0003-resolves-into-not-compiles.md:12 — "creative resolution followed by formal verification" |
| Resolves into | confirmed | .memory/adr/0003-resolves-into-not-compiles.md:8,12 — reject "compiles", use "resolves into" |
| Hands-down | confirmed | docs/glossary.md:60 — downward resolution, concretizes |
| Pass-up | confirmed | skills/archwright-passup/SKILL.md:14 — level-terminating, confidence-gated, provenance |
| Provenance link | confirmed | skills/archwright-passup/SKILL.md:12 "same provenance links, opposite direction"; :69 chain walk |
| Counterexample | confirmed | tools/check/alloy.py:139 — "counterexample found — invariant violated" |
| Contrast pair | confirmed | tools/check/trace.py:232 — `"contrast_pair": {"expected", "actual"}` |
| Confidence (★★/★/—) | confirmed | docs/glossary.md:18 map; tools/stacks/REGISTRY.yaml tiers; passup SKILL.md:102 ★★→escalate |
| Scenario walk | confirmed | docs/glossary.md:34 — walk desire through architecture (concept-level; no tool anchor) |
| Quiescence | confirmed | skills/archwright-passup/SKILL.md (quiescence); docs/glossary.md "done state … convergence" |
| State graph | confirmed | docs/glossary.md:45 — central anchor, states+transitions, human/AI/checkable |
| Behavior (spec kind) | confirmed | tools/spec-schema.yaml:2 "behavior specs (statechart definitions)"; :14 const: behavior |
| Spec | confirmed | tools/archwright-validate.py:34 VALID_KINDS; :43 LINK_REF_PATTERN kind:id refs |
| Contract (spec kind) | confirmed | tools/contract-schema.yaml; spec-schema.yaml:167 contract ref; data shape + lifecycle |
| Constraint (spec kind) | confirmed | tools/archwright-validate.py:34 — `constraint` kind; carries own check strategy |
| Dependency (spec kind) | confirmed | tools/archwright-validate.py:34 — `dependency` kind; static-analysis checked |
| Proxy invariant | confirmed | skills/archwright-review/references/visual-conformance.md (proxy invariant); docs/glossary.md |
| Lift (re-abstraction) | confirmed | skills/archwright-passup/SKILL.md:69 — "translate the signal into that level's vocabulary" |
| Promotion | confirmed | skills/archwright-passup/SKILL.md:65 — "extended-state variable → discrete mode, unnamed writer → named actor" |
| CEGAR | confirmed | skills/archwright-passup/SKILL.md (CEGAR); docs/glossary.md:58 spurious-vs-real fork |
| Baseline | confirmed | tools/archwright-check.py:11 — ".archwright-baseline.json … --update-baseline … NEVER adds" (CK-07/08) |
| Fingerprint (aw/v1) | confirmed | tools/check/common.py:12 `FINGERPRINT_ALGO="aw/v1"`; :142 sha256(spec_id+invariant+path+content)[:16], line nums dropped |
| Evidence ledger | confirmed | tools/check/ledger.py:1 ADR 0009; :60-63 demotion/promotion-candidate; :4 "human RATIFICATION" |
| Commit-binding (code_state) | confirmed | tools/check/ledger.py:57,68-69 — code_state git commit+dirty, "dedup identity UNCHANGED"; check-output-schema.yaml:124-131 |
| Force file | confirmed | tools/archwright-forces-gen.py:59 `design/forces`; validate.py:131 kind must be 'force' |
| HITL-blocking gate | confirmed | .memory/adr/0007-hitl-only-gates.md:17 — "HITL-blocking or flow-through"; :13 resolve/grill/★★ |
| Gated (pattern status) | confirmed | tools/archwright-validate.py:177 — gated requires non-empty `gated_on` (ticket 011); pattern-schema.yaml:42 |
| Span | confirmed | steering/archwright-conventions.md (span, flow-through, span boundary); ADR 0007 |
| Protocol cluster (contract exception) | confirmed | skills/archwright-contract/SKILL.md:82 — "Sanctioned exception — protocol cluster … named for the protocol" |
| Contract candidate | confirmed | tools/archwright-validate.py:843-845 — candidate events global namespace; shared:true opt-in (ADR 0013) |
| Domain overlay | confirmed | tools/domains/{game,web,general}/scales.yaml + predicates.yaml + detect.yaml present |
| Extension Protocol | confirmed | .memory/adr/0008-extension-protocol.md; docs/glossary.md:58 pending→★→★★ |
| Stack adapter | confirmed | tools/stacks/REGISTRY.yaml + gdscript/python/typescript dirs present |
| Discovery track | confirmed | .memory/adr/0011-discovery-track.md; skills/archwright-discover-ui/SKILL.md |
| Seam contract | confirmed | skills/archwright-resolve/SKILL.md + archwright-passup/SKILL.md (seam); decision ledger format |
| Decision ledger | confirmed | tools/templates/discovery-ledger.md present (D{NNN}, SUPERSEDES) |
| Artifact gap | confirmed | skills/archwright-model/SKILL.md (conservation/artifact gap); discover-ui SKILL.md |
| Conservation check | confirmed | skills/archwright-model/SKILL.md, archwright-woz-import/SKILL.md, tools/archwright-import-woz.py |
| Rubber-stamp guard (calibration) | confirmed | skills/archwright-discover-ui/SKILL.md:14 — "3+ consecutive `suggested` decisions → stop" |
| Reconciliation pass | confirmed | docs/glossary.md:58 + steering/archwright-conventions.md — per-area then all-up synthesis |
| Posture (report) | confirmed | tools/report/derive.py:319-326 — posture(): tool-error/empty-project/needs-attention/all-clear |
| Ask-type (report taxonomy) | confirmed | tools/report/derive.py:15 — ASK_DECISION/ASK_APPROVAL/ASK_SUGGESTION; :257 auto-approvable |
| Blind battery (visual conformance) | confirmed | skills/archwright-review/references/visual-conformance.md:18-20 — ≥1 neutral question per D-anchor, fresh session, blind |

## Contradictions (characterized fact)

None found. All 49 terms are confirmed against code/docs; no term's CONTEXT.md definition contradicts code or the `docs/glossary.md` definition of the same term.

Notes on the CONTEXT.md ↔ docs/glossary.md overlap (consistent, not contradictory):
- **Confidence**: both name CONTEXT.md as the anchor and point to `docs/glossary.md`'s map table for derived scales — complementary, agree on ★★/★/— semantics.
- **Force / Desire / Constraint / Tension / Pattern / Resolution / State graph / Hands-down / Pass-up / Provenance link / Counterexample / Scenario walk / Quiescence / Lift / Promotion / Extension Protocol / Stack adapter / Reconciliation pass**: appear in both glossaries with the same meaning; CONTEXT.md adds the "_Avoid_" guidance, docs/glossary.md adds flow/visualization detail. No definitional divergence.
- docs/glossary.md defines a few terms CONTEXT.md does not (Consequence, Guard, Event alphabet, Ingress/egress, Invariant tiers, Pattern status, visualization primitives) — additive, out of scope for this term-by-term check, not conflicts.
