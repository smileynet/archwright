# R32 — ArchUnit FreezingArchRule: storing and matching known violations across runs

## Summary

ArchUnit's `FreezingArchRule` wraps any `ArchRule` and, on first run, records all current violations to a `ViolationStore` (by default a plain-text, VCS-committable file store). On subsequent runs only *new* violations fail the build; known violations are matched against the store using a `ViolationLineMatcher` that deliberately ignores line numbers (and anonymous-class/lambda indices), so code drift doesn't cause false "new violation" reports. The store is a one-way ratchet by default: fixed violations are automatically removed from the store (preventing reintroduction), while new violations are rejected and never auto-added.

## Details

### What's stored

- Default store: `TextFileBasedViolationStore` — plain text files in a directory (configurable via `archunit.properties`: `freeze.store.default.path=/some/path/in/a/vcs/repo`). Intended to be committed to version control so progress is tracked over time. [L2:verified — official user guide §8.6.2]
- Layout: a `stored.rules` index file mapping each frozen rule's full description text to a per-rule violations file (UUID-named); each per-rule file contains one violation message per line — the same human-readable failure lines ArchUnit reports (e.g. `Method <a.b.SomeService.callController()> calls method <a.b.SomeController.execute()> in (SomeService.java:14)`). [L3:reported — GitHub issue #510 references "the stored.rules entry and the corresponding violation file"; L6:inferred from issue #1057 which discusses `TextFileBasedViolationStore#write` joining violations with `\n`]
- The store is keyed by the rule's *description text* — renaming/rephrasing a rule effectively orphans its stored violations (a known operational footgun; `freeze.refreeze=true` exists partly for "the format of some violations has changed"). [L2:verified — user guide]
- The `ViolationStore` is an extension point: implement `com.tngtech.archunit.library.freeze.ViolationStore` and plug in via `FreezingArchRule.freeze(rule).persistIn(customStore)` or `freeze.store=fqcn` property (e.g. community XML-based store for merge-friendlier diffs). [L2:verified — user guide §8.6.3; L6 — stefanroeck gist]

### How violations are matched despite line-number drift

- Matching is textual, per violation line, mediated by the `ViolationLineMatcher` extension point. [L2:verified]
- Default matcher: "ignores line numbers and numbers of anonymous classes or lambda expressions, and counts lines as equivalent when all other details match." So `(SomeService.java:14)` vs `(SomeService.java:87)` is the SAME known violation as long as the class, members, and violation description are otherwise identical; likewise `Foo$1` vs `Foo$2` and lambda indices are normalized. [L2:verified — user guide §8.6.3 "Violation Line Matcher"]
- Consequence: violations shifted by refactoring (adding imports, reordering methods) do NOT resurface as new. But a rename of the class or method, or any change in the violation's other details, breaks the match and the violation is reported as new.
- Custom matchers: `FreezingArchRule.freeze(rule).associateViolationLinesVia(customLineMatcher)` or `freeze.lineMatcher=fqcn`. [L2:verified]

### Ratchet behavior

- **Solved violations are removed automatically.** If a run finds fewer violations than stored, `FreezingArchRule` updates the store to the reduced set (default `freeze.store.default.allowStoreUpdate=true`). Maintainer confirmation: allowStoreUpdate "only allows ArchUnit to automatically reduce the violation store if violations are fixed... so they can't be reintroduced 2 weeks later." [L3:verified — TNG/ArchUnit issue #510 maintainer response] There's even a Stack Overflow question asking how to *stop* this auto-reduction (answer: set `allowStoreUpdate=false`). [L6]
- **New violations are rejected, never silently absorbed.** `allowStoreUpdate=true` does NOT add new violations to the store — the check fails. To consciously accept new violations you either delete the rule's store entries (loses history) or set `freeze.refreeze=true` for one run, which rewrites the store with the current state and reports success. [L2:verified — user guide; L3 — issue #510]
- **CI guard rails:** `freeze.store.default.allowStoreCreation=false` (the default) prevents a misconfigured CI environment from silently creating a fresh store and passing; `allowStoreUpdate=false` prevents CI from mutating the store at all (issue #211 documents the CI-silently-updates-store hazard). All properties overridable as `-Darchunit.…` system properties. [L2:verified]

### Relevance to archwright

This is the same shape as a "known-violations baseline" for archwright checks: (1) store violation *messages* not positions, (2) match with a normalizer that strips volatile details (line numbers, synthetic indices), (3) ratchet asymmetry — auto-shrink on fixes, hard-fail on additions, explicit one-shot "refreeze" escape hatch, (4) creation/update permission flags to keep CI honest.

## Sources

- [L2:verified] ArchUnit User Guide §8.6 "Freezing Arch Rules" — https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules (read 2026-07-18; store config, refreeze, ViolationStore + ViolationLineMatcher extension points, default matcher semantics)
- [L3:verified] TNG/ArchUnit issue #510 "Frozen rules not updated when new violation occurs" — https://github.com/TNG/ArchUnit/issues/510 (allowStoreUpdate semantics: reduction-only; stored.rules + per-rule violation file layout)
- [L3:reported] TNG/ArchUnit issue #211 "Enhance Freezing for CI executions" — https://github.com/TNG/ArchUnit/issues/211 (CI silently updating store hazard → allowStoreCreation/allowStoreUpdate flags)
- [L3:reported] TNG/ArchUnit issue #1057 "FreezingArchRule generates file missing newline" — https://github.com/TNG/ArchUnit/issues/1057 (confirms TextFileBasedViolationStore writes one violation per line)
- [L6:reported] Stack Overflow: "If violations are fixed, FreezingArchRule automatically reduce the stored violations… any way to stop this?" — https://stackoverflow.com/questions/77046215/ (confirms auto-reduction default; allowStoreUpdate=false disables)
- [L6:reported] stefanroeck gist: XML-based VCS-friendly ViolationStore — https://gist.github.com/stefanroeck/0e7b2002eb0e801b8ff619e6738048db (evidence the text store's diff/merge behavior motivates custom stores)

## Open Questions

- Exact `stored.rules` file syntax (properties-style rule-description→UUID mapping?) — inferred from issues, not read from source. Reading `TextFileBasedViolationStore.java` would confirm.
- How the default `ViolationLineMatcher` tokenizes a violation line (regex over `(File.java:NN)` and `$<digits>`?) — semantics are documented but the normalization algorithm isn't; source read needed for a faithful reimplementation.
- Behavior when two *identical* violation lines exist (duplicate messages after line-number stripping) — is matching multiset-aware (N stored allows N actual) or set-based?
- Interaction with `archunit_ignore_patterns.txt`: issue #915 asks that ignored violations not enter the store — resolution status unverified.
