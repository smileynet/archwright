> Recorded at `ea37928`, before adoption: paths cite the old `.memory/` layout.

# archwright: adopt-project Steps 1-3 findings

Target: `~/code/archwright`, fast-forwarded from `f35b919` to `ea37928` (origin/main, 81 commits,
0 local) before the audit. Tracked tree was clean; untracked: `.scratch/HANDOFF.md`,
`.scratch/vision-probes/` (both gitignored). Dry-run and test runs of the relocation happened in a
throwaway clone (`/tmp/aw-clone`).

## Step 1: survey and classification

- **Archetype:** 4 (lightly-scaffolded middle) on a methodology repo that ships skills. One large
  AGENTS.md (304 lines, 33.8 KB), a live tkt board (`.tickets/`, 98 tickets, `config.toml` with
  `[close] require_resolution = true`), a crew-research `.memory/` (100 tracked files: adr 14,
  grill 16, lessons 19, specs 10, audit 7, spike-findings 5, research-extension-protocol 4,
  reflections 1, 24 loose files).
- **Polarity:** incumbent present, so **subsume**. The tracker is already tkt; nothing migrates.
  `tkt init --write` adds only the AGENTS block.
- **Agent layer:** AGENTS.md, `.memory/`, `.tickets/`, `.kiro/skills/repo-maintenance/`
  (project-local, "never deployed globally"; owns `run-fixture-tests.sh` + `deploy-skills.sh`),
  `mise.toml` tasks. No CLAUDE.md, `.cursor`, `.github`, `.agents/`. `.kiro/agents/` empty.
- **Shipped artifacts (product, not crew copies):** `skills/archwright-*` (16 skills) and
  `steering/{archwright-conventions,subagent-reliability}.md`, distributed by
  `tools/deploy-skills.sh` (`--tool kiro|claude|codex|agy`). The kiro-global copies are
  **symlinks into this repo** (`~/.kiro/skills/archwright-*`, `~/.kiro/steering/archwright-conventions.md`),
  so any edit is live everywhere at once. Also shipped: `docs/glossary.md` (deployed into
  `archwright-survey/references/glossary.md`), `tools/domains/`, `tools/stacks/`, `tools/templates/`.
  None is byte-identical to a crew-research skill; `steering/subagent-reliability.md` is a drifted
  older copy of crew-research's `subagent-reliability` (J3).
- **Not examined:** content of `tests/fixtures/` (70 files), `examples/` (52), `design/` (self-run
  artifacts), `tools/report/vendor/` (minified ELK). Grepped only for `.memory` mentions.

### Shipped skills, open-standard audit

All 16 `skills/*/SKILL.md` + `.kiro/skills/repo-maintenance`: `name` matches the dir,
descriptions 313-484 chars (≤1024), `metadata` inert. Grey-matter layout rules (bucket READMEs,
compass, `agents/openai.yaml`) are **N/A**: they ship through archwright's own installer.

### Relocation hazard (the riskiest finding)

The relocation script rewrites every repo-rooted `.memory/...` mention it can map. In the shipped
skills and steering, most `.memory/` mentions mean **the target project's** `.memory/`, not
archwright's (survey:77-81 reads a target's `.memory/adr/`, `.memory/specs/`, `.memory/CONTEXT.md`).
A blanket rewrite would silently retarget the methodology at paths target projects don't have.
So `skills/` and `steering/` are passed as `--evidence-dir` (no rewrite), and the one
archwright-self pointer in a skill is fixed by hand (S3). The same hazard hit two rewritten
non-shipped lines (S1).

## Conformance-audit Phase 1

### Safe-auto-fix

