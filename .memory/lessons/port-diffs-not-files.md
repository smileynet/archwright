# Port diffs, never whole files — and verify content, not commit messages

**One-line:** A commit claiming `feat(check): run bounded Alloy verification` actually REPLACED check.py + compile-alloy.py with a 760-line pre-Phase-5 lineage, wiping baseline/evidence/fingerprints/CK-03 AND the coverage modes its own sibling commits had just added (c5d2c81, repaired f08e20e, 2026-07-19).

## Incident

The other work lane ported adaptations from a forked archwright copy back to
upstream. Thirteen commits ported correctly (diff-on-top: 2,380-line check.py
with both lanes' features at cb29fcf). The fourteenth copied whole files from
the fork's older tree, silently regressing ~1,500 lines. Upstream main's
fixture suite crashed outright; AGENTS.md promised flags the tool no longer
had. Its new unit tests encoded the OLD lineage's semantics (`skipped` where
the contract says `pending`) — tests written against the wrong baseline pass
locally and entrench the regression.

## Rules

1. **Port by diff, never by file copy**, when moving work between repo copies.
   A whole-file copy from a fork is a time machine.
2. **Verify feature presence, not commit messages.** Review a merge by
   grepping the incoming tree for known feature markers
   (`baseline|evidence|fingerprint|contrast_pair`) and comparing line counts —
   a net-negative diffstat on a core tool is a red flag, whatever the message says.
3. **Suite green before push** — the receiving repo's suite is the arbiter;
   run it at the final tree, not just after your own commits.
4. **Merges reintroduce policy violations.** The same merge reintroduced the
   real target-project name in 2 files (sanitization convention, README status
   line staleness) — caught only by an incidental grep hours later. After any
   merge, sweep repo-wide conventions (sanitization aliases, status lines),
   not just the suite.
5. Scratch worktree (`git worktree add /tmp/x origin/main`) proves upstream
   health without disturbing local state; remove with `--force` after.

## Repair pattern used

Restore clobbered files from the last-good commit (`git checkout <sha> -- <files>`),
KEEP the offending commit's legitimate additions, delete tests encoding stale
semantics (with a re-add invitation in the commit message), suite as final arbiter.
