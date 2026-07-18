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

# CK-06: target_status: pending → coverage.pending (disjoint bucket), never
# pass/fail/skipped; reason still surfaces in skips[]; human output says PENDING.
cat > "$FEAT_DIR/ck06-pending.md" <<'EOF'
---
kind: constraint
id: ck06-pending
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: "not/built/yet"
  pattern: "foo"
  expect: present
  target_status: pending
---
# T
## Rule
Target not built yet.
EOF
rc=0; CK06_OUT=$(python3 "$CHECK" --json "$FEAT_DIR/ck06-pending.md" 2>&1) || rc=$?
if [ "$rc" -eq 0 ] \
   && echo "$CK06_OUT" | grep -q '"pending": 1' \
   && echo "$CK06_OUT" | grep -q '"skipped": 0' \
   && echo "$CK06_OUT" | grep -q '"target_status: pending'; then
  report PASS "ck06: pending spec = coverage.pending 1 / skipped 0, reason in skips[], exit 0"
else
  report FAIL "ck06: pending spec = coverage.pending 1 / skipped 0, reason in skips[], exit 0" "exit=$rc"
fi

CK06_HUMAN=$(python3 "$CHECK" "$FEAT_DIR/ck06-pending.md" 2>&1) || true
if echo "$CK06_HUMAN" | grep -q "PENDING: ck06-pending.md"; then
  report PASS "ck06: human output labels pending spec PENDING (not SKIP)"
else
  report FAIL "ck06: human output labels pending spec PENDING (not SKIP)"
fi

# CK-06 violating scenario (Extension Protocol rule 4): a pending spec must not
# mask a real failure batched alongside it — document still FAILs, exit 1,
# coverage buckets stay disjoint (checked = failed + pending here).
cat > "$FEAT_DIR/ck06-failing.md" <<'EOF'
---
kind: constraint
id: ck06-failing
from_patterns: ["pattern:ball-possession"]
confidence: "★★"
check:
  method: grep
  target: "client/src"
  pattern: "extends"
  expect: absent
---
# T
## Rule
No extends (deliberately violated by fixture code).
EOF
rc=0; CK06_MIX=$(python3 "$CHECK" --json "$FEAT_DIR/ck06-pending.md" "$FEAT_DIR/ck06-failing.md" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] \
   && echo "$CK06_MIX" | grep -q '"status": "fail"' \
   && echo "$CK06_MIX" | grep -q '"pending": 1' \
   && echo "$CK06_MIX" | grep -q '"failed": 1'; then
  report PASS "ck06: pending never masks a batched FAIL (status fail, exit 1, buckets disjoint)"
else
  report FAIL "ck06: pending never masks a batched FAIL (status fail, exit 1, buckets disjoint)" "exit=$rc"
fi

unset ARCHWRIGHT_PROJECT_ROOT

echo ""
echo "=== Baseline: aw/v1 Fingerprints + Suppression + Ratchet (CK-07/CK-08) ==="
# Own tiny target tree so line shifts never touch shared fixtures. Explicit
# --baseline throughout for hermeticity (auto-discovery walk-up could catch a
# stray file under /tmp).
CK07_TREE="$FEAT_DIR/ck07-tree"
mkdir -p "$CK07_TREE/src"
printf 'import direct_db\nx = 1\n' > "$CK07_TREE/src/app.py"
CK07_BL="$FEAT_DIR/ck07-baseline.json"
cat > "$FEAT_DIR/ck07-star2.md" <<'EOF'
---
kind: constraint
id: ck07-star2
from_patterns: ["pattern:ball-possession"]
confidence: "★★"
check:
  method: grep
  target: "src"
  pattern: "import direct_db"
  expect: absent
---
# T
## Rule
No direct db imports.
EOF

# CK-07a: violations carry aw/v1 fingerprints aligned with evidence
rc=0; CK07_OUT1=$(python3 "$CHECK" --json --target "$CK07_TREE" "$FEAT_DIR/ck07-star2.md" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] \
   && echo "$CK07_OUT1" | grep -q '"fingerprint_algo": "aw/v1"' \
   && echo "$CK07_OUT1" | grep -q '"fingerprints"'; then
  report PASS "ck07: violations carry aw/v1 fingerprints"
else
  report FAIL "ck07: violations carry aw/v1 fingerprints" "exit=$rc"
