> Recorded at `ea37928`, before adoption: paths cite the old `.memory/` layout.

# archwright: STAGED glossary terms (not committed to GLOSSARY.md)

Inferred during adoption; confirm / correct / reject each before it enters `GLOSSARY.md`.

**Spec (requirements doc vs design spec)** — STAGED
Two artifacts share the word. A *design spec* is a typed, checkable `design/specs/` file
(`kind: behavior|contract|constraint|dependency`) that `archwright-check` verifies. A
*requirements spec* is a planning document in `docs/agents/specs/` (ex `.memory/specs/`, e.g.
`polyglot-check-tooling.md`, `discovery-track.md`). Grey-matter's GLOSSARY uses bare "spec" for the
requirements document.
_Avoid_: bare "spec" where both could be meant; say "design spec" or "requirements spec".
Evidence: `tools/spec-schema.yaml:2`; `.memory/specs/discovery-track.md:1` ("All-Up Plan"); GLOSSARY "Spec" entry
defines only the design-spec sense.

**Glossary (agent glossary vs shipped glossary)** — STAGED
`GLOSSARY.md` (ex `.memory/CONTEXT.md`) is the repo's agent vocabulary. `docs/glossary.md` is the
shipped methodology glossary deployed into `archwright-survey/references/glossary.md`.
_Avoid_: "the glossary" without saying which.
Evidence: `tools/deploy-skills.sh:154-155`, `.gitignore:12,16`; finding J4.

**Field evidence** — STAGED
A sanitized digest a field run deposits into this repo (`field-evidence/<alias>-<date>.yaml`),
distinct from the *evidence ledger* (`.archwright-evidence.json`, tool-appended confidence events in
a target project) and from recorded check output.
_Avoid_: bare "evidence" when the ledger or a field digest is meant.
Evidence: AGENTS.md:265 (Field-evidence convention; no `field-evidence/` dir exists yet); GLOSSARY "Evidence ledger".

**Area** — STAGED
A partition of a large target project that gets its own full pipeline run before an all-up
reconciliation pass (forces/tensions outputs are per-area: `archwright-forces-<area>.yaml`).
_Avoid_: "module" or "domain" (domain = vocabulary overlay; see "Domain overlay").
Evidence: `skills/archwright-tensions/SKILL.md:66`; steering/archwright-conventions.md (Run
Scoping); GLOSSARY "Reconciliation pass".
