# R32 — Violation Fingerprinting Strategy (Research Synthesis)

**Date:** 2026-07-18 · **Unblocks:** CK-07 (baseline file), CK-16 (SARIF dedup), ADR 0009 (evidence ledger — shared fingerprint plumbing)
**Question:** How should violations be fingerprinted for stable dedup across runs? (file+line is fragile; content hash?)
**Sources studied:** SARIF 2.1.0 spec + GitHub `fingerprints.ts` [L1/L2:verified], semgrep `rule_match.py` + `run_scan.py` [L1:verified], ArchUnit FreezingArchRule user guide + issues [L2/L3:verified]. Full per-source detail: `research-r32-sarif-fingerprints.md`, `research-r32-semgrep-fingerprint.md`, `research-r32-archunit-freezing.md` (siblings in `.memory/`).

## Convergent findings (all three tools agree)

1. **Never hash line numbers.** Normative in SARIF Appendix B (inserting lines above a result must not change its identity); semgrep hashes code text, never positions; ArchUnit's default matcher explicitly ignores line numbers and anonymous-class/lambda indices. Line numbers are display metadata, not identity.
2. **Identity = rule id + path + normalized matched content.** All three converge on this triple. Normalization: strip/skip whitespace (GitHub skips spaces+tabs entirely; semgrep dedents + strips + removes `nosemgrep` comments), so re-indentation never churns identity.
3. **Occurrence index for identical duplicates, appended visibly — not hashed in.** Two identical `return null;` matches in one file need distinct identities: GitHub suffixes `:<n>`, semgrep suffixes `_<n>` *after* hashing so siblings are recognizable (`abc_0`/`abc_1`). Deleting an earlier duplicate shifts later indices — accepted limitation in both.
4. **Ratchet asymmetry.** ArchUnit: fixed violations auto-removed from the store (`allowStoreUpdate` is reduction-only, maintainer-confirmed); new violations always fail and are NEVER auto-added; `refreeze=true` is the explicit one-shot escape hatch. This independently validates CK-08's design as written ("never add automatically; count can only decrease").
5. **Version the fingerprint algorithm.** SARIF names are versioned hierarchical strings (`key/v2`); consumers compare on the greatest common version; a changed algorithm gets a new version, never a silent change. Semgrep ships `matchBasedId/v1`. Semgrep's own comment on MurmurHash3: "we need to keep consistent hashes so we cannot change this easily" — pick the algorithm deliberately, version it from day one.
6. **CI guard rails.** ArchUnit defaults `allowStoreCreation=false` so a misconfigured CI can't silently create a fresh (empty-debt) store and pass; semgrep suppresses findings when the baseline scan *failed* ("cannot prove new" ≠ new).

## Divergences worth knowing

| Aspect | GitHub/SARIF | semgrep | ArchUnit |
|---|---|---|---|
| Content window | first 100 non-ws chars from alert line (crosses line boundaries — edits *below* a short line churn it) | exact matched lines, normalized | whole violation message, volatile tokens stripped |
| Rename handling | path change = close+reopen (new alert) | git rename-dict substituted before compare | message-based; class rename = new violation |
| Edit tolerance | any edit in window = new | two tiers: syntactic (exact text) vs match_based (pattern+metavars — survives edits that keep bindings) | any non-volatile detail change = new |
| Store | server-side | none (re-scans baseline commit in a worktree) | plain-text VCS-committed file, one violation per line |

Semgrep's two-tier design (a strict syntactic id AND a looser semantic id, plus decomposed `code_hash`/`pattern_hash`/`line_hash` so the platform can classify *what changed*) is the most sophisticated; ArchUnit's committed-text-file store is the closest shape to CK-07's `.archwright-baseline.json`.

## Recommendation: `aw/v1` fingerprint

```
fingerprint = sha256(spec_id ⊕ invariant ⊕ norm_path ⊕ norm_evidence)[:16] + "_" + occurrence_index
```

- **Inputs, joined with `\x00` separators** (unambiguous, no delimiter collisions):
  - `spec_id` — the rule identity (semgrep/SARIF: rule id is always an identity input).
  - `invariant` — archwright's sub-rule granularity (one spec can host several invariants).
  - `norm_path` — evidence file path relative to project root, `/`-separators. Renames = new violation in v1 (GitHub's position; semgrep's rename-dict is a v2 candidate — noted as limitation, not built: rule-of-two).
  - `norm_evidence` — the matched content with the `file:line:` prefix REMOVED and whitespace collapsed (strip ends, collapse internal runs to one space). Never the line number. For static/grep checks this is the matched line text. For behavior/trace violations: `event` name only (no position, no state dump — both are run-volatile).