fi

# CK-07b: fingerprints stable under line shift (content moves, identity doesn't)
FP1=$(echo "$CK07_OUT1" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sorted(fp for v in d['violations'] for fp in v['fingerprints']))" 2>/dev/null) || FP1="extract-failed-1"
printf '# comment shifts everything down\n\nimport direct_db\nx = 1\n' > "$CK07_TREE/src/app.py"
CK07_OUT2=$(python3 "$CHECK" --json --target "$CK07_TREE" "$FEAT_DIR/ck07-star2.md" 2>&1) || true
FP2=$(echo "$CK07_OUT2" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sorted(fp for v in d['violations'] for fp in v['fingerprints']))" 2>/dev/null) || FP2="extract-failed-2"
if [ "$FP1" = "$FP2" ] && [ "$FP1" != "extract-failed-1" ]; then
  report PASS "ck07: fingerprints stable under line shift (line numbers never hashed)"
else
  report FAIL "ck07: fingerprints stable under line shift (line numbers never hashed)" "$FP1 vs $FP2"
fi

# CK-07c: baselined violation suppressed — exit 0, warning severity, ★★ keeps escalate
echo "$CK07_OUT2" | python3 -c "
import json, sys
d = json.load(sys.stdin)
entries = [{'fingerprint': fp, 'algo': 'aw/v1', 'spec_id': v['spec_id'], 'note': 'test debt'}
           for v in d['violations'] for fp in v['fingerprints']]
print(json.dumps({'entries': entries}))
" > "$CK07_BL"
rc=0; CK07_SUP=$(python3 "$CHECK" --json --target "$CK07_TREE" --baseline "$CK07_BL" "$FEAT_DIR/ck07-star2.md" 2>&1) || rc=$?
if [ "$rc" -eq 0 ] \
   && echo "$CK07_SUP" | grep -q '"status": "pass"' \
   && echo "$CK07_SUP" | grep -q '"baselined": true' \
   && echo "$CK07_SUP" | grep -q '"severity": "warning"' \
   && echo "$CK07_SUP" | grep -q '"escalate": true' \
   && echo "$CK07_SUP" | grep -q '"remaining_delta": 0'; then
  report PASS "ck07: baselined violation = warning + exit 0; ★★ keeps escalate (no C2 back door)"
else
  report FAIL "ck07: baselined violation = warning + exit 0; ★★ keeps escalate (no C2 back door)" "exit=$rc"
fi

# CK-07d violating scenario (Extension Protocol rule 4): a NEW match alongside
# baselined debt must FAIL — all-or-nothing suppression per violation.
printf '# comment shifts everything down\n\nimport direct_db\nimport direct_db as second_new_debt\nx = 1\n' > "$CK07_TREE/src/app.py"
rc=0; CK07_NEW=$(python3 "$CHECK" --json --target "$CK07_TREE" --baseline "$CK07_BL" "$FEAT_DIR/ck07-star2.md" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] \
   && echo "$CK07_NEW" | grep -q '"status": "fail"' \
   && echo "$CK07_NEW" | grep -q '"baselined": false' \
   && echo "$CK07_NEW" | grep -q '"remaining_delta": 1'; then
  report PASS "ck07: new violation is never masked by the baseline (fail, exit 1)"
else
  report FAIL "ck07: new violation is never masked by the baseline (fail, exit 1)" "exit=$rc"
fi

# CK-08a ratchet: entries whose violations no longer reproduce are removed;
# the new violation is NOT added (count only ever decreases).
printf 'x = 1\nimport direct_db as second_new_debt\n' > "$CK07_TREE/src/app.py"
rc=0; python3 "$CHECK" --json --target "$CK07_TREE" --baseline "$CK07_BL" --update-baseline "$FEAT_DIR/ck07-star2.md" >/dev/null 2>&1 || rc=$?
BL_COUNT=$(python3 -c "import json; print(len(json.load(open('$CK07_BL'))['entries']))" 2>/dev/null) || BL_COUNT="?"
if [ "$rc" -eq 1 ] && [ "$BL_COUNT" = "0" ]; then
  report PASS "ck08: ratchet removes resolved entries, never adds new ones (exit still 1)"
else
  report FAIL "ck08: ratchet removes resolved entries, never adds new ones (exit still 1)" "exit=$rc entries=$BL_COUNT"
fi

