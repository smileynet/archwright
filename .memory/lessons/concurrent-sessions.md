# Concurrent sessions on main are normal — merge discipline

One-line: never assume sole ownership; test-merge, then merge, suite, deploy, push.

**Date:** 2026-07-16 (recurred 3× on 2026-07-17) · **Source:** multiple sessions

Upstream main repeatedly gains commits mid-session (7 once; two full collisions
in one day, including two independent implementations of the same feature).
Protocol: `git fetch` before push; `git merge --no-commit --no-ff` to test;
after any merge run `mise run test` AND `mise run deploy-skills` (upstream skill
edits go stale in ~/.kiro silently). Two lanes implementing one feature can be
productive — the reconciliation unioned the better halves of each.