| id | Artifact | Finding | Rule |
|---|---|---|---|
| S1 | `.tickets/034-skill-skeleton-gate-reflections.md:33`, `.memory/PLAN.md:318` | The rewrite wrongly retargets a **target-project** path (`.memory/reflections/` "in target project") and a **cross-repo** citation (crew-research `.memory/specs/ticket-cli-spec.md`). Restore both to their original text after apply. | relocation.md step 4 (cross-repo / non-local mentions stay) |
| S2 | `.memory/adr/0011-discovery-track.md:5`, `.memory/grill/discovery-track/INDEX.md:5`, `.memory/specs/discovery-track.md:3`, `.memory/research-r32-fingerprinting.md:5`, `.memory/audit/claims.md:3` | Glob/bare mentions of moved files the map can't reach: `.memory/research-discovery-*.md` → `docs/agents/research/discovery-*.md`; sibling names `research-r32-*.md (siblings in .memory/)` → `r32-*.md (siblings in docs/agents/research/)`; "validated in .memory" → "validated in `docs/agents/`". | relocation.md step 4 (convention mention reworded) |
| S3 | `skills/archwright-derive/SKILL.md:36` | Archwright-self pointer "`.memory/reflections/global.md` in the archwright repo" goes stale on the move. → `docs/agents/reflections/global.md`. Line 37 (target project) stays. | link resolution where installed |
| S4 | `.memory/adr/.gitkeep` | Moves into `docs/adr/` beside 13 ADRs; drop it. | relocation.md step 5 |
| S5 | `.gitignore:5`, `.references/` | Plain `.references/` line; no README. One entry: `alloy6.jar` (no `.git`). → `.references/*` + `!.references/README.md`, README with `mise run rehydrate-alloy`. | repo-hygiene.md § .references |
| S6 | root | No `CLAUDE.md` pointer. | init-project plumbing |
| S7 | `AGENTS.md:85-92,206,228,236,257-261,302-304` | Layout tree, workflow, tickets, constraint and customization lines cite `.memory/` paths. Handled by the reshape (AGENTS.proposed.md). | relocation |

### Needs-judgment

| id | Finding | Rule / evidence |
|---|---|---|
| J1 | **Shipped steering self-references archwright's old `.memory/`.** `steering/archwright-conventions.md:33` (`.memory/audit/pipeline-dryrun.md`), `:92` (`.memory/research-*.md`), `:183` (`.memory/reflections/global.md` "in the archwright repo") go stale after the move. Adoption doesn't edit steering. The file is live global steering via symlink. Suggested: repoint to `docs/agents/audit/`, `docs/agents/research/`, `docs/agents/reflections/global.md` (match S3). | relocation.md step 4; adopt brief (no steering edits) |
| J2 | **Shipped skills assume the crew-research target layout.** survey:77-81,134; audit:45,168; forces:161,168; tensions:66; derive:37; steering:58,184 read/write a target's `.memory/{CONTEXT.md,adr,specs,grills,archwright-*.yaml,reflections}`. Targets adopted into grey-matter now have `GLOSSARY.md`, `docs/adr/`, `docs/agents/{specs,grill}/`. Survey will miss those sources and forces/tensions will write scratch into a `.memory/` that no longer exists. Decide: read both layouts, or switch the default. | adopt-project SKILL.md § "Breaking what the repo ships" |
| J3 | **Shipped artifacts lean on retired crew-research skills/steering.** `skills/archwright-resolve/SKILL.md:77` (source-authority), `:162` (spec-driven-development, retired → wayfinder/to-spec), `skills/archwright-{audit:171,forces:234,survey:102}` (`subagent-reliability` steering). `steering/subagent-reliability.md` ships a drifted copy of crew-research's skill (not byte-identical: crew's adds frontmatter + 2 failure modes); `~/.kiro/steering/subagent-reliability.md` is currently a plain file (not this repo's symlink). Decide who owns it, and what the skills cite. | brief retirement map; writing-for-agents |
| J4 | **Two glossaries.** `.memory/CONTEXT.md` → `GLOSSARY.md` (49 terms, agent glossary) and `docs/glossary.md` (shipped, deployed into survey references). About 18 terms appear in both; consistent today (glossary-verdicts) but drift-prone, and "glossary" is ambiguous. Decide: one source and a generated/derived other, or a stated split. | domain-modeling (one vocabulary); doc-conventions |
| J5 | **Tracker coupled to crew-research.** AGENTS.md §Tickets names crew-research `.memory/specs/ticket-cli-spec.md` as authority and installs tkt from `~/code/crew-research/tools/tkt`; `mise.toml:45-50` `validate:tickets` falls back to `PYTHONPATH=$HOME/code/crew-research/tools/tkt`. tkt is now the cargo build (`~/.cargo/bin/tkt`). 68 done tickets lack a `## Resolution` section (all 68 `tkt validate` warnings; most predate `require_resolution`). PLAN.md is the declared status narrative; `tkt sync-plan` is not wired. Decide: drop the crew fallback, backfill resolutions, and whether PLAN.md stays authoritative. | tkt conventions; AGENTS.md:226-246 |
| J6 | **Sanitization map lived in recall (retired) and the tree already fails the check.** AGENTS.md:264 and `mise.toml:170` say the real↔alias map is "held in recall". `mise run sanitize-check` (machine-local denylist) FAILs at baseline: 53 match lines in 14 files (12 tickets 051-076, `steering/archwright-conventions.md`, `tools/report/derive.py`). Names not reproduced here. Decide the map's new home and whether to alias the hits (history purge is the owner's call). | repo-hygiene.md § Sensitive; retirement map (recall → drop) |
| J7 | **Hygiene and stale pointers.** `docs/presentation/Archwright_Brief.pptx` (822 KB) tracked without LFS (no `.gitattributes`). Pre-existing broken links: `skills/archwright-check/SKILL.md:33` → `../archwright-resolve/references/pass-up.md` (no such file anywhere), `.memory/PLAN.md:208` → never-committed `next-work-proposals.md`. `audit-plan.md` (57 KB, CLOSED 2026-07-18) sits at the root. AGENTS.md layout tree and skill/tool lists duplicate `ls skills/` and each SKILL.md (cut to pointers in the proposal). | repo-hygiene.md § LFS; check-docs-consistency (links); writing-for-agents |

