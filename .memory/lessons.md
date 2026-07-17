# Lessons — archwright tooling

## 2026-07-16 — First full pipeline run on Windows (target: ExposeAR)

One-line: Windows portability bugs made the check phase silently lie; three tool fixes landed.

1. **`read_text()` without encoding** broke ★-confidence parsing (cp1252 default). Fixed in validate/check/compile-alloy — always pass `encoding="utf-8"`.
2. **check tool trusted missing binaries:** `grep` absent on the machine → command-mode checks returned empty stdout → false PASS on expect:absent. Fixed: pure-Python grep for target+pattern, Git-bash for command mode, rc>1/"not recognized" → status error. Rule: a check runner must fail loud when its own tooling is missing (`fail-loud-at-source` applies to the checker itself).
3. **`target_status: pending` (derive skill) was unimplemented in archwright-check.py** → 20+ pending specs reported as FAIL. Fixed: → SKIP. Keep skills and tools in lockstep; grep the tool for any field a skill mandates.
4. Full pipeline (survey→forces→tensions→resolve→formalize→model→contract→derive→check) validated end-to-end on a real brownfield Unity/MR project: 93 forces, 13 tensions, 13 patterns, 44 specs, all validate; check phase surfaced genuine violations once tooling was fixed. Pipeline artifacts live in ExposeAR `design/` + `.memory/`.
5. Enhancement candidates observed in the field: `include:` glob support for python-grep checks (tls-only matched 897 lines repo-wide; wants *.cs scoping); multi-target support (specs wrote space-separated targets, invalid today); windows.md steering should note the real python path pattern.
6. **Run the fixture suite after ANY check/validate change.** The python-grep rewrite initially emitted absolute Windows paths, silently breaking `only-in` substring filters (single-ball-writer fixture failed). Fixed: emit project-relative POSIX paths. `tools/run-fixture-tests.sh` caught it — 21 passed / 0 failed / 1 skipped (alloy) is the green baseline. On Windows, run it via Git bash with a `/tmp/pyshim/python3` shim, since `python3` resolves to the MS Store stub even inside bash.
7. **Concurrent sessions are real:** upstream main had 7 new commits mid-session (grill closeouts, C9 contract validation in archwright-validate.py). `git merge --no-commit --no-ff` first to test conflicts (was clean), then merge + push. Never assume sole ownership of main.


## 2026-07-17 — mise adoption for tool management

One-line: mise.toml now owns tools/env/tasks; one gotcha — mise's Windows python has no `python3`.

1. **`mise install && mise run setup && mise run rehydrate-alloy` is the full rehydration path** (AGENTS.md "Dependency Rehydration"). `[env]` sets `PYTHONIOENCODING=utf-8` + `ARCHWRIGHT_ALLOY_JAR` automatically in-repo — the manual env dance and `/tmp/pyshim` hack are obsolete.
2. **mise's Windows python ships only `python.exe`** — no `python3` binary or shim, so bare `python3` still hits the MS Store stub even under `mise run`. `run-fixture-tests.sh` defines a `python3()` → `python` fallback function; scripts calling `python3` need the same guard or must use `python`.
3. **`mise run test` green baseline** (behavior check active — jar + temurin-21 both mise-provisioned; verified 2026-07-17): 22/0/0, then 26/0/0 after the include-glob + comment-positional conformance fixtures landed later that day. Trust the docs (AGENTS.md/fixture README) for the current number.
4. `cargo:`-backend tools deliberately excluded from mise.toml (rust toolchain too heavy for optional merman-cli renderer).

## 2026-07-17 — include: globs + comment-stripping false-pass

One-line: comment *truncation* silently broke any pattern containing the comment token itself.

1. **`check.include:` globs landed** (ticket 005): bare glob matches file name, glob with `/` matches project-relative path; declarative target+pattern checks only (loud error with `command:`); explicitly-named single-file targets are never filtered (the GNU grep `--include` gotcha, avoided by design). ExposeAR `tls-only` went from 897 noise matches to 2 honest violations.
2. **Truncating lines at the first comment token false-passed TLS checks:** `http://` contains `//`, so in C-family files the pattern could never survive truncation — ExposeAR `tls-only` PASSed while two plain-HTTP URLs sat in .cs files. Fixed positionally: a match counts iff it starts before the comment token. Rule: when filtering by comment token, never mutate the haystack a pattern must match against.
3. Both behaviors have fixture canaries now: `no-shell-exec` (include filtering) and `endpoint-pinned` (`expect: present` with `//` inside the pattern + trailing comment on the matching line). Verify a checker's fix with an independent tool before trusting its verdict — the false-pass was caught by cross-checking with a second grep.
