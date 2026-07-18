# R32: Semgrep Finding Fingerprints — baseline/dedup mechanics

Researched: 2026-07-18. Sources: semgrep docs + `semgrep/semgrep` source (develop branch, verified directly).

## Summary

Semgrep tracks finding identity with two fingerprints: `syntactic_id` (MurmurHash3 of rule id + path + matched-code-text + occurrence index) and `match_based_id` (blake2b of rule id + path + rule pattern with metavariable values substituted, plus an appended occurrence index — this is the `fingerprint` field in JSON output and `matchBasedId/v1` in SARIF). `--baseline-commit` does **not** compare fingerprints against a stored baseline file — it re-scans the baseline commit in a git worktree (only files that had head matches, only rules that matched) and drops head findings whose `ci_unique_key` (rule, path, matched code text, index) also appears in the baseline scan, with explicit rename mapping so renamed files don't resurface as new findings.

## Details

### The identity keys (verified in `cli/src/semgrep/rule_match.py`)

**`syntactic_context`** — the normalized matched code: the matched lines with any inline `nosemgrep` comment stripped from the first line, `textwrap.dedent`-ed, and whitespace-stripped. This is the "code content" input; it deliberately ignores indentation changes and nosem-comment additions.

**`ci_unique_key`** = `(rule_id, path-relative-to-cwd, syntactic_context, index)`
- `index` = how many *prior* matches in the same file had the identical (rule, path, code) triple — i.e., occurrence counter among exact duplicates, assigned in `RuleMatches.add()`. It exists so duplicated code still produces distinct findings.

**`syntactic_id`** = `hash128(str(ci_unique_key))` — 128-bit MurmurHash3, hex-encoded (32 chars). Source comment: "no good reason for us to use MurmurHash3 here, but we need to keep consistent hashes so we cannot change this easily." Sent to semgrep.dev; docs say it's now "primarily used by Semgrep for internal debugging."

**`match_based_key`** = `(rule-formula-string with metavariable values substituted in, path, rule_id)`
- The formula string is the rule's pattern; metavariable bindings (e.g. `$X` → `"foo"`) are substituted, with keys sorted longest-first to avoid prefix-collision substitutions.

**`match_based_id`** = `blake2b(str(match_based_key)).hexdigest() + "_" + match_based_index` (sha256 instead of blake2b in FIPS mode). Note the index is **appended after** hashing, not hashed in — deliberately, so `abc_0` and `abc_1` are visibly siblings (same rule + same abstract pattern + same file). `match_based_index` is a separate occurrence counter keyed by match_based_key (kept separate from `index` because the two keys have different collision behavior).

This is the primary dedup identity: docs state Semgrep Platform uses `match_based_id` to correlate the same finding across scans and branches (a triage action on one branch carries to another). DefectDojo and other integrators also dedup on it.

### The `fingerprint` output field

- JSON output `extra.fingerprint` = the `match_based_id`. Per the JSON/SARIF fields doc, it's populated only when logged in to Semgrep AppSec Platform (CE column: ❌); logged-out output shows a redacted placeholder.
- SARIF output: `results[].fingerprints["matchBasedId/v1"]` — same value.
- Additional hashes collected alongside (source): `code_hash` (sha256 of syntactic_context only), `pattern_hash` (sha256 of substituted formula only), `start_line_hash`/`end_line_hash`. These decompose the identity so the platform can tell *what kind* of change happened (file moved → path changed but code_hash same; moved within file → index changed; edited → code_hash changed).

### `--baseline-commit` behavior (verified in `cli/src/semgrep/run_scan.py`, `baseline_run` + `remove_matches_in_baseline`)

