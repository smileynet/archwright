# Global Reflections

Methodology-level lessons from archwright spec derivation and checking. These apply to ALL target projects regardless of language or structure.

## How to use

- Read before `archwright-derive` (step 1b)
- Add a new entry when a spec failure reveals a methodology-level pitfall
- Keep entries concrete and actionable (not vague principles)

## Entries

### R1: grep patterns with alternation require exclude analysis (2026-07-13)

**Failure:** `resolver-owns-derivation` spec used pattern `step_ball_carriers|mirror_positions|carry_forward` with `expect: absent`. After `grep -E` was enabled (correct behavior), the alternation matched read-only field accesses — not just derivation logic.

**Lesson:** When writing `expect: absent` constraints with `|` alternation:
1. The pattern will match ALL occurrences of each term (reads AND writes)
2. Before committing, run the check and inspect every match
3. Categorize: is this a violation (writes/computes) or legitimate use (reads/declares)?
4. Add legitimate uses to `exclude` (string or list of path substrings)
5. `exclude` filters by file path, not line content — use filenames, not code patterns

### R2: skeleton specs should target specific files, not broad directories (2026-07-14)

**Failure (anticipated):** A skeleton spec targeting `client/src/` with `expect: absent` would match broadly and require many excludes. A skeleton targeting `client/src/execution/play_manager3d.gd` is precise and immediately actionable.

**Lesson:** Skeleton specs exist to validate ONE commitment quickly. Target the most specific file that embodies the pattern's primary invariant. If you need a broad directory target, it's not a skeleton — it's a full constraint spec.

### R3: behavior specs with context variables need accumulated state for guard evaluation (2026-07-13)

**Failure:** Python trace validator evaluated guards against only the current event's context snapshot. Multi-step state (e.g., `pending_completions` decremented across events) was lost between events.

**Lesson:** When writing behavior specs with context variables:
1. Guards reference accumulated state, not per-event deltas
2. Trace events should include the full relevant context at each step (or at least the variables referenced by guards)
3. The bash validator (archwright-trace-validate) checks transitions only — it doesn't evaluate guards. The Python validator (archwright-check --trace) evaluates guards against accumulated context.

### R4: First trace validation run always reveals spec inaccuracies (2026-07-14)

**Source:** OCI-vercel review — initial spec was missing `running_migrations` state. Trace validation caught this on first run.

**Lesson:** The first trace validation against a new behavior spec almost always reveals inaccuracies. This is the feedback loop working, not a derivation failure.
1. After deriving a behavior spec, immediately write one trace — the act forces precision the spec alone doesn't demand
2. Expect the spec-to-trace loop to iterate at least once
3. Don't treat first-run trace failures as "broken spec" — treat them as refinement signals

### R5: Default to grep, not semgrep — structure is the decision boundary (2026-07-14)

**Source:** Spike S1 — "Bad semgrep patterns: simple presence/absence of a string. Single-line patterns without structural context."

**Lesson:** When deriving constraint specs, default to `method: grep` unless the check requires understanding code STRUCTURE:
- Does the constraint involve try/catch blocks, object literals, nested scopes, import graphs? → semgrep
- Is it simple presence/absence of a term or pattern? → grep
- Semgrep for "does string X appear?" is unnecessary complexity with slower execution

### R6: Drift accumulates in error/recovery paths, not happy paths (2026-07-14)

**Source:** OCI-vercel review — 4 drift findings, ALL in recovery/fallback code, none in the primary deploy flow.

**Lesson:** Happy paths are well-tested and architecturally sound. Drift hides in error handlers, recovery code, and fallback paths — these are exercised less and often added hastily.
1. When running semantic review, prioritize error paths over happy paths
2. Ask explicitly: "What happens when this fails? Does the failure path honor the spec?"
3. Constraint specs should include error-path examples in their "Violations Look Like" section

### R7: Pipeline phase discipline prevents compounding errors (2026-07-14)

**Source:** ADR-0003, archwright-conventions.md, multiple sessions. "Pattern quality depends on force quality. Spec quality depends on pattern quality."

**Lesson:** Skipping human review between pipeline phases ALWAYS compounds errors. A bad force → misframed tension → wrong pattern → specs that verify the wrong invariant. Each phase must be reviewed before feeding the next.
1. Never auto-advance between phases — even when user says "proceed," execute ONE phase
2. If uncertain whether output is correct, present and ask rather than continuing
3. The cost of stopping is always lower than the cost of unwinding 5 derived specs

### R8: Don't adopt tools that aren't clearly better than grep+semgrep (2026-07-14)

**Source:** Spike S5 — ArchUnitTS "works and is expressive enough but is not clearly better." Conditionally adopted, never actually used.

**Lesson:** Tools that are "fine but not clearly better" will never be adopted. The overhead of installing, configuring, and maintaining a dependency must produce measurably better results than the existing approach. For archwright, grep + semgrep covers 95%+ of constraint checking needs.
1. Before recommending a new tool: "What does this catch that grep/semgrep misses?"
2. If the answer is "nothing in current specs" → don't adopt
3. A tool is only worth recommending when it solves a demonstrated gap

### R9: Spec-ahead is normal and healthy — categorize, don't alarm (2026-07-14)

**Source:** LBP alignment review — 2 gaps both classified as spec-ahead (ball-possession, step-advancement).

**Lesson:** Specs that describe the NEXT implementation increment are a feature, not a bug. They provide a blueprint. Always categorize findings:
- **Drift** — implementation violates spec (bug — fix the code)
- **Spec-ahead** — spec describes something not yet built (expected — implement next)
- **Gap** — implementation exists without a spec (derive needed)

Never present spec-ahead as a "failure" in alignment reports. The `--coverage` mode now detects this mechanically.

### R10: Report subagent failures explicitly — never silent fallback (2026-07-14)

**Source:** subagent-reliability.md steering, multiple sessions with empty returns.

**Lesson:** When a subagent returns empty or errors:
1. Report immediately: "Subagent returned empty. Retrying with smaller prompt."
2. If falling back to direct read, say so: "Falling back to direct read — less systematic."
3. Never present a direct-read result as if it came from systematic subagent extraction
4. The user needs to distinguish rigorous from improvised
