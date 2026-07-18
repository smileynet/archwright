#!/usr/bin/env bash
# Run all archwright checks against the lacrosse-bosse fixture.
# Exit 0 if all pass (or fixture is empty), 1 if any fail.
set -euo pipefail

TOOLS="$(dirname "$0")"
FIXTURE="$TOOLS/../tests/fixtures/lacrosse-bosse"
VALIDATE="$TOOLS/archwright-validate.py"
CHECK="$TOOLS/archwright-check.py"
PASS=0
FAIL=0
SKIP=0

# Windows: `python3` may be a broken MS Store stub, and mise-managed python ships
# only `python.exe`. Prefer a python3 that actually runs; else delegate to `python`.
if ! python3 -c 'pass' >/dev/null 2>&1; then
  if python -c 'pass' >/dev/null 2>&1; then
    python3() { python "$@"; }
  else
    echo "ERROR: no working python3/python on PATH (try: mise install)" >&2
    exit 2
  fi
fi

report() {
  if [ "$1" = "PASS" ]; then
    echo "  ✓ $2"
    PASS=$((PASS + 1))
  elif [ "$1" = "SKIP" ]; then
    echo "  ○ $2"
    SKIP=$((SKIP + 1))
  else
    echo "  ✗ $2"
    [ -n "${3:-}" ] && echo "    $3"
    FAIL=$((FAIL + 1))
  fi
}

# Schema Validation (forces + patterns + specs) — `|| true` guards set -e when dirs are absent
forces=$(find "$FIXTURE/design/forces" -name "*.md" 2>/dev/null | sort || true)
patterns=$(find "$FIXTURE/design/patterns" -name "*.md" 2>/dev/null | sort || true)
specs=$(find "$FIXTURE/design/specs" \( -name "*.md" -o -name "*.yaml" \) 2>/dev/null | sort || true)

if [ -z "$forces" ] && [ -z "$patterns" ] && [ -z "$specs" ]; then
  echo "=== Fixture is empty — no forces, patterns, or specs to validate ==="
  echo "=== Results: 0 passed, 0 failed (clean slate) ==="
  exit 0
fi

echo "=== Schema Validation ==="
for f in $forces $patterns $specs; do
  if python3 "$VALIDATE" "$f" > /dev/null 2>&1; then
    report PASS "$(basename "$f")"
  else
    report FAIL "$(basename "$f")" "$(python3 "$VALIDATE" "$f" 2>&1)"
  fi
done

# Link Validation
echo ""
echo "=== Link Validation ==="
if python3 "$VALIDATE" --links "$FIXTURE/design/" > /dev/null 2>&1; then
  report PASS "all links resolve"
else
  report FAIL "broken links" "$(python3 "$VALIDATE" --links "$FIXTURE/design/" 2>&1)"
fi

# Conformance Checks (constraint/dependency specs with check blocks)
echo ""
echo "=== Conformance Checks ==="
md_specs=$(find "$FIXTURE/design/specs" -name "*.md" 2>/dev/null | sort || true)
if [ -z "$md_specs" ]; then
  report SKIP "no constraint/dependency specs to check"
else
  for f in $md_specs; do
    result=$(python3 "$CHECK" "$f" 2>&1 || true)
    if echo "$result" | grep -q "PASS"; then
      report PASS "$(basename "$f" .md)"
    elif echo "$result" | grep -q "SKIP"; then
      report SKIP "$(basename "$f" .md)"
    else
      report FAIL "$(basename "$f" .md)" "$result"
    fi
  done
fi

