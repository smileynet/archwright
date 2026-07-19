---
name: archwright-woz-import
description: "Import a wizard_of_oz game-design session into archwright discovery artifacts: mechanical export→ledger conversion, then interpretation — force evidence, model seed from the simulation log, screen flow from wireframes, draft behavior seeds with from_woz provenance. Use when bringing a WoZ/wizard_of_oz session or its JSON export into a project's design space. Trigger: import woz session, wizard of oz export, bring in the woz session, woz-session json, import game design session."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright WoZ Import

Discovery-track skill (ADR 0011, grill Q01/Q05): consume a wizard_of_oz session export (`woz-session/v1` JSON) into the target project's `design/` space. The import is a **snapshot with citation, refreshed deliberately** — wizard_of_oz stays standalone and owns the session format; archwright is a consumer, never a peer.

Two stages, split by the constitution (agent IS the system; tools are mechanical servants):

1. **Mechanical conversion** — `tools/archwright-import-woz.py` (never hand-convert: agent approximation of a mechanically-parseable format is the drift failure mode, grill Q05).
2. **Interpretation** — this skill's work: force evidence, model seed, screen flow, draft behavior seeds.

## Process

### 1. Obtain the export

- Given a session `.md` file: run wizard_of_oz's exporter — `python3 <wizard_of_oz-repo>/tools/export-session.py <session.md> > export.json`. Validation failure = exit 1 with errors on stderr and NOTHING on stdout — fix the session in wizard_of_oz, don't patch the JSON.
- Given JSON directly: proceed. The tool validates the `format` field; an unknown version is a loud failure, never a best-effort parse.

### 2. Convert (mechanical)

```bash
python3 <archwright-repo>/tools/archwright-import-woz.py export.json [-o design] [--force]
```

Produces `design/discovery/woz/woz-<session-id>.md` — a `kind: discovery` artifact, `status: proposed`, with:
- the full ledger (active + superseded entries in append order; `SUPERSEDES` rendered idempotently — exports may already embed the marker in the decision text (salvage-run does), marker-free exports get it prepended; either shape renders it once, and the ticket-026 validator excludes superseded targets),
- categories mapped consumer-side (identity except woz `aesthetic` → core `experience`),
- session summary, fenced simulation log + wireframes (verbatim evidence — fencing keeps transcript D-mentions out of the conservation citation graph),
- Not Resolved Here from the export's `unresolved` block.

Exit 1 = contract violation (unknown format version or category — regenerate the export in wizard_of_oz), nothing written. Exit 2 on an existing import without `--force` — refreshing a snapshot is a deliberate act. Re-running after a session evolved is the intended refresh path; interpretation artifacts (step 3) cite entry anchors, which are append-only stable.

### 3. Interpret (this skill's work)

Work from the imported artifact — entries are truth; cite every claim as `woz-<session-id>#D{NNN}` (conservation, grill Q6):

1. **Force evidence:** for each decision that evidences an existing force, append the rationale verbatim to the force file, cited. Decisions that surface NEW desires (the elevator pitch, aesthetics, MLP features are desire-dense) → flag for the forces phase; never silently create force files.
2. **Model seed:** compile `design/discovery/woz/model-seed.md` from the simulation log — states/modes the sim walked through, events the player actions imply, per-beat escalation. Every element cites its anchors.
3. **Screen flow:** wireframes in the sim log → screen-flow section of the seed (what the player SEES at each beat, transitions between them), each citing the beat's decisions.
4. **Draft behavior seeds:** candidate state machines (e.g., run lifecycle, resource states) as SEED SECTIONS inside the model seed — with `from_woz:` anchors. These are inputs for the model/derive phases; never write `design/specs/` files here.
5. **Unconsumed decisions:** active entries no interpretation output cites go under an explicit `## Unconsumed decisions` list with reasons (nothing lost).
6. **Surface `inferred` entries** for confirmation — unconfirmed inferred entries block graduation (ledger rules). Confirmations may exist only as prose in a later entry's decision text ("CONFIRMS D005") — `woz-session/v1` has no structured confirms field, so the mechanical layer can't see them; read the ledger and cite the confirming entry when resolving an inferred entry's status (field case: salvage-run D024 confirms D005, 2026-07-19).

### 4. Validate + graduate

```bash
python3 <archwright-repo>/tools/archwright-validate.py design/discovery/woz/*.md
python3 <archwright-repo>/tools/archwright-validate.py --links design/
```

While `proposed`, conservation findings are warnings (an un-interpreted import warns on every active entry — expected). On operator approval flip `status: approved` — conservation becomes errors, so consume-or-defer must be complete first. Graduated decisions enter the pipeline at the `resolve` seam as pre-resolved tensions (one batched confirmation).

## Does NOT

- Own or patch the session format — `woz-session/v1` is wizard_of_oz's external contract; format errors route to wizard_of_oz
- Hand-convert ledgers the tool can convert (drift failure mode)
- Write `design/specs/` or `design/models/` files (derive/contract/model phases own those — this skill seeds)
- Create force files for newly surfaced desires (flag for the forces phase)
- Auto-approve the import — approval is the operator's, and it arms the conservation gate
