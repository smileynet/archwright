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