# CK-08b: --update-baseline refuses on an errored run (proves nothing about absence)
echo '{"entries": [{"fingerprint": "deadbeefdeadbeef_0", "algo": "aw/v1"}]}' > "$CK07_BL"
rc=0; python3 "$CHECK" --json --target "$CK07_TREE" --baseline "$CK07_BL" --update-baseline "$FEAT_DIR/bad-expect.md" >/dev/null 2>&1 || rc=$?
BL_COUNT=$(python3 -c "import json; print(len(json.load(open('$CK07_BL'))['entries']))" 2>/dev/null) || BL_COUNT="?"
if [ "$rc" -eq 2 ] && [ "$BL_COUNT" = "1" ]; then
  report PASS "ck08: errored run refuses --update-baseline, file untouched (exit 2)"
else
  report FAIL "ck08: errored run refuses --update-baseline, file untouched (exit 2)" "exit=$rc entries=$BL_COUNT"
fi

# CK-08c: explicit --baseline pointing nowhere = tool error, not silent no-suppression
rc=0; python3 "$CHECK" --json --baseline "$FEAT_DIR/does-not-exist.json" "$FEAT_DIR/ck07-star2.md" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 2 ]; then
  report PASS "ck07: explicit missing baseline = tool error (exit 2)"
else
  report FAIL "ck07: explicit missing baseline = tool error (exit 2)" "exit=$rc"
fi

# CK-07e: behavior violations are NEVER suppressible — design violations, not
# adoptable debt. Baseline the unguarded fixture's fingerprints; check must
# still FAIL. Alloy-gated like the guard-conformance section.
if [ -f "$GC_JAR" ] && command -v java >/dev/null 2>&1 && [ -f "$GUARD_SPECS/zone-progress-unguarded.yaml" ]; then
  BEH_OUT=$(python3 "$CHECK" --json "$GUARD_SPECS/zone-progress-unguarded.yaml" 2>&1) || true
  echo "$BEH_OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
entries = [{'fingerprint': fp, 'algo': 'aw/v1'} for v in d['violations'] for fp in v['fingerprints']]
print(json.dumps({'entries': entries}))
" > "$CK07_BL"
  rc=0; BEH_SUP=$(python3 "$CHECK" --json --baseline "$CK07_BL" "$GUARD_SPECS/zone-progress-unguarded.yaml" 2>&1) || rc=$?
  if [ "$rc" -eq 1 ] && echo "$BEH_SUP" | grep -q '"baselined": false'; then
    report PASS "ck07: behavior violations never suppressed by baseline (still fail)"
  else
    report FAIL "ck07: behavior violations never suppressed by baseline (still fail)" "exit=$rc"
  fi
else
  report SKIP "ck07: behavior never-suppressed (alloy jar or java unavailable)"
fi

echo ""
echo "=== Evidence Ledger (ADR 0009 / ticket 017) ==="
# Tool-owned confidence evidence events. Activation by existence (or explicit
# --evidence); demotion-candidate on ★★/★ FAIL (never baselined/—);
# promotion-candidate on pass streak or deeper-tier (bounded) pass; dedup on
# identical re-observation; malformed ledger = exit 2.
ADR9_TREE="$FEAT_DIR/adr9-tree"
mkdir -p "$ADR9_TREE/src"
printf 'import direct_db\nx = 1\n' > "$ADR9_TREE/src/app.py"
ADR9_EV="$FEAT_DIR/adr9-evidence.json"
cat > "$FEAT_DIR/adr9-star2.md" <<'EOF'
---
kind: constraint
id: adr9-star2
from_patterns: ["pattern:ball-possession"]
confidence: "★★"
check:
  method: grep
  target: "src"
  pattern: "import direct_db"
  expect: absent
---
# T
## Rule
No direct db imports.
EOF

# ADR9-a: no ledger file + no flag → inert (nothing created, no doc key)
rc=0; ADR9_OUT=$(python3 "$CHECK" --json --target "$ADR9_TREE" "$FEAT_DIR/adr9-star2.md" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] \
   && ! echo "$ADR9_OUT" | grep -q '"evidence_ledger"' \
   && [ ! -f "$ADR9_TREE/.archwright-evidence.json" ]; then
  report PASS "adr9: no ledger + no flag = inert (nothing created)"
else
  report FAIL "adr9: no ledger + no flag = inert (nothing created)" "exit=$rc"
