# Test Fixture: lacrosse-bosse

Sanitized reference files from lacrosse-bosse-platform that exercise all archwright checks.

## Structure

```
project.godot                       # Godot project file (no autoloads)
client/src/
  services/
    ball_state_service.gd           # Single source of truth for ball possession
  execution/
    play_manager_3d.gd             # Pure step executor (no resolver, no UI, no builder)
    runtime_objective.gd           # Objective stub
  fielder/
    fielder_ai_controller.gd       # AI controller (uses request_transfer, no direct writes)
    fielder.gd                     # Fielder type stub
  play_data/
    play_resolver.gd              # Resolution logic (NOT in execution/)
    resolved_play_view.gd         # Pre-computed view stub
design/
  forces/
    ball-always-somewhere.md      # Desire: possession never ambiguous
    single-holder.md              # Constraint (hard): one holder — physics
    any-fielder-receives.md       # Desire: open play
    predictable-practice-runs.md  # Desire: deterministic replay
    testable-in-isolation.md      # Desire: headless testing
  patterns/
    ball-possession.md            # Pattern: single-holder + request/validate
    execution-purity.md           # Pattern: executor does only execution
    explicit-dependencies.md      # Pattern: no autoloads, explicit injection
  specs/
    ball-state-lifecycle.yaml     # Behavior spec (statechart)
    ball-possession-events.yaml   # Contract spec (event payloads)
    single-ball-writer.md         # Constraint: only BallStateService writes ball_holder
    ball-write-ownership.md       # Dependency: forbidden writers
    executor-no-resolve.md        # Constraint: execution/ never references PlayResolver
    executor-boundaries.md        # Dependency: PlayManager3D forbidden imports
    no-autoloads.md              # Constraint: no autoload registrations
```

## What This Exercises

| Check | Mechanism | Proves |
|-------|-----------|--------|
| Schema validation | Pattern frontmatter + spec YAML/frontmatter | Format correctness |
| Link validation | All kind:id references resolve | Provenance integrity |
| no-autoloads | grep project.godot | Simplest conformance check |
| executor-no-resolve | grep execution/ for PlayResolver | Code-level constraint |
| single-ball-writer | grep for ball_holder assignments | Write-ownership enforcement |
| executor-boundaries | grep play_manager_3d.gd for forbidden imports | Dependency boundary |

## Running

```bash
./tools/run-fixture-tests.sh
```

Expected: **26 passed, 0 failed, 0 skipped** with `.references/alloy6.jar` present (`mise run rehydrate-alloy`); without the jar the behavior spec SKIPs → 25 passed, 0 failed, 1 skipped. Two specs are regression canaries: `no-shell-exec` is the conformance corpus for `check.include:` glob filtering (`client/docs/porting-notes.md` deliberately contains its pattern in prose — a filtering regression flips it red), and `endpoint-pinned` guards positional comment handling (its pattern contains `//` inside `https://` — a regression to line-truncation flips it red).