## Step 2: glossary verdicts (`.memory/CONTEXT.md` → `GLOSSARY.md`)

All 49 terms **confirmed** against code/docs; 0 stale, 0 contradicted (full table:
`glossary-verdicts.md`, one evidence line per term, e.g. Fingerprint aw/v1 →
`tools/check/common.py:12,142`; Gated → `tools/archwright-validate.py:177`; Posture →
`tools/report/derive.py:319-326`). The header is crew-style (`# Project Glossary`): retitle.

### Contradictions recorded as characterized fact

- C1: none between glossary and code. The one structural fact: two glossaries overlap (J4).
- C2: `GLOSSARY.md:114` (Force file) cites the target-project working inventory
  `.memory/archwright-forces-*.yaml`; that's the shipped skills' target convention (J2), not an
  archwright path. Left as-is.

## Migration-finding tickets

1. **Review migration finding: shipped steering self-references the old .memory/ layout**
   Covers J1. `steering/archwright-conventions.md:33,92,183` cite archwright's own `.memory/`
   paths, now `docs/agents/{audit,research,reflections}/`. Adoption doesn't edit steering, and the
   file is live global steering by symlink. Suggested: repoint the three lines, matching the
   derive skill fix (S3). First AC: review.
2. **Review migration finding: shipped skills assume the crew-research target-project layout**
   Covers J2. survey/audit/forces/tensions/derive and steering:58,184 read and write a target's
   `.memory/`. Grey-matter-adopted targets now use `GLOSSARY.md`, `docs/adr/`, `docs/agents/`.
   Decide whether the skills read both layouts, switch the default, or stay crew-shaped. Verify
   with a survey dry run on an adopted target.
3. **Review migration finding: shipped skills cite retired crew-research skills and a drifted subagent-reliability copy**
   Covers J3. resolve:77,162; audit:171, forces:234, survey:102. `steering/subagent-reliability.md`
   is an older copy of crew-research's. Decide the owner (archwright, grey-matter, or drop it from
   deploy) and what each skill cites instead.
4. **Review migration finding: two glossaries (GLOSSARY.md vs shipped docs/glossary.md)**
   Covers J4, C1. 49-term agent glossary and the deployed `docs/glossary.md` overlap on ~18
   terms. Decide one source of truth and how the other is derived, or record the split.
5. **Review migration finding: ticket tooling still points at crew-research**
   Covers J5. AGENTS.md §Tickets authority + install path and `mise.toml` `validate:tickets`
   fallback point at crew-research. 68 done tickets lack a Resolution section. Decide on dropping the
   fallback, backfilling resolutions, and the PLAN.md/ticket seam.