fi

# ADR9-b: --evidence + ★★ FAIL → demotion-candidate with aw/v1 fingerprints
echo '{}' > "$ADR9_EV"
rc=0; ADR9_OUT=$(python3 "$CHECK" --json --target "$ADR9_TREE" --evidence "$ADR9_EV" "$FEAT_DIR/adr9-star2.md" 2>&1) || rc=$?
ADR9_CHECK=$(python3 -c "
import json
L = json.load(open('$ADR9_EV'))
e = L['events'][0]
ok = (e['event'] == 'demotion-candidate' and e['key'] == 'constraint:adr9-star2'
      and e['confidence'] == '★★' and e['fingerprints'] and e['at'])
print('OK' if ok and len(L['events']) == 1 else 'BAD: ' + json.dumps(e))
" 2>&1) || ADR9_CHECK="extract-failed"
if [ "$rc" -eq 1 ] && [ "$ADR9_CHECK" = "OK" ] \
   && echo "$ADR9_OUT" | grep -q '"events_appended": 1'; then
  report PASS "adr9: ★★ FAIL appends demotion-candidate with fingerprints"
else
  report FAIL "adr9: ★★ FAIL appends demotion-candidate with fingerprints" "exit=$rc $ADR9_CHECK"
fi

# ADR9-c: identical re-run appends nothing (dedup)
rc=0; ADR9_OUT=$(python3 "$CHECK" --json --target "$ADR9_TREE" --evidence "$ADR9_EV" "$FEAT_DIR/adr9-star2.md" 2>&1) || rc=$?
ADR9_N=$(python3 -c "import json; print(len(json.load(open('$ADR9_EV'))['events']))" 2>/dev/null) || ADR9_N="?"
if echo "$ADR9_OUT" | grep -q '"events_appended": 0' && [ "$ADR9_N" = "1" ]; then
  report PASS "adr9: identical re-observation deduped (1 event total)"
else
  report FAIL "adr9: identical re-observation deduped (1 event total)" "events=$ADR9_N"
fi

# ADR9-d: baselined violation emits NO event (the baseline IS the adjudication)
echo "$ADR9_OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
entries = [{'fingerprint': fp, 'algo': 'aw/v1'} for v in d['violations'] for fp in v['fingerprints']]
print(json.dumps({'entries': entries}))
" > "$FEAT_DIR/adr9-baseline.json"
echo '{}' > "$ADR9_EV"
rc=0; python3 "$CHECK" --json --target "$ADR9_TREE" --baseline "$FEAT_DIR/adr9-baseline.json" --evidence "$ADR9_EV" "$FEAT_DIR/adr9-star2.md" >/dev/null 2>&1 || rc=$?
ADR9_N=$(python3 -c "import json; print(len(json.load(open('$ADR9_EV'))['events']))" 2>/dev/null) || ADR9_N="?"
if [ "$rc" -eq 0 ] && [ "$ADR9_N" = "0" ]; then
  report PASS "adr9: baselined violation emits no demotion event"
else
  report FAIL "adr9: baselined violation emits no demotion event" "exit=$rc events=$ADR9_N"
fi

# ADR9-e: '—' confidence FAIL emits nothing (no confidence claim to demote)
sed 's/adr9-star2/adr9-dash/; s/★★/—/' "$FEAT_DIR/adr9-star2.md" > "$FEAT_DIR/adr9-dash.md"
echo '{}' > "$ADR9_EV"
rc=0; python3 "$CHECK" --json --target "$ADR9_TREE" --evidence "$ADR9_EV" "$FEAT_DIR/adr9-dash.md" >/dev/null 2>&1 || rc=$?
ADR9_N=$(python3 -c "import json; print(len(json.load(open('$ADR9_EV'))['events']))" 2>/dev/null) || ADR9_N="?"
if [ "$rc" -eq 1 ] && [ "$ADR9_N" = "0" ]; then
  report PASS "adr9: — confidence FAIL emits no event"
else
  report FAIL "adr9: — confidence FAIL emits no event" "exit=$rc events=$ADR9_N"
fi

# ADR9-f: pass streak (config.promotion_streak) → exactly ONE promotion-candidate;
# a FAIL resets the streak and lands a ★ demotion-candidate.
cat > "$FEAT_DIR/adr9-star1.md" <<'EOF'
---
kind: constraint
id: adr9-star1
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: "src"
  pattern: "import forbidden_thing"
  expect: absent
---
# T
## Rule
No forbidden imports.
EOF
printf '{"config": {"promotion_streak": 3}}' > "$ADR9_EV"
for _i in 1 2 3 4; do
  python3 "$CHECK" --json --target "$ADR9_TREE" --evidence "$ADR9_EV" "$FEAT_DIR/adr9-star1.md" >/dev/null 2>&1 || true
done
ADR9_CHECK=$(python3 -c "
import json
L = json.load(open('$ADR9_EV'))
promos = [e for e in L['events'] if e['event'] == 'promotion-candidate']
ok = (len(promos) == 1 and promos[0]['reason'] == 'pass-streak-3'
      and promos[0]['confidence'] == '★'
      and L['streaks']['constraint:adr9-star1#adr9-star1'] == 4)
print('OK' if ok else 'BAD: ' + json.dumps(L))
" 2>&1) || ADR9_CHECK="extract-failed"
if [ "$ADR9_CHECK" = "OK" ]; then
  report PASS "adr9: pass streak emits one promotion-candidate (config threshold honored)"
else
  report FAIL "adr9: pass streak emits one promotion-candidate (config threshold honored)" "$ADR9_CHECK"
fi

printf 'import direct_db\nimport forbidden_thing\n' > "$ADR9_TREE/src/app.py"
rc=0; python3 "$CHECK" --json --target "$ADR9_TREE" --evidence "$ADR9_EV" "$FEAT_DIR/adr9-star1.md" >/dev/null 2>&1 || rc=$?
ADR9_CHECK=$(python3 -c "
import json
L = json.load(open('$ADR9_EV'))
demos = [e for e in L['events'] if e['event'] == 'demotion-candidate']
ok = ('constraint:adr9-star1#adr9-star1' not in L['streaks']
      and len(demos) == 1 and demos[0]['confidence'] == '★')
print('OK' if ok else 'BAD: ' + json.dumps(L))
" 2>&1) || ADR9_CHECK="extract-failed"
if [ "$rc" -eq 1 ] && [ "$ADR9_CHECK" = "OK" ]; then
  report PASS "adr9: FAIL resets streak and appends ★ demotion-candidate"
else
  report FAIL "adr9: FAIL resets streak and appends ★ demotion-candidate" "exit=$rc $ADR9_CHECK"
fi
printf 'import direct_db\nx = 1\n' > "$ADR9_TREE/src/app.py"

# ADR9-g violating scenario (Extension Protocol rule 4): malformed ledger = exit 2
echo 'not json{' > "$FEAT_DIR/adr9-bad.json"
rc=0; python3 "$CHECK" --json --target "$ADR9_TREE" --evidence "$FEAT_DIR/adr9-bad.json" "$FEAT_DIR/adr9-star1.md" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 2 ]; then
  report PASS "adr9: malformed ledger = tool error (exit 2)"
else
  report FAIL "adr9: malformed ledger = tool error (exit 2)" "exit=$rc"
fi

# ADR9-h: trace mode — ★★ invariant FAIL appends demotion-candidate with
# fingerprints: [] (aw/v1 needs static path+content; CK-07 scope cut upheld);
# a passing trace credits streaks only for CHECKED (non-skipped) ★/— invariants.
ADR9_TS="$TOOLS/../tests/fixtures/trace-strict"
echo '{}' > "$ADR9_EV"
rc=0; python3 "$CHECK" --trace "$ADR9_TS/trace-strict-conformance.yaml" "$ADR9_TS/violating.trace.json" --json --evidence "$ADR9_EV" >/dev/null 2>&1 || rc=$?
ADR9_CHECK=$(python3 -c "
import json
L = json.load(open('$ADR9_EV'))
e = L['events'][0]
ok = (len(L['events']) == 1 and e['event'] == 'demotion-candidate'
      and e['key'] == 'behavior:trace-strict-conformance'
      and e['invariant'] == 'count-within-max'
      and e['confidence'] == '★★' and e['fingerprints'] == [])
print('OK' if ok else 'BAD: ' + json.dumps(L, ensure_ascii=False))
" 2>&1) || ADR9_CHECK="extract-failed"
if [ "$rc" -eq 1 ] && [ "$ADR9_CHECK" = "OK" ]; then
  report PASS "adr9: trace ★★ FAIL appends demotion-candidate, fingerprints []"
else
  report FAIL "adr9: trace ★★ FAIL appends demotion-candidate, fingerprints []" "exit=$rc $ADR9_CHECK"
fi

rc=0; python3 "$CHECK" --trace "$ADR9_TS/trace-strict-conformance.yaml" "$ADR9_TS/ok.trace.json" --json --evidence "$ADR9_EV" >/dev/null 2>&1 || rc=$?
ADR9_CHECK=$(python3 -c "
import json
L = json.load(open('$ADR9_EV'))
# count-within-max is ★★ (never promotes → no streak); opaque-* invariants SKIP → no credit
print('OK' if L['streaks'] == {} else 'BAD: ' + json.dumps(L['streaks']))
" 2>&1) || ADR9_CHECK="extract-failed"
if [ "$rc" -eq 0 ] && [ "$ADR9_CHECK" = "OK" ]; then
  report PASS "adr9: trace pass credits no streaks for ★★/skipped invariants"
else
  report FAIL "adr9: trace pass credits no streaks for ★★/skipped invariants" "exit=$rc $ADR9_CHECK"
fi

# ADR9-i (Alloy-gated): a ★ invariant passing a BOUNDED (mechanical) check is an
# immediate deeper-tier promotion-candidate.
if [ -f "$GC_JAR" ] && command -v java >/dev/null 2>&1 && [ -f "$GUARD_SPECS/zone-progress.yaml" ]; then
  sed 's/confidence: "★★"/confidence: "★"/; s/^id: .*/id: adr9-alloy-star/' "$GUARD_SPECS/zone-progress.yaml" > "$FEAT_DIR/adr9-alloy-star.yaml"
  echo '{}' > "$ADR9_EV"
  rc=0; python3 "$CHECK" --json --evidence "$ADR9_EV" "$FEAT_DIR/adr9-alloy-star.yaml" >/dev/null 2>&1 || rc=$?
  ADR9_CHECK=$(python3 -c "
import json
L = json.load(open('$ADR9_EV'))
promos = [e for e in L['events'] if e['event'] == 'promotion-candidate'
          and 'deeper-check' in (e.get('reason') or '')]
ok = promos and all(e['confidence'] == '★' for e in promos)
print('OK' if ok else 'BAD: ' + json.dumps(L, ensure_ascii=False))
" 2>&1) || ADR9_CHECK="extract-failed"
  if [ "$rc" -eq 0 ] && [ "$ADR9_CHECK" = "OK" ]; then
    report PASS "adr9: ★ invariant passing bounded check = deeper-tier promotion-candidate"
  else
    report FAIL "adr9: ★ invariant passing bounded check = deeper-tier promotion-candidate" "exit=$rc $ADR9_CHECK"
  fi
else
  report SKIP "adr9: deeper-tier promotion (alloy jar or java unavailable)"
fi

echo ""
echo "=== Changed-Only Scope Selection (CK-19) ==="
# --changed-only [--base <ref>]: only specs affected by the git diff run.
# Affected = spec file changed OR changed/untracked file under check.target;
# git failures = exit 2 (never an empty-diff false pass).
if command -v git >/dev/null 2>&1; then
  CK19_TREE="$FEAT_DIR/ck19-tree"
  mkdir -p "$CK19_TREE/src" "$CK19_TREE/lib" "$CK19_TREE/design/specs"
  printf 'x = 1\n' > "$CK19_TREE/src/app.py"
  printf 'y = 1\n' > "$CK19_TREE/lib/util.py"
  cat > "$CK19_TREE/design/specs/watch-src.md" <<'EOF'
---
kind: constraint
id: watch-src
from_patterns: ["pattern:ball-possession"]
confidence: "★"
check:
  method: grep
  target: "src"
  pattern: "import direct_db"
  expect: absent
---
# T
## Rule
No direct db imports in src.
EOF
  sed 's/watch-src/watch-lib/; s|target: "src"|target: "lib"|' "$CK19_TREE/design/specs/watch-src.md" > "$CK19_TREE/design/specs/watch-lib.md"
  git -C "$CK19_TREE" init -q
  git -C "$CK19_TREE" -c user.email=t@t -c user.name=t add -A
  git -C "$CK19_TREE" -c user.email=t@t -c user.name=t commit -qm init

  # CK-19a: clean tree → 0 affected specs, exit 0, scope reports the filter
  rc=0; CK19_OUT=$(python3 "$CHECK" --static "$CK19_TREE/design/specs" --changed-only --json --target "$CK19_TREE" 2>&1) || rc=$?
  if [ "$rc" -eq 0 ] \
     && echo "$CK19_OUT" | grep -q '"changed_only": true' \
     && echo "$CK19_OUT" | grep -q '"specs_checked": 0' \
     && echo "$CK19_OUT" | grep -q '"specs_total": 2'; then
    report PASS "ck19: clean tree = 0 affected specs, pass (scope reports filter)"
  else
    report FAIL "ck19: clean tree = 0 affected specs, pass (scope reports filter)" "exit=$rc"
  fi

  # CK-19b violating scenario (Extension Protocol rule 4): an UNTRACKED
  # violating file under one target selects exactly that spec and FAILs.
  printf 'import direct_db\n' > "$CK19_TREE/src/new_file.py"
  rc=0; CK19_OUT=$(python3 "$CHECK" --static "$CK19_TREE/design/specs" --changed-only --json --target "$CK19_TREE" 2>&1) || rc=$?
  if [ "$rc" -eq 1 ] \
     && echo "$CK19_OUT" | grep -q '"status": "fail"' \
     && echo "$CK19_OUT" | grep -q '"spec_id": "watch-src"' \
     && echo "$CK19_OUT" | grep -q '"specs_checked": 1' \
     && echo "$CK19_OUT" | grep -q '"specs_unaffected": 1'; then
    report PASS "ck19: untracked violating file selects only its spec and FAILs (exit 1)"
  else
    report FAIL "ck19: untracked violating file selects only its spec and FAILs (exit 1)" "exit=$rc"
  fi
  rm "$CK19_TREE/src/new_file.py"

  # CK-19c: a changed spec file re-runs even with no code changes
  printf '\n<!-- touched -->\n' >> "$CK19_TREE/design/specs/watch-lib.md"
  rc=0; CK19_OUT=$(python3 "$CHECK" --static "$CK19_TREE/design/specs" --changed-only --json --target "$CK19_TREE" 2>&1) || rc=$?
  if [ "$rc" -eq 0 ] && echo "$CK19_OUT" | grep -q '"specs_checked": 1'; then
    report PASS "ck19: changed spec file itself re-runs"
  else
    report FAIL "ck19: changed spec file itself re-runs" "exit=$rc"
  fi

  # CK-19d: bad base ref = tool error (exit 2), never an empty false pass
  rc=0; python3 "$CHECK" --static "$CK19_TREE/design/specs" --changed-only --base no-such-ref --json --target "$CK19_TREE" >/dev/null 2>&1 || rc=$?
  if [ "$rc" -eq 2 ]; then
    report PASS "ck19: bad --base ref = tool error (exit 2)"
  else
    report FAIL "ck19: bad --base ref = tool error (exit 2)" "exit=$rc"
  fi

  # CK-19e violating scenario: --update-baseline + --changed-only refuses (exit 2)
  # and leaves the baseline untouched — a scoped run would wrongly drop entries
  # belonging to unaffected specs (they "don't reproduce" only because they
  # weren't checked).
  CK19_BL="$FEAT_DIR/ck19-baseline.json"
  echo '{"entries": [{"fingerprint": "deadbeefdeadbeef_0", "algo": "aw/v1"}]}' > "$CK19_BL"
  rc=0; python3 "$CHECK" --static "$CK19_TREE/design/specs" --changed-only --update-baseline --baseline "$CK19_BL" --json --target "$CK19_TREE" >/dev/null 2>&1 || rc=$?
  CK19_N=$(python3 -c "import json; print(len(json.load(open('$CK19_BL'))['entries']))" 2>/dev/null) || CK19_N="?"
  if [ "$rc" -eq 2 ] && [ "$CK19_N" = "1" ]; then
    report PASS "ck19: --update-baseline refuses under --changed-only, baseline untouched (exit 2)"
  else
    report FAIL "ck19: --update-baseline refuses under --changed-only, baseline untouched (exit 2)" "exit=$rc entries=$CK19_N"
  fi
else
  report SKIP "ck19: changed-only scope selection (git unavailable)"
fi

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
