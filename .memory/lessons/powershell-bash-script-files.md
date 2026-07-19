# Bash from PowerShell: always a script file, never an inline string

One-line: PowerShell interpolates `$PATH`/`$?`/`$@` inside double-quoted `bash -c` strings — and Windows Python can't see bash's `/tmp`.

**Date:** 2026-07-17 · **Source:** DemoAR-lane session (bit twice in one day despite a prior lessons entry)

Failure modes observed live:
1. `& bash.exe -lc "...$?..."` → PowerShell substitutes ITS `$?` (prints `rc=True`) —
   a silently corrupted verdict, worse than the loud `unexpected EOF` variant.
2. `python - <<EOF` inside Git bash, asserting on files written to `/tmp/...` —
   Windows-native Python doesn't share bash's `/tmp` mount; the test failed with a
   misleading assertion error, not a path error.

Rules:
- Multi-line or `$`-containing bash commands go in a `.sh` file under `.scratch/`,
  invoked as `& "C:\Program Files\Git\bin\bash.exe" script.sh`.
- Cross-interpreter temp files (bash writes, Windows python reads) use repo-relative
  paths, never `/tmp`.

Queued upstream as crew-research ticket 12 (windows.md steering suggestion).
