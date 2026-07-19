# Lessons — archwright tooling

One durable lesson per file, one-line summary at the top of each. Formerly a
single `lessons.md` (migrated 2026-07-17) — ticket references like
"lessons.md #5" point at the session log below.

**Conventions:** add a new file per lesson (topical slug, not date); update an
existing file rather than duplicating; delete files proven wrong. Session
records (run stats, baselines) belong in the session log here, not in lesson
files.

## Index

| Lesson | One-line |
|--------|----------|
| [utf8-encoding-explicit](utf8-encoding-explicit.md) | Windows cp1252 default silently broke ★-confidence parsing |
| [fail-loud-missing-tooling](fail-loud-missing-tooling.md) | Absent `grep` → empty stdout → false PASS; the checker itself must fail loud |
| [skills-tools-lockstep](skills-tools-lockstep.md) | Grep the tools for every field a skill mandates |
| [suite-after-tool-changes](suite-after-tool-changes.md) | Output format is a contract; only the fixture suite catches format drift |
| [concurrent-sessions](concurrent-sessions.md) | Test-merge, merge, suite, deploy, push — never assume sole ownership of main |
| [mise-rehydration](mise-rehydration.md) | mise owns tools/env/tasks; Windows python3 + bash-activation gotchas |
| [yaml-on-boolean-keys](yaml-on-boolean-keys.md) | `on:` parses as boolean True — months of vacuous behavior checks |
| [checkers-need-negative-tests](checkers-need-negative-tests.md) | A checker proven only on passing cases may be vacuous |
| [reporters-surface-source-reason](reporters-surface-source-reason.md) | Wrappers restating a tool's status in their own words drift into lies |
| [alloy-context-vars-frozen](alloy-context-vars-frozen.md) | `alloy:` expressions must reference M.current only — context vars are frozen |
| [skills-no-repo-relative-paths](skills-no-repo-relative-paths.md) | Deployed skills run from target projects — `<archwright-repo>/` placeholders |
| [comment-filtering-positional](comment-filtering-positional.md) | Never truncate the haystack — `http://` contains `//` |
| [powershell-bash-script-files](powershell-bash-script-files.md) | Inline `bash -c` from PowerShell corrupts `$`-expressions; use script files; `/tmp` invisible to Windows python |
| [alloy-safety-skeletons](alloy-safety-skeletons.md) | Render leads-to as safety skeletons; probe non-vacuity before trusting PASS |

## Session log

| Date | Session | Outcome |
|------|---------|---------|
| 2026-07-16 | First full pipeline run on Windows (DemoAR) | End-to-end validation on a real brownfield Unity/MR project: 93 forces, 13 tensions, 13 patterns, 44 specs; check surfaced genuine violations once tooling was fixed. Artifacts in DemoAR `design/` + `.memory/`. Field wants became tickets 005/006. (Was "lessons.md 2026-07-16 #1–7") |
| 2026-07-17 | mise adoption | mise.toml owns tools/env/tasks; baseline 22/0/0 at adoption. (Was "#1–4") |
| 2026-07-17 | Alloy wiring + DoD-5 chain | First jar execution exposed two dormant compiler bugs; CK-03/04/05/09/10 + CK-21 landed. |
| 2026-07-17 | include: globs + comment false-pass (DemoAR lane) | Concurrent implementation reconciled; positional comment matching; DemoAR tls-only 897 noise → 2 honest violations. Baseline 31/0/0. |
| 2026-07-17 | DemoAR close-out + DemoVR handoff (DemoAR lane) | Check phase CLOSED (1/6/26/0 — 6 FAILs = intentional work queue); first field alloy authoring (5 invariants bounded-checked, non-vacuity verified); project continues as DemoVR (`~/code/DemoVR/HANDOFF.md`); tickets 007–010 queued; crew-research tickets 12/13 (push pending Code Defender approval). |
