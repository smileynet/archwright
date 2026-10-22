# SARIF 2.1.0 partialFingerprints & Alert Deduplication (incl. GitHub Code Scanning)

Researched: 2026-07-18 (session: sarif-fingerprints)

## Summary

SARIF 2.1.0 defines `result.partialFingerprints` as a property bag of strings that *contribute to* (but do not by themselves constitute) a stable identity for a result; a result management system combines them with other data (tool name, rule id, file path) into a full fingerprint used to group "logically identical" results across runs. GitHub Code Scanning uses exactly one partial fingerprint key, `primaryLocationLineHash` — a 64-bit rolling hash of the first 100 non-whitespace characters starting at the result's primary line, plus an occurrence counter — which is line-number-independent and therefore tolerant of code shifting up or down in the file. If a fingerprint is absent, the `upload-sarif` GitHub Action computes it server-side-of-the-action from the checked-out source (via `fingerprints.ts`); uploads through the raw REST API without fingerprints produce duplicate alerts.

## Details

### The spec model (OASIS SARIF 2.1.0)

- **`fingerprints` (§3.27.16)** vs **`partialFingerprints` (§3.27.17)**: `fingerprints` holds *complete* stable identifiers, intended to be populated by a result management system when it ingests the file (direct producers SHOULD NOT populate it). `partialFingerprints` holds *contributing* strings that producers MAY emit; the result management system SHOULD incorporate them into its own fingerprint computation, using any combining algorithm (all-match, any-match, majority — spec leaves it open).
- **What goes in a partial fingerprint**: information a result management system could not deduce itself — e.g., a prohibited word for a doc checker (spec's example: `"wordPlusLangHash": "2c26b46b…"`). Producers SHOULD NOT include information deducible from the SARIF file itself (like file hashes).
- **What must NOT be hashed (Appendix B, normative)**: absolute line numbers (or absolute byte offsets) — inserting lines above a result would change the fingerprint and cause the result to be misreported as "new". Recommended fingerprint inputs for a result management system: tool name, rule id, file path, plus partialFingerprints. Logical locations (`fullyQualifiedName`) are called out as especially fingerprint-friendly because they're more resilient to edits than line numbers (§3.28.1).
- **Related identity mechanisms**: `correlationGuid` (§3.27.4) is the opaque-equivalence-class alternative to fingerprints; `baselineState` (§3.27.24: new/unchanged/updated/absent) is what fingerprint matching ultimately drives.

### Versioned fingerprint keys (§3.5.4.2 + §3.27.17)

- Property names in both `fingerprints` and `partialFingerprints` are **versioned hierarchical strings**: forward-slash-separated components where a final component matching `v<non-negative-integer>` is a version, e.g. `prohibitedWordHash/v2`.
- A name **without** a version component is considered *older* than any versioned form of the same name.
- Comparison rule: when two results both carry multiple versions of the same key, the consumer SHOULD compare using the **latest version present in both** (greatest common version). Example from spec: result A has v1+v2, result B has v2+v3 → compare on v2.
- Producer guidelines: use meaningful documented names; a *changed algorithm gets a new name/version*; avoid removing existing keys (consumers may depend on them).
- Note: the `:1` suffix in GitHub's `primaryLocationLineHash` value (`"39fa2ee980eb94b0:1"`) is **not** a spec version — it's an occurrence counter (see below). GitHub's key itself is unversioned.

### GitHub Code Scanning's implementation

- **Only `primaryLocationLineHash` is used** — GitHub docs state: "Code scanning only uses the `primaryLocationLineHash`." CodeQL also emits `primaryLocationStartColumnFingerprint`, but GitHub ignores it for matching.
- **Matching preconditions**: `ruleId` must be stable across analyses, and **file paths must be consistent** across runs — a path change closes the old alert and opens a "new" one (duplicate).
- **Fallback behavior**: SARIF from CodeQL includes fingerprints. Third-party SARIF uploaded via the `upload-sarif` action gets `partialFingerprints` computed automatically from the checked-out source files. SARIF uploaded via the `/code-scanning/sarifs` REST endpoint without fingerprints is accepted but **users may see duplicate alerts** — GitHub recommends computing them yourself, pointing at `github/codeql-action/src/fingerprints.ts` as a reference implementation.

### The primaryLocationLineHash algorithm (from fingerprints.ts, verified against source)

Exact mechanics of the codeql-action implementation:

1. **Normalization**: line endings `\r`, `\r\n` → `\n`; **spaces and tabs are skipped entirely** (so re-indentation doesn't change the hash).
2. **Rolling polynomial hash** (Rabin–Karp style): 64-bit arithmetic (`Long`), multiplier `MOD = 37`, window `BLOCK_SIZE = 100` characters. For each position: `hash = 37·hash + incoming_char − 37^100·outgoing_char` (wrapping 64-bit).
3. **Per-line hash**: for every line, the hash covers the first **100 non-space/tab characters counted from the start of that line** — which means the window **crosses line boundaries** into following lines for short lines. An EOF sentinel (−1) plus `\0` padding ensures lines near end-of-file still get a full 100-char window.
4. **Output format**: lowercase unsigned hex of the 64-bit hash, suffixed with an **occurrence counter**: `"<hex>:<n>"` where n counts how many times this exact hash value has been seen so far in the file (1-based). This disambiguates identical lines-in-context (e.g., two identical `return null;` blocks) — the 1st gets `:1`, the 2nd `:2`.
5. **Anchoring**: only `locations[0].physicalLocation.region.startLine` is used (primary location). If the region is absent (whole-file alert), line 1's hash is used. If a result already carries a `primaryLocationLineHash` that disagrees with the computed one, the existing value is kept and a warning logged.
6. **Skip conditions**: no fingerprint is computed when the URI scheme isn't file/relative, the path is outside the source root, the file doesn't exist at analysis time, or the location has no startLine.

### How line-shift tolerance works

The hash input is **content-only** (100 significant chars starting at the line) — the line *number* never enters the hash. Consequences:

- **Tolerant of**: inserting/deleting lines elsewhere in the file (above or below), whitespace/indentation changes, CRLF↔LF changes. The alert re-matches at its new line number because the hash travels with the content.
- **Not tolerant of**: any edit within the ~100 significant characters starting at the alert line — including edits to *subsequent* lines that fall inside the window (a change 2 lines below a short alert line changes its hash). Also not tolerant of: renaming/moving the file (path is a separate matching input), duplicating-then-editing so occurrence counts shift (the `:n` suffix reorders), or rule id changes.
- This is a deliberate trade-off: cheap, deterministic, and resilient to the most common churn (line shifts), at the cost of treating nearby-content edits as a close+open (new alert) rather than an update.

## Sources

- [L2:verified] OASIS SARIF 2.1.0 spec (§3.5.4.2 versioned hierarchical strings, §3.27.2 logically identical results, §3.27.16 fingerprints, §3.27.17 partialFingerprints, Appendix B normative fingerprint guidance) — https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html (OASIS Standard, 2020-03-27; read directly)
- [L1:verified] `github/codeql-action` fingerprints implementation (rolling hash, BLOCK_SIZE=100, MOD=37, occurrence counter, EOF padding, callback anchoring) — https://github.com/github/codeql-action/blob/main/src/fingerprints.ts (read full source, main branch as of 2026-07-18)
- [L4:verified] GitHub Docs, "SARIF support for code scanning" — fingerprint generation section ("Code scanning only uses the primaryLocationLineHash"; consistent-filepath requirement; upload-sarif auto-computes; API uploads may duplicate) — https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning (read directly)
- [L5:reported] GitHub codeql discussion #5982 "Can anyone tell how primaryLocationLineHash be generated?" — confirms it's an opaque hash for logical-identity matching — https://github.com/github/codeql/discussions/5982 (search snippet only)

## Open Questions

- **Server-side matching internals**: GitHub's docs describe *inputs* (ruleId + path + primaryLocationLineHash) but not the exact server-side matching/merge algorithm (e.g., whether a secondary heuristic rescues alerts when the hash changes but line/rule/path match). Not publicly documented.
- **Occurrence-counter fragility**: when a duplicated code block is edited so that occurrence order changes (`:1`/`:2` swap), does GitHub close-and-reopen both alerts? Behavior is implied by the format but not documented.
- **Why 37 / 100**: no published rationale for the multiplier or block size; presumably empirical (collision rate vs. edit-window sensitivity). Commit history (e.g. c0950054 "Some refactoring in fingerprint computation") might explain but wasn't examined.
- **Cross-branch matching**: docs say fingerprints match "across commits and branches" for the selected branch's latest run; interaction with `automationDetails.id` categories and multi-config uploads (same result from two analysis categories) not fully specified.
- **Versioned keys in practice**: GitHub's `primaryLocationLineHash` carries no `/vN` suffix — if GitHub ever changed the hash algorithm, the spec-correct move would be `primaryLocationLineHash/v2`; no evidence they've committed to that path.