# Behavior Checks (Alloy if jar present, else SKIP)
echo ""
echo "=== Behavior Checks ==="
yaml_behavior=$(grep -l "^kind: behavior" "$FIXTURE"/design/specs/*.yaml 2>/dev/null | sort || true)
if [ -z "$yaml_behavior" ]; then
  report SKIP "no behavior specs"
else
  for f in $yaml_behavior; do
    result=$(python3 "$CHECK" "$f" 2>&1 || true)
    if echo "$result" | grep -q "PASS"; then
      report PASS "$(basename "$f" .yaml)"
    elif echo "$result" | grep -q "SKIP"; then
      # Surface check.py's actual skip reason (jar missing / java missing / no alloy: expression)
      reason=$(echo "$result" | sed -n '2p' | sed 's/^ *//' | cut -c1-60)
      report SKIP "$(basename "$f" .yaml) (${reason:-skipped})"
    else
      report FAIL "$(basename "$f" .yaml)" "$result"
    fi
  done
fi

echo ""
echo "=== Guard Compilation Conformance (ticket 008) ==="
# Golden corpus (Extension Protocol rule 4): guarded spec PASSes, its
# unguarded twin FAILs (the invariant is provable ONLY with the guard
# compiled), and an opaque-guard twin SKIPs with reason (rule 1 — never a
# spurious FAIL). Requires the Alloy jar + java, like behavior checks.
GUARD_SPECS="$TOOLS/../tests/fixtures/guarded-counter/design/specs"
GC_JAR="${ARCHWRIGHT_ALLOY_JAR:-$TOOLS/../.references/alloy6.jar}"
if [ ! -d "$GUARD_SPECS" ]; then
  report SKIP "guard conformance (fixture missing)"
elif [ ! -f "$GC_JAR" ] || ! command -v java >/dev/null 2>&1; then
  report SKIP "guard conformance (alloy jar or java unavailable)"
else
  if python3 "$VALIDATE" "$GUARD_SPECS"/*.yaml >/dev/null 2>&1; then
    report PASS "guard fixture: all 3 specs schema-valid"
  else
    report FAIL "guard fixture: all 3 specs schema-valid"
  fi

  rc=0; out=$(python3 "$CHECK" "$GUARD_SPECS/zone-progress.yaml" 2>&1) || rc=$?
  if [ $rc -eq 0 ] && echo "$out" | grep -q "PASS"; then
    report PASS "guard compiled: solved-iff-win-condition holds (bounded)"
  else
    report FAIL "guard compiled: solved-iff-win-condition holds (bounded)" "$out"
  fi

  rc=0; out=$(python3 "$CHECK" "$GUARD_SPECS/zone-progress-unguarded.yaml" 2>&1) || rc=$?
  if [ $rc -eq 1 ] && echo "$out" | grep -q "counterexample"; then
    report PASS "guard removed: same invariant FAILs w/ counterexample (non-vacuous)"
  else
    report FAIL "guard removed: same invariant FAILs w/ counterexample (non-vacuous)" "exit=$rc: $out"
  fi

  rc=0; out=$(python3 "$CHECK" "$GUARD_SPECS/zone-progress-opaque-guard.yaml" 2>&1) || rc=$?
  if [ $rc -eq 0 ] && echo "$out" | grep -q "reachable without their guard"; then
    report PASS "opaque guard: invariant SKIPs with taint reason (no spurious FAIL)"
  else
    report FAIL "opaque guard: invariant SKIPs with taint reason (no spurious FAIL)" "exit=$rc: $out"
  fi
fi

echo ""
echo "=== Tool Conformance: forces-gen + probe ==="
# forces-gen: inventory → force files (conformance at birth, rule 4: incl. failing case)
FG_DIR=$(mktemp -d)
cat > "$FG_DIR/inv.yaml" <<'EOF'
product_forces:
  - id: probe-desire
    polarity: desire
    statement: "Someone wants a thing."
    who: user
    evidence_level: L1
    provenance: [{source: "test", quote: "quote"}]
forces:
  - id: probe-constraint
    polarity: constraint-hard
    statement: "A bound is given."
    serves: probe-desire
    evidence_level: L1
    provenance: [{source: "test", quote: "quote"}]
EOF
if python3 "$TOOLS/archwright-forces-gen.py" "$FG_DIR/inv.yaml" -o "$FG_DIR/out" >/dev/null 2>&1 \
   && [ "$(ls "$FG_DIR/out" | wc -l)" = "2" ] \
   && python3 "$VALIDATE" "$FG_DIR/out"/*.md >/dev/null 2>&1; then
  report PASS "forces-gen: inventory → 2 valid force files"
else
  report FAIL "forces-gen: inventory → 2 valid force files"
fi
cat > "$FG_DIR/bad.yaml" <<'EOF'
forces:
  - id: bad-force
    polarity: not-a-polarity
    statement: "s"
    provenance: [{source: "t", quote: "q"}]
EOF
if python3 "$TOOLS/archwright-forces-gen.py" "$FG_DIR/bad.yaml" -o "$FG_DIR/out2" >/dev/null 2>&1; then
  report FAIL "forces-gen: invalid polarity = tool error (exit 2)"
else
  report PASS "forces-gen: invalid polarity = tool error (exit 2)"
fi
rm -rf "$FG_DIR"

# --probe: non-vacuity probing (jar-gated like behavior checks)
PROBE_JAR="${ARCHWRIGHT_ALLOY_JAR:-$TOOLS/../.references/alloy6.jar}"
if [ ! -f "$PROBE_JAR" ] || ! command -v java >/dev/null 2>&1; then
  report SKIP "probe conformance (alloy jar or java unavailable)"
else
  rc=0; python3 "$CHECK" --probe "$FIXTURE/design/specs/ball-state-lifecycle.yaml" >/dev/null 2>&1 || rc=$?
  if [ $rc -eq 0 ]; then
    report PASS "probe: live model → false invariant FAILs (exit 0)"
  else
    report FAIL "probe: live model → false invariant FAILs (exit 0)" "exit=$rc"
  fi
  # Vacuous case: a transition guarded by an unsatisfiable condition — the
  # target state is syntactically present but semantically unreachable, so
  # the false invariant PASSES and probe must report vacuity (exit 1).
  PR_DIR=$(mktemp -d)
  cat > "$PR_DIR/vacuous.yaml" <<'EOF'
kind: behavior
id: vacuous-machine
from_patterns: ["pattern:zone-progress"]
protects_experience: "test"
user_story: "test"
context:
  variables:
    n:
      type: int
      initial: 0
initial: idle
states:
  idle:
    type: atomic
    "on":
      GO:
        target: done
        guard:
          predicate: "n == 5"
          confidence: "★★"
  done:
    type: atomic
    "on": {}
invariants: []
EOF
  rc=0; python3 "$CHECK" --probe "$PR_DIR/vacuous.yaml" >/dev/null 2>&1 || rc=$?
  if [ $rc -eq 1 ]; then
    report PASS "probe: unreachable target → vacuity reported (exit 1)"
  else
    report FAIL "probe: unreachable target → vacuity reported (exit 1)" "exit=$rc"
  fi
  rm -rf "$PR_DIR"
fi

echo ""
echo "=== Stack Adapter Conformance: typescript.trace_emitter ==="
# Extension Protocol rules 3-5: spike output is the scenario; corpus includes a
# violating trace that must FAIL; status is computed by this suite.
TE_DIR="$TOOLS/stacks/typescript/trace_emitter"
if ! command -v node >/dev/null 2>&1; then
  report SKIP "ts trace emitter conformance (node unavailable)"
else
  TE_OUT=$(mktemp -d)
  if node --experimental-strip-types "$TE_DIR/conformance/scenario.ts" "$TE_OUT" >/dev/null 2>&1; then
    report PASS "ts-emitter: scenario emits traces via recorder"
  else
    report FAIL "ts-emitter: scenario emits traces via recorder"
  fi
  rc=0; python3 "$CHECK" --trace "$TE_DIR/conformance/ts-emitter-conformance.yaml" "$TE_OUT/passing.trace.json" >/dev/null 2>&1 || rc=$?
  if [ $rc -eq 0 ]; then
    report PASS "ts-emitter: guarded run trace validates (exit 0)"
  else
    report FAIL "ts-emitter: guarded run trace validates (exit 0)" "exit=$rc"
  fi
  rc=0; python3 "$CHECK" --trace "$TE_DIR/conformance/ts-emitter-conformance.yaml" "$TE_OUT/violating.trace.json" >/dev/null 2>&1 || rc=$?
  if [ $rc -eq 1 ]; then
    report PASS "ts-emitter: unguarded run trace FAILs at capacity breach (exit 1)"
  else
    report FAIL "ts-emitter: unguarded run trace FAILs at capacity breach (exit 1)" "exit=$rc"
  fi
  rm -rf "$TE_OUT"
fi

echo ""
echo "=== Check-Tool Feature Tests ==="
# Golden assertions for check-backend features (tickets 005/006) — temp specs
# run against the fixture tree, cleaned up unconditionally.
FEAT_DIR=$(mktemp -d)
trap 'rm -rf "$FEAT_DIR"' EXIT
export ARCHWRIGHT_PROJECT_ROOT="$(cd "$FIXTURE" && pwd)"

# 005a: include glob scopes matching — 'extends' exists in .gd files, but scoped
# to a glob matching nothing it must not FAIL. Since ticket 012 this reports
# skipped (vacuous absent: scanned nothing, proved nothing), still exit 0.
cat > "$FEAT_DIR/incl-scope.md" <<'EOF'
---
kind: constraint
id: incl-scope
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: "client/src"
  pattern: "extends"
  include: "*.nomatch"
  expect: absent
---
# T
## Rule
Include glob excludes all files.
EOF
rc=0; INCL_OUT=$(python3 "$CHECK" --json "$FEAT_DIR/incl-scope.md" 2>&1) || rc=$?
if [ "$rc" -eq 0 ] && echo "$INCL_OUT" | grep -q '"skipped": 1'; then
  report PASS "feature: include glob matching nothing = vacuous SKIP, exit 0 (005a/012)"
else
  report FAIL "feature: include glob matching nothing = vacuous SKIP, exit 0 (005a/012)" "exit=$rc"
fi

# 005b: include glob admits matching files (expect: present with *.gd → PASS).
cat > "$FEAT_DIR/incl-admit.md" <<'EOF'
---
kind: constraint
id: incl-admit
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: "client/src"
  pattern: "extends"
  include: ["*.gd"]
  expect: present
---
# T
## Rule
Include glob admits .gd files.
EOF
if python3 "$CHECK" "$FEAT_DIR/incl-admit.md" >/dev/null 2>&1; then
  report PASS "feature: include glob (list form) admits matching files"
else
  report FAIL "feature: include glob (list form) admits matching files"
fi

# 006a: multi-target union — pattern only in project.godot; list target must find it.
cat > "$FEAT_DIR/multi-target.md" <<'EOF'
---
kind: constraint
id: multi-target
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: ["client/src", "project.godot"]
  pattern: "config_version"
  expect: present
---
# T
## Rule
Multi-target unions matches.
EOF
if python3 "$CHECK" "$FEAT_DIR/multi-target.md" >/dev/null 2>&1; then
  report PASS "feature: multi-target unions matches across roots"
else
  report FAIL "feature: multi-target unions matches across roots"
fi

# 006b: missing entry in a target list = loud tool error (exit 2).
cat > "$FEAT_DIR/multi-missing.md" <<'EOF'
---
kind: constraint
id: multi-missing
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: ["client/src", "does/not/exist"]
  pattern: "x"
  expect: absent
---
# T
## Rule
Missing target list entry errors loudly.
EOF
rc=0; python3 "$CHECK" "$FEAT_DIR/multi-missing.md" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 2 ]; then
  report PASS "feature: missing multi-target entry = tool error (exit 2)"
else
  report FAIL "feature: missing multi-target entry = tool error (exit 2)" "exit was $rc"
fi

# CK-05 regression: unknown expect value = tool error (exit 2), never silent pass.
cat > "$FEAT_DIR/bad-expect.md" <<'EOF'
---
kind: constraint
id: bad-expect
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: "client/src"
  pattern: "x"
  expect: absnet
---
# T
## Rule
Unknown expect errors.
EOF
rc=0; python3 "$CHECK" "$FEAT_DIR/bad-expect.md" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 2 ]; then
  report PASS "feature: unknown expect value = tool error (exit 2)"
else
  report FAIL "feature: unknown expect value = tool error (exit 2)" "exit was $rc"
fi

unset ARCHWRIGHT_PROJECT_ROOT

echo ""
echo "=== Pattern Status: gated (ticket 011) ==="
# gated = resolution ratified, activation gated on a named event. Requires
# gated_on:; fog stays reserved for unresolved tension (never a ratified deferral).
PS_DIR=$(mktemp -d)
cat > "$PS_DIR/gated-ok.md" <<'EOF'
---
kind: pattern
id: gated-ok
name: "Gated OK"
scale: loops-systems
confidence: "★"
status: gated
gated_on: "Unity 6 migration"
---
# Gated OK
EOF
rc=0; python3 "$VALIDATE" "$PS_DIR/gated-ok.md" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  report PASS "pattern-status: gated with gated_on validates (exit 0)"
else
  report FAIL "pattern-status: gated with gated_on validates (exit 0)" "exit=$rc"
fi
cat > "$PS_DIR/gated-bad.md" <<'EOF'
---
kind: pattern
id: gated-bad
name: "Gated Bad"
scale: loops-systems
confidence: "★"
status: gated
---
# Gated Bad
EOF
PS_OUT=""; rc=0; PS_OUT=$(python3 "$VALIDATE" "$PS_DIR/gated-bad.md" 2>&1) || rc=$?
if [ "$rc" -ne 0 ] && echo "$PS_OUT" | grep -q "requires a gated_on"; then
  report PASS "pattern-status: gated without gated_on rejected"
else
  report FAIL "pattern-status: gated without gated_on rejected" "exit=$rc"
fi
rm -rf "$PS_DIR"

echo ""
echo "=== from_model Resolution: Boundary Producers + Folds (ticket 013) ==="
# Boundary entities named as producers in contract_candidates are valid
# from_model targets; plain boundary entities and unknown ids still FAIL;
# folded candidates follow the fold for coverage.
FM_DIR=$(mktemp -d)
mkdir -p "$FM_DIR/design/models" "$FM_DIR/design/specs" "$FM_DIR/design/patterns"
cat > "$FM_DIR/design/patterns/content-pipeline.md" <<'EOF'
---
kind: pattern
id: content-pipeline
status: active
confidence: "★"
---
# content-pipeline
EOF
cat > "$FM_DIR/design/models/actors.yaml" <<'EOF'
actors:
  - id: session-host
    name: Session Host
boundary_entities:
  - {id: content-authority, name: "puzzles.yaml", classification: configuration-authority, why: "authored reference"}
  - {id: plain-helper, name: "util.ts", classification: boundary-service, why: "no contracts"}
contract_candidates:
  - {event: puzzle-definition, producer: content-authority, consumers: [session-host]}
  - {event: placement-command, producer: session-host, consumers: [renderer]}
  - {event: placement-verdict, producer: session-host, consumers: [renderer], folded_into: placement-command}
EOF
cat > "$FM_DIR/design/specs/puzzle-definition.yaml" <<'EOF'
kind: contract
id: puzzle-definition
from_patterns: ["pattern:content-pipeline"]
confidence: "★"
from_model: "model:content-authority"
events:
  puzzle-definition:
    producer: content-authority
    consumers: [session-host]
    stability: internal
    payload:
      fields:
        - {name: pid, type: string, required: true}
EOF
cat > "$FM_DIR/design/specs/placement-command.yaml" <<'EOF'
kind: contract
id: placement-command
from_patterns: ["pattern:content-pipeline"]
confidence: "★"
from_model: "model:session-host"
events:
  placement-command:
    producer: session-host
    consumers: [renderer]
    stability: internal
    payload:
      fields:
        - {name: pos, type: string, required: true}
EOF
rc=0; python3 "$VALIDATE" --links "$FM_DIR/design" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  report PASS "from_model: producer boundary entity + folded candidate resolve (exit 0)"
else
  report FAIL "from_model: producer boundary entity + folded candidate resolve (exit 0)" "exit=$rc"
fi
# Violating: plain boundary entity (not a producer) must FAIL with the precise message.
sed -i.bak 's/model:content-authority/model:plain-helper/' "$FM_DIR/design/specs/puzzle-definition.yaml"
rc=0; FM_OUT=$(python3 "$VALIDATE" --links "$FM_DIR/design" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] && echo "$FM_OUT" | grep -q "not a contract producer"; then
  report PASS "from_model: plain boundary entity FAILs with producer-rule message"
else
  report FAIL "from_model: plain boundary entity FAILs with producer-rule message" "exit=$rc"
fi
# Violating: nonexistent id must still FAIL (no vacuous acceptance).
sed -i.bak 's/model:plain-helper/model:ghost-entity/' "$FM_DIR/design/specs/puzzle-definition.yaml"
rc=0; python3 "$VALIDATE" --links "$FM_DIR/design" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 1 ]; then
  report PASS "from_model: nonexistent id still FAILs (exit 1)"
else
  report FAIL "from_model: nonexistent id still FAILs (exit 1)" "exit=$rc"
fi
sed -i.bak 's/model:ghost-entity/model:content-authority/' "$FM_DIR/design/specs/puzzle-definition.yaml"
# Violating: folded candidate with its OWN spec = double ownership, must FAIL.
cat > "$FM_DIR/design/specs/placement-verdict.yaml" <<'EOF'
kind: contract
id: placement-verdict
from_patterns: ["pattern:content-pipeline"]
confidence: "★"
from_model: "model:session-host"
events:
  placement-verdict:
    producer: session-host
    consumers: [renderer]
    stability: internal
    payload:
      fields:
        - {name: ok, type: boolean, required: true}
EOF
rc=0; FM_OUT=$(python3 "$VALIDATE" --links "$FM_DIR/design" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] && echo "$FM_OUT" | grep -q "ALSO directly covered"; then
  report PASS "from_model: folded candidate with own spec FAILs (double ownership)"
else
  report FAIL "from_model: folded candidate with own spec FAILs (double ownership)" "exit=$rc"
fi
rm -rf "$FM_DIR"

echo ""
echo "=== Vacuous Absence Guard (ticket 012) ==="
# expect:absent over a target that scans zero files must SKIP-with-reason,
# never PASS — while a real absent-check over real files still PASSes/FAILs.
VA_DIR=$(mktemp -d)
mkdir -p "$VA_DIR/proj/empty-dir"
cat > "$VA_DIR/vacuous-absent.md" <<'EOF'
---
kind: constraint
id: vacuous-absent
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: "empty-dir"
  pattern: "forbidden_thing"
  expect: absent
---
# T
## Rule
Forbidden pattern must not appear (but the target scans zero files).
EOF
rc=0; VA_OUT=$(python3 "$CHECK" --json --target "$VA_DIR/proj" "$VA_DIR/vacuous-absent.md" 2>&1) || rc=$?
if [ "$rc" -eq 0 ] && echo "$VA_OUT" | grep -q '"skipped": 1' && echo "$VA_OUT" | grep -qi "scanned nothing"; then
  report PASS "vacuous-absent: empty target = SKIP with reason, exit 0"
else
  report FAIL "vacuous-absent: empty target = SKIP with reason, exit 0" "exit=$rc"
fi
# Non-vacuous control: same spec shape over a real file — violation still FAILs.
printf 'ok line\nforbidden_thing here\n' > "$VA_DIR/proj/empty-dir/real.txt"
rc=0; python3 "$CHECK" --target "$VA_DIR/proj" "$VA_DIR/vacuous-absent.md" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 1 ]; then
  report PASS "vacuous-absent control: real violation still FAILs (exit 1)"
else
  report FAIL "vacuous-absent control: real violation still FAILs (exit 1)" "exit=$rc"
fi
rm -rf "$VA_DIR"

echo ""
echo "=== Trace Predicate Strict Mode (ticket 015) ==="
# Untranslatable predicates SKIP-with-reason at invariant/guard granularity —
# never silent-pass. Corpus includes a translatable violation that must still
# FAIL (Extension Protocol rule 4). Fixture: tests/fixtures/trace-strict/.
TS_FIX="$TOOLS/../tests/fixtures/trace-strict"
TS_OUT=$(mktemp)
rc=0; python3 "$CHECK" --trace "$TS_FIX/trace-strict-conformance.yaml" "$TS_FIX/ok.trace.json" > "$TS_OUT" 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  report PASS "trace-strict: pass-with-skips exits 0"
else
  report FAIL "trace-strict: pass-with-skips exits 0" "exit=$rc"
fi
if grep -q '"invariants_skipped": \[{"id": "opaque-comparison"' "$TS_OUT" && grep -q '"opaque-construct"' "$TS_OUT"; then
  report PASS "trace-strict: untranslatable invariants listed in invariants_skipped with reason"
else
  report FAIL "trace-strict: untranslatable invariants listed in invariants_skipped with reason"
fi
if grep -q '"invariants_checked": \["count-within-max"\]' "$TS_OUT"; then
  report PASS "trace-strict: skipped invariants excluded from invariants_checked"
else
  report FAIL "trace-strict: skipped invariants excluded from invariants_checked"
fi
if grep -q '"guards_skipped"' "$TS_OUT" && grep -q '"final_state": "running"' "$TS_OUT"; then
  report PASS "trace-strict: untranslatable guard = transition accepted with skip note"
else
  report FAIL "trace-strict: untranslatable guard = transition accepted with skip note"
fi
rc=0; python3 "$CHECK" --trace "$TS_FIX/trace-strict-conformance.yaml" "$TS_FIX/violating.trace.json" > "$TS_OUT" 2>&1 || rc=$?
if [ "$rc" -eq 1 ]; then
  report PASS "trace-strict: translatable violation still FAILs (exit 1)"
else
  report FAIL "trace-strict: translatable violation still FAILs (exit 1)" "exit=$rc"
fi
if grep -q '"status": "fail"' "$TS_OUT" && grep -q '"invariants_skipped": \[{"id": "opaque-comparison"' "$TS_OUT"; then
  report PASS "trace-strict: fail output carries accumulated skips (no hidden coverage gaps)"
else
  report FAIL "trace-strict: fail output carries accumulated skips (no hidden coverage gaps)"
fi
rm -f "$TS_OUT"

echo ""
echo "=== Trace Mode CK-03 Document (ticket 016) ==="
# --trace --json emits the CK-03 document (check-output-schema.yaml) so passup
# routes trace violations uniformly with static ones. Bespoke shape stays the
# non-json output. Reuses the trace-strict fixture (★★ violating invariant +
# untranslatable skips exercise every mapping).
T16_OUT=$(mktemp)
rc=0; python3 "$CHECK" --trace "$TS_FIX/trace-strict-conformance.yaml" "$TS_FIX/ok.trace.json" --json > "$T16_OUT" 2>&1 || rc=$?
if [ "$rc" -eq 0 ] && grep -q '"mode": "trace"' "$T16_OUT" && grep -q '"status": "pass"' "$T16_OUT"; then
  report PASS "trace-ck03: passing trace emits CK-03 document (mode trace, exit 0)"
else
  report FAIL "trace-ck03: passing trace emits CK-03 document (mode trace, exit 0)" "exit=$rc"
fi
if grep -q '"invariant": "opaque-comparison"' "$T16_OUT" && grep -q '"invariant": null' "$T16_OUT"; then
  report PASS "trace-ck03: invariant + guard skips map into skips[] with reasons"
else
  report FAIL "trace-ck03: invariant + guard skips map into skips[] with reasons"
fi
if grep -q '"checked": 3' "$T16_OUT" && grep -q '"skipped": 2' "$T16_OUT"; then
  report PASS "trace-ck03: coverage counts invariants (3 checked, 2 skipped)"
else
  report FAIL "trace-ck03: coverage counts invariants (3 checked, 2 skipped)"
fi
rc=0; python3 "$CHECK" --trace "$TS_FIX/trace-strict-conformance.yaml" "$TS_FIX/violating.trace.json" --json > "$T16_OUT" 2>&1 || rc=$?
if [ "$rc" -eq 1 ] && grep -q '"status": "fail"' "$T16_OUT"; then
  report PASS "trace-ck03: violating trace emits fail document (exit 1)"
else
  report FAIL "trace-ck03: violating trace emits fail document (exit 1)" "exit=$rc"
fi
# All 10 violation fields present with correct derivations (★★ → error + escalate)
if grep -q '"invariant": "count-within-max"' "$T16_OUT" \
   && grep -q '"confidence": "★★"' "$T16_OUT" \
   && grep -q '"severity": "error"' "$T16_OUT" \
   && grep -q '"escalate": true' "$T16_OUT" \
   && grep -q '"from_pattern": "pattern:conformance-fixture"' "$T16_OUT" \
   && grep -q '"from_force": "conformance-fixture"' "$T16_OUT" \
   && grep -q '"suggested_route": "fix-implementation"' "$T16_OUT" \
   && grep -q '"contrast_pair"' "$T16_OUT" \
   && grep -q '"expected": "Count never exceeds max' "$T16_OUT" \
   && grep -q '"evidence"' "$T16_OUT"; then
  report PASS "trace-ck03: violation carries all 10 fields (★★ derives error+escalate, provenance, contrast_pair)"
else
  report FAIL "trace-ck03: violation carries all 10 fields (★★ derives error+escalate, provenance, contrast_pair)"
fi
if grep -q '"invariant": "opaque-comparison"' "$T16_OUT" && grep -q '"remaining_delta": 1' "$T16_OUT"; then
  report PASS "trace-ck03: fail document carries accumulated skips + remaining_delta"
else
  report FAIL "trace-ck03: fail document carries accumulated skips + remaining_delta"
fi
# Non-json output unchanged (bespoke replay shape, not the document)
rc=0; python3 "$CHECK" --trace "$TS_FIX/trace-strict-conformance.yaml" "$TS_FIX/ok.trace.json" > "$T16_OUT" 2>&1 || rc=$?
if grep -q '"assurance": "trace"' "$T16_OUT" && ! grep -q '"scope"' "$T16_OUT"; then
  report PASS "trace-ck03: non-json output keeps the bespoke replay shape"
else
  report FAIL "trace-ck03: non-json output keeps the bespoke replay shape"
fi
rm -f "$T16_OUT"

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $SKIP skipped ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
