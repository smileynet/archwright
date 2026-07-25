# Deprecated — removal queue

Files/paths that have been superseded but not yet removed. One row per item;
remove when the condition is met (usually during a project-cleanup pass), then
delete the row. Rows are claims — verify the condition before removing.

**Maintenance:** repo-maintenance coverage audit step 4 reviews this list.
Add a row the moment something becomes redundant (merge leftovers, superseded
mechanisms, dated working notes) — don't wait for a cleanup pass to rediscover it.

| Path | Superseded by | Remove when | Added |
|------|---------------|-------------|-------|
| Legacy jar fallback in `tools/archwright-check.py` `_find_alloy_jar` (`~/code/archwright/.references/alloy6.jar`, line ~410) | `ARCHWRIGHT_ALLOY_JAR` env (mise sets it) + script-relative path | No machine relies on the legacy checkout location (verify: env var set on all dev machines) | 2026-07-19 |
| `.memory/review-improvements-2026-07-11.md` | Its actionable items were absorbed into skills/tools (upstream commit ec359c6 claims "review improvements") | Verify absorption claim (diff its recommendations vs current skills), then delete | 2026-07-19 (upstream merge) |

## Not deprecated (explicitly, to stop re-flagging)

- `tools/archwright-check-compile.mjs` — prototype awaiting its ADR 0012 rewrite trigger (20+ specs); load-bearing for the intent→check workflow until then
- `tools/archwright-compile-alloy.py` — c5d2c81's rewrite attempt was reverted (regressed suite features, see `.memory/lessons/port-diffs-not-files.md`); the ADR 0012 rewrite intent stands but THIS version is the working one
- `audit-plan.md` — CLOSED but kept deliberately as the close-out record
- `.memory/spike-findings/` (ex `design/findings/`) — historical spike evidence, correctly homed 2026-07-19