- **sha256** — stdlib, FIPS-safe (semgrep's own FIPS fallback IS sha256), no new dependency. Truncate to 16 hex chars (64 bits — same width GitHub uses; collision space is per-project, tiny).
- **Occurrence index appended after hashing** (semgrep convention): the Nth identical (spec, invariant, path, content) tuple gets `_<n>`, 0-based. Siblings stay visible in the ledger.
- **Version tag stored alongside, not inside**: baseline/ledger entries carry `"algo": "aw/v1"`. Algorithm changes bump to `aw/v2`; a reader seeing an unknown version treats entries as unmatchable (stale), never guesses. When CK-16 lands, the same value exports as SARIF `partialFingerprints["awFingerprint/v1"]` — and `primaryLocationLineHash` should ALSO be emitted (compute or let `upload-sarif` compute) since GitHub matches only on its own key.

### Baseline entry shape (CK-07 input)

```json
{
  "fingerprint": "9f2a4c1e8b3d5a70_0",
  "algo": "aw/v1",
  "spec_id": "no-direct-db-access",
  "invariant": "no-direct-db-access",
  "path": "src/handlers/order.ts",
  "evidence": "import { db } from '../db'",
  "first_seen": "2026-07-18",
  "note": "pre-archwright debt, ticket BACKLOG-42"
}
```

Human-readable fields ride along for review/diff friendliness (ArchUnit's committed-text-store lesson: the baseline is a reviewed artifact, not an opaque cache). Matching uses ONLY `fingerprint`+`algo`.

### Behavior carried over from prior art

- **Ratchet (CK-08, validated):** `--update-baseline` removes entries whose fingerprints no longer reproduce; never adds. Adding an entry is a human edit (or an explicit future `--refreeze`-style flag, if ever — not in scope).
- **No silent store creation:** missing baseline file = no suppression (all violations report). A flag creating one from current state must be explicit and print what it froze.
- **Errored checks never update the baseline** (semgrep's "cannot prove new" guard): exit-2 runs are ineligible for `--update-baseline`.
- **Suppressed ≠ silent:** baselined violations surface as `severity: warning` with `"baselined": true` and keep their provenance — they are debt, not noise. `remaining_delta` = violations AFTER suppression (the CK-03 field finally earns its name).

### What the evidence ledger (ADR 0009) shares

The same `aw/v1` fingerprint keys recurrence: a FAIL event in `design/.archwright-evidence.json` carries the violation fingerprint, so "same violation recurring across N runs" vs "new violation" is mechanical. Pass-streak events key by `kind:id` + invariant (no evidence content exists on a pass — nothing to fingerprint; the spec identity suffices).

## Known limitations (accepted for v1)

1. **File renames churn fingerprints** — baselined debt in a renamed file resurfaces as new. Mitigation is manual (re-baseline after big moves) until a git-rename dict proves needed (rule-of-two).
2. **Duplicate-index shifts** — deleting the 1st of two identical matches renames `_1` → `_0`; the survivor reads as new. Both semgrep and GitHub accept this.
3. **Edit-adjacent churn** — any edit to the matched line itself is a new violation even if semantically identical (no metavariable-tier tolerance; archwright's grep patterns have no bindings to substitute). A semgrep-style two-tier id is the natural v2 if field friction shows up.

## Open questions (carried, non-blocking)

- ArchUnit's multiset question applies to us: N identical baselined entries should tolerate exactly N live occurrences — occurrence indexing handles this if `--update-baseline` recomputes indices atomically; verify in CK-07 tests.
- Whether trace violations should be baselineable at all (they're deterministic design violations — candidate policy: baseline applies to static mode only; trace/behavior FAILs always report). Decide at CK-07 pickup — HITL, since it touches what ★★ escalation can be suppressed by a baseline entry. **Recommended default: baseline suppresses severity/escalation ONLY for ★ and — violations; a baselined ★★ still escalates** (a baseline entry must not be a back door around C2).