1. Scan HEAD (diff-aware target selection when a baseline handler exists).
2. Compute baseline targets: only the files that had head matches, **plus** the old paths of renamed files, **minus** files added since baseline (they don't exist there). Only the rules that produced head matches are run.
3. Check out the baseline commit into a **git worktree** (`baseline_handler.baseline_context()`) and run that reduced scan.
4. Remove head matches whose `get_path_changed_ci_unique_key(renames)` appears in the baseline match set for the same rule. The rename dict (new path → old path, from git status) is substituted into the key before comparison — this is how renames are prevented from creating spurious "new" findings.
5. Reliability guard: if the baseline scan *failed* on a file (engine error, timeout), head findings there are **suppressed** rather than reported as new — file-wide when the error has no rule id, rule-scoped when it does ("cannot prove new").

So baseline comparison uses the **syntactic** key (exact normalized code text), not `match_based_id`. Consequences:
- **Rename, no edit** → not new (rename dict maps the path).
- **Move within file, no edit** → not new (line numbers aren't in the key). Index only changes if the ordering among *identical duplicate* snippets changes.
- **Any textual edit to the matched lines** (beyond indentation/nosem-comment/trailing whitespace) → reported as new by `--baseline-commit`, even if `match_based_id` would have survived (match_based_id is more tolerant: edits that don't change the metavariable-substituted pattern — e.g. inserting unrelated lines between taint source and sink — keep the same match_based_id).
- **Rule renamed or rule pattern edited** → new finding under both schemes (rule id is in both keys; pattern text is in match_based_key).
- Docs carry an explicit caveat: "The calculations used to determine whether findings are new are subject to change at any time."

### Stability summary table

| Change | syntactic_id / baseline key | match_based_id (`fingerprint`) |
|---|---|---|
| Reindent / add `// nosemgrep` / trailing whitespace | stable | stable |
| Move match within file | stable | stable |
| Rename file | stable for `--baseline-commit` (rename dict); the raw hash itself changes (path is an input) | changes (path is hashed) — platform uses code_hash/pattern_hash to reconcile |
| Edit matched code, same abstracted pattern + metavariable values | **changes** | stable |
| Edit that changes metavariable values | changes | changes |
| Rule id rename or pattern edit | changes | changes |
| Nth duplicate of identical snippet added/removed above | index shifts for later duplicates | match_based_index shifts likewise |

## Sources

- [Remove duplicate findings (match_based_id / syntactic_id)](https://semgrep.dev/docs/semgrep-code/remove-duplicates) — semgrep.dev docs [L4:verified]
- [Findings in CI](https://semgrep.dev/docs/managing-findings/) — diff-aware scans report only findings new relative to baseline commit [L4:verified]
- [JSON and SARIF fields](https://semgrep.dev/docs/semgrep-appsec-platform/json-and-sarif) — `fingerprint` platform-only; SARIF `matchBasedId/v1` [L4:verified]
- [`cli/src/semgrep/rule_match.py`](https://github.com/semgrep/semgrep/blob/develop/cli/src/semgrep/rule_match.py) — hash inputs, MurmurHash3/blake2b, index handling [L1:verified, read directly]
- [`cli/src/semgrep/run_scan.py`](https://github.com/semgrep/semgrep/blob/develop/cli/src/semgrep/run_scan.py) — `baseline_run`, `remove_matches_in_baseline`, rename handling, failure suppression [L1:verified, read directly]
- [PR #7973: diff scans in dirty repos](https://github.com/returntocorp/semgrep/pull/7973) — `--baseline-commit` scans staged files in unclean trees; `ci --baseline-commit HEAD` pre-commit pattern [L3:reported]
- [CI environment variables](https://semgrep.dev/docs/semgrep-ci/ci-environment-variables/) — `SEMGREP_BASELINE_COMMIT` [L4:verified]
- [DefectDojo Semgrep Pro parser](https://docs.defectdojo.com/supported_tools/parsers/file/semgrep_pro/) — third parties dedup on match_based_id [L4:reported]

## Open Questions

- Exact conditions under which the CLI populates `extra.fingerprint` vs the redacted placeholder when logged out (docs table says platform-only; unverified whether CE ever emits a real value locally).
- Whether `match_based_index` reuses freed indices when an earlier duplicate is deleted (i.e., can a surviving finding's id shift from `_1` to `_0` and appear "new" on the platform). Source suggests yes (counter recomputed each scan); platform-side reconciliation unverified.
- Versioning: SARIF exposes `matchBasedId/v1` — no public evidence of a v2, but the docs' "subject to change at any time" caveat means pinning to the hash format is unsafe.
- `--baseline-commit` with `is_mergebase` (`baseline_commit_is_mergebase`) semantics — present in source, behavior relative to plain commit baseline not fully traced.