6. **Review migration finding: sanitization map home and pre-existing denylist hits**
   Covers J6. The alias map was "held in recall" (retired). `sanitize-check` already fails: 53
   lines in 14 files. Decide the map's home and whether to alias the hits; any history purge is
   the owner's call.
7. **Review migration finding: binary deck, broken links, and root-level closed plan**
   Covers J7. pptx without LFS; two pre-existing broken links (check→pass-up.md, PLAN→
   next-work-proposals.md); `audit-plan.md` at the root. Decide LFS, link repairs, and whether
   `audit-plan.md` moves under `docs/agents/`.

## Baseline

Run at `ea37928` (after `mise run setup` installed pyyaml + hypothesis into the gitignored
`.venv`; without them 2/165 ran):
- **Tests:** `mise run test` → `=== Results: 165 passed, 0 failed, 0 skipped ===` (run).
- **Design links:** `mise exec -- python tools/archwright-validate.py --links design/` → `PASS: all links resolve` (run).
- **Link check:** `relocate-knowledge.mjs check-links .` → 347 md files, **2 broken**
  (`.memory/PLAN.md:208`, `skills/archwright-check/SKILL.md:33`; both J7). Clone post-apply: 347
  files, same 2 broken (run).
- **Tickets:** `tkt validate --brief` → `pass (68 finding(s))`, all warnings (run).
- **Sanitize:** `mise run sanitize-check` → FAIL, 53 lines / 14 files (pre-existing, J6) (run).

## Hygiene

- **H1, tracked binaries not in LFS:** `docs/presentation/Archwright_Brief.pptx` (822 KB). `.git`
  is 8.7 MB. `tools/report/vendor/elk.bundled.min.js` reads as binary to `file` but is minified
  text (leave).
- **H2, sensitive:** no credentials/keys (grep AKIA/secret/password hits are rule text). Real
  target-project names: see J6 (denylist hits, not reproduced).
- **H3, `.references/`:** one entry, `alloy6.jar` (no `.git`): local-only, rehydrate with
  `mise run rehydrate-alloy` (`tools/install-alloy.py`, pinned URL + SHA-256 in
  `tools/alloy-runtime.json`).
- **H4, project copies of crew-research skills:** none in `.kiro/skills` (only `repo-maintenance`,
  project-unique) or `.agents/skills` (absent). Shipped `steering/subagent-reliability.md`
  overlaps crew's skill but is shipped and drifted (J3).

## Leftovers after the dry-run (20) and the hand-fix per line

| Leftover | Action |
|---|---|
| `GLOSSARY.md:114` `.memory/archwright-forces-*.yaml` | leave: target-project convention (C2/J2) |
| `docs/agents/PLAN.md:208` `../../.memory/next-work-proposals.md` | leave: pre-existing broken (J7) |
| `docs/adr/0011-discovery-track.md:5`, `docs/agents/grill/discovery-track/INDEX.md:5`, `docs/agents/specs/discovery-track.md:3` | fix S2 |
| `docs/agents/research/r32-fingerprinting.md:5`, `docs/agents/audit/claims.md:3` | fix S2 |
| `docs/agents/audit/pipeline-dryrun.md:9` (`.memory/grills` target sources) | leave: target-project convention |
| `docs/agents/lessons/README.md:36` (DemoAR `.memory/`) | leave: field target |
| `.tickets/009:56`, `.tickets/010:36,50`, `.tickets/036:10,45` | leave: dated provenance (files gone or historical) |
| `AGENTS.md:85` | reshape (S7) |
| `audit-plan.md:160,244,268,274` | leave: dated provenance / target-project / cross-repo |
| `docs/open-questions.md:147` `.memory/review-history/` | leave: proposed mechanism for targets |
| Evidence-protected (6 files: skills audit/derive/forces/survey/tensions, steering) | S3 for derive:36; rest J1/J2 |
| Wrongly rewritten (not leftovers) | S1 restores `.tickets/034:33`, `docs/agents/PLAN.md:318` |
