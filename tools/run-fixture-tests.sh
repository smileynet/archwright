#!/usr/bin/env bash
# Run all archwright checks against the fieldball-coach fixture.
# Exit 0 if all pass (or fixture is empty), 1 if any fail.
set -euo pipefail

TOOLS="$(dirname "$0")"
FIXTURE="$TOOLS/../tests/fixtures/fieldball-coach"
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

# Windows: Cygwin/MSYS bash's /tmp and Python's tempfile.gettempdir() may diverge
# (bash → /tmp = C:\Users\...\AppData\Local\Temp via Cygwin map; Python → C:\tmp).
# Force mktemp to use Python's temp so inline `python3 -c "open('$path')"` works.
# The path must use forward slashes — backslashes in Python string literals become
# escape sequences (\U → invalid unicode escape, \A → invalid, etc.).
if [ -z "${TMPDIR:-}" ]; then
  _PY_TMP=$(python3 -c 'import tempfile, os; t=tempfile.gettempdir(); print(t.replace(os.sep, "/") if os.name=="nt" else t)' 2>/dev/null)
  if [ -n "$_PY_TMP" ] && [ -d "$_PY_TMP" ]; then
    export TMPDIR="$_PY_TMP"
  fi
fi
# Ensure all paths derived from mktemp use forward slashes (Cygwin mktemp already
# does; the guard above ensures the prefix matches Python's view of the filesystem).

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
# No-partial-set: a valid entry BEFORE an invalid one must not reach disk —
# render-all-then-write (same discipline as import-woz).
cat > "$FG_DIR/mixed.yaml" <<'EOF'
forces:
  - id: good-force
    polarity: constraint-hard
    statement: "s"
    evidence_level: L1
    provenance: [{source: "t", quote: "q"}]
  - id: bad-force
    polarity: not-a-polarity
    statement: "s"
    provenance: [{source: "t", quote: "q"}]
EOF
rc=0; python3 "$TOOLS/archwright-forces-gen.py" "$FG_DIR/mixed.yaml" -o "$FG_DIR/out3" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 2 ] && [ "$(ls "$FG_DIR/out3" 2>/dev/null | wc -l)" = "0" ]; then
  report PASS "forces-gen: invalid entry mid-list writes NO partial set (exit 2, 0 files)"
else
  report FAIL "forces-gen: invalid entry mid-list writes NO partial set (exit 2, 0 files)" "exit=$rc"
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
echo "=== Commit-Binding of Check Evidence (ticket 018) ==="
# code_state {commit, dirty} in --json output + evidence events (EDA signoff
# precedent, ADR 0009 amendment). Dedup identity unchanged; git-absent/non-repo
# = null fields with reason, never a crash. Git-gated like CK-19.
if command -v git >/dev/null 2>&1; then
  CB_TREE=$(mktemp -d)
  mkdir -p "$CB_TREE/src"
  printf 'import direct_db\n' > "$CB_TREE/src/app.py"
  cat > "$CB_TREE/cb-spec.md" <<'EOF'
---
kind: constraint
id: cb-spec
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
  git -C "$CB_TREE" init -q
  git -C "$CB_TREE" -c user.email=t@t -c user.name=t add -A
  git -C "$CB_TREE" -c user.email=t@t -c user.name=t commit -qm init
  CB_HEAD=$(git -C "$CB_TREE" rev-parse HEAD)

  # 018a: clean tree → code_state.commit == HEAD, dirty false (exit 1: real violation)
  rc=0; CB_OUT=$(python3 "$CHECK" --json --target "$CB_TREE" "$CB_TREE/cb-spec.md" 2>&1) || rc=$?
  CB_CHECK=$(echo "$CB_OUT" | python3 -c "
import json, sys
cs = json.load(sys.stdin)['code_state']
print('OK' if cs['commit'] == '$CB_HEAD' and cs['dirty'] is False else 'BAD: ' + json.dumps(cs))
" 2>&1) || CB_CHECK="extract-failed"
  if [ "$rc" -eq 1 ] && [ "$CB_CHECK" = "OK" ]; then
    report PASS "cb018: clean tree = code_state carries HEAD commit, dirty false"
  else
    report FAIL "cb018: clean tree = code_state carries HEAD commit, dirty false" "exit=$rc $CB_CHECK"
  fi

  # 018b: uncommitted change → dirty true (commit alone no longer identifies the code)
  printf '# uncommitted\n' >> "$CB_TREE/src/app.py"
  CB_OUT=$(python3 "$CHECK" --json --target "$CB_TREE" "$CB_TREE/cb-spec.md" 2>&1) || true
  CB_CHECK=$(echo "$CB_OUT" | python3 -c "
import json, sys
cs = json.load(sys.stdin)['code_state']
print('OK' if cs['dirty'] is True else 'BAD: ' + json.dumps(cs))
" 2>&1) || CB_CHECK="extract-failed"
  if [ "$CB_CHECK" = "OK" ]; then
    report PASS "cb018: dirty working tree flagged (dirty true)"
  else
    report FAIL "cb018: dirty working tree flagged (dirty true)" "$CB_CHECK"
  fi
  git -C "$CB_TREE" -c user.email=t@t -c user.name=t add -A
  git -C "$CB_TREE" -c user.email=t@t -c user.name=t commit -qm change
  CB_HEAD2=$(git -C "$CB_TREE" rev-parse HEAD)

  # 018c: evidence event stamped with code_state (commit of the checked tree).
  # The ledger file lives OUTSIDE the repo — inside it would dirty the tree.
  CB_EV=$(mktemp)
  echo '{}' > "$CB_EV"
  rc=0; python3 "$CHECK" --json --target "$CB_TREE" --evidence "$CB_EV" "$CB_TREE/cb-spec.md" >/dev/null 2>&1 || rc=$?
  CB_CHECK=$(python3 -c "
import json
L = json.load(open('$CB_EV'))
e = L['events'][0]
cs = e.get('code_state') or {}
ok = (e['event'] == 'demotion-candidate' and cs.get('commit') == '$CB_HEAD2'
      and cs.get('dirty') is False)
print('OK' if ok and len(L['events']) == 1 else 'BAD: ' + json.dumps(e))
" 2>&1) || CB_CHECK="extract-failed"
  if [ "$rc" -eq 1 ] && [ "$CB_CHECK" = "OK" ]; then
    report PASS "cb018: evidence event carries code_state (commit + dirty false)"
  else
    report FAIL "cb018: evidence event carries code_state (commit + dirty false)" "exit=$rc $CB_CHECK"
  fi

  # 018d: dedup identity UNCHANGED — identical re-observation at a NEW commit
  # appends nothing (the original binding stands; staleness is judged by consumers)
  git -C "$CB_TREE" -c user.email=t@t -c user.name=t commit -q --allow-empty -m bump
  rc=0; CB_OUT=$(python3 "$CHECK" --json --target "$CB_TREE" --evidence "$CB_EV" "$CB_TREE/cb-spec.md" 2>&1) || rc=$?
  CB_N=$(python3 -c "import json; print(len(json.load(open('$CB_EV'))['events']))" 2>/dev/null) || CB_N="?"
  if echo "$CB_OUT" | grep -q '"events_appended": 0' && [ "$CB_N" = "1" ]; then
    report PASS "cb018: identical re-observation at a new commit appends nothing (dedup unchanged)"
  else
    report FAIL "cb018: identical re-observation at a new commit appends nothing (dedup unchanged)" "events=$CB_N"
  fi
  rm -rf "$CB_TREE" "$CB_EV"

  # 018e: non-repo target → commit/dirty null with reason, run otherwise unchanged
  CB_NOGIT=$(mktemp -d)
  mkdir -p "$CB_NOGIT/src"
  printf 'x = 1\n' > "$CB_NOGIT/src/app.py"
  cat > "$CB_NOGIT/cb-clean.md" <<'EOF'
---
kind: constraint
id: cb-clean
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
No direct db imports.
EOF
  rc=0; CB_OUT=$(python3 "$CHECK" --json --target "$CB_NOGIT" "$CB_NOGIT/cb-clean.md" 2>&1) || rc=$?
  CB_CHECK=$(echo "$CB_OUT" | python3 -c "
import json, sys
cs = json.load(sys.stdin)['code_state']
ok = cs['commit'] is None and cs['dirty'] is None and cs.get('reason')
print('OK' if ok else 'BAD: ' + json.dumps(cs))
" 2>&1) || CB_CHECK="extract-failed"
  if [ "$rc" -eq 0 ] && [ "$CB_CHECK" = "OK" ]; then
    report PASS "cb018: non-repo target = null code_state with reason, never a crash (exit 0)"
  else
    report FAIL "cb018: non-repo target = null code_state with reason, never a crash (exit 0)" "exit=$rc $CB_CHECK"
  fi
  rm -rf "$CB_NOGIT"

  # 018f: trace mode --json carries code_state too
  CB_OUT=$(python3 "$CHECK" --trace "$TOOLS/../tests/fixtures/trace-strict/trace-strict-conformance.yaml" "$TOOLS/../tests/fixtures/trace-strict/ok.trace.json" --json 2>&1) || true
  if echo "$CB_OUT" | grep -q '"code_state"'; then
    report PASS "cb018: trace-mode CK-03 document carries code_state"
  else
    report FAIL "cb018: trace-mode CK-03 document carries code_state"
  fi
else
  report SKIP "cb018: commit-binding (git unavailable)"
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

# Invariant-description WARN (ticket 038 schema nudge): behavior invariants
# without a plain-language description WARN (never fail); described ones don't.
ID_DIR=$(mktemp -d)
cat > "$ID_DIR/inv-desc.yaml" <<'EOF'
kind: behavior
id: inv-desc-probe
from_patterns: ["pattern:x"]
protects_experience: "test"
initial: a
states: [a]
invariants:
  - id: bare-inv
    type: state
    predicate: "a"
  - id: described-inv
    type: state
    predicate: "a"
    description: "plain words a cold reader can follow"
EOF
ID_OUT=""; rc=0; ID_OUT=$(python3 "$VALIDATE" "$ID_DIR/inv-desc.yaml" 2>&1) || rc=$?
if [ "$rc" -eq 0 ] && echo "$ID_OUT" | grep -q "invariant 'bare-inv' has no 'description'" \
   && ! echo "$ID_OUT" | grep -q "invariant 'described-inv'"; then
  report PASS "validate: behavior invariant without description WARNs (only the bare one), exit 0"
else
  report FAIL "validate: behavior invariant without description WARNs (only the bare one), exit 0" "exit=$rc"
fi
rm -rf "$ID_DIR"

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
echo "=== Discovery Schema + Conservation (ticket 026) ==="
# kind: discovery seam artifacts (ADR 0011, grill Q6): frontmatter schema +
# conservation citation-graph. Golden corpus per Extension Protocol rule 4 —
# passing corpus + violating fixtures for BOTH conservation directions, the
# schema, and citation resolution. Fixture: tests/fixtures/discovery/.
DISC="$TOOLS/../tests/fixtures/discovery"
rc=0; python3 "$VALIDATE" "$DISC"/passing/design/discovery/ui/*.md >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  report PASS "discovery: passing corpus schema-valid (design-system + wireframe + model-seed)"
else
  report FAIL "discovery: passing corpus schema-valid (design-system + wireframe + model-seed)" "exit=$rc"
fi
rc=0; python3 "$VALIDATE" --links "$DISC/passing/design" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  report PASS "discovery: passing corpus conserves (SUPERSEDES excluded, deferral honored, links resolve)"
else
  report FAIL "discovery: passing corpus conserves (SUPERSEDES excluded, deferral honored, links resolve)" "exit=$rc"
fi
# Violating: orphan output — approved artifact, Hands-To element without a citation
rc=0; DISC_OUT=$(python3 "$VALIDATE" "$DISC/violating/orphan-output/wf-orphan.md" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] && echo "$DISC_OUT" | grep -q "nothing invented"; then
  report PASS "discovery: orphan output FAILs approved artifact (nothing invented)"
else
  report FAIL "discovery: orphan output FAILs approved artifact (nothing invented)" "exit=$rc"
fi
# Status gating: the SAME orphan as proposed = warning only, exit 0
DISC_TMP=$(mktemp -d)
sed 's/^status: approved/status: proposed/' "$DISC/violating/orphan-output/wf-orphan.md" > "$DISC_TMP/wf-orphan.md"
rc=0; DISC_OUT=$(python3 "$VALIDATE" "$DISC_TMP/wf-orphan.md" 2>&1) || rc=$?
if [ "$rc" -eq 0 ] && echo "$DISC_OUT" | grep -q "WARN: conservation"; then
  report PASS "discovery: same orphan as proposed = WARN only, exit 0 (approval is the gate)"
else
  report FAIL "discovery: same orphan as proposed = WARN only, exit 0 (approval is the gate)" "exit=$rc"
fi
rm -rf "$DISC_TMP"
# Violating: unaccounted input — active entry neither consumed nor deferred (--links)
rc=0; DISC_OUT=$(python3 "$VALIDATE" --links "$DISC/violating/unaccounted-input/design" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] && echo "$DISC_OUT" | grep -q "nothing lost"; then
  report PASS "discovery: unaccounted active entry FAILs --links (nothing lost)"
else
  report FAIL "discovery: unaccounted active entry FAILs --links (nothing lost)" "exit=$rc"
fi
# Violating: illegal status value
rc=0; DISC_OUT=$(python3 "$VALIDATE" "$DISC/violating/illegal-status/wf-bad-status.md" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] && echo "$DISC_OUT" | grep -q "invalid status"; then
  report PASS "discovery: illegal status value rejected"
else
  report FAIL "discovery: illegal status value rejected" "exit=$rc"
fi
# Violating: citation to a nonexistent ledger entry — must FAIL even with no
# ledger anywhere in the tree (the vacuous-pass guard)
rc=0; DISC_OUT=$(python3 "$VALIDATE" --links "$DISC/violating/broken-citation/design" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] && echo "$DISC_OUT" | grep -q "does not resolve (no such ledger entry)"; then
  report PASS "discovery: citation to nonexistent entry FAILs (no vacuous pass without a ledger)"
else
  report FAIL "discovery: citation to nonexistent entry FAILs (no vacuous pass without a ledger)" "exit=$rc"
fi
# Ledger entry structure: bad origin/category/duplicate anchor all rejected
DISC_TMP=$(mktemp -d)
cat > "$DISC_TMP/wf-bad-entries.md" <<'EOF'
---
kind: discovery
id: wf-bad-entries
status: proposed
---
# T
## Decisions
### D001 — Bad enums
- **Category:** vibes
- **Origin:** telepathy
- **Decision:** x
- **Rationale:** "x"
- **Alternatives:** x
### D001 — Duplicate anchor
- **Category:** structure
- **Origin:** user
- **Decision:** y
- **Rationale:** "y"
- **Alternatives:** y
EOF
rc=0; DISC_OUT=$(python3 "$VALIDATE" "$DISC_TMP/wf-bad-entries.md" 2>&1) || rc=$?
if [ "$rc" -eq 1 ] \
   && echo "$DISC_OUT" | grep -q "invalid origin" \
   && echo "$DISC_OUT" | grep -q "invalid category" \
   && echo "$DISC_OUT" | grep -q "duplicate ledger entry"; then
  report PASS "discovery: ledger entry structure enforced (origin, category enum, duplicate anchor)"
else
  report FAIL "discovery: ledger entry structure enforced (origin, category enum, duplicate anchor)" "exit=$rc"
fi
rm -rf "$DISC_TMP"

echo ""
echo "=== WoZ Import Conformance (ticket 025) ==="
# archwright-import-woz.py: woz-session/v1 JSON → discovery artifact. Golden
# corpus per Extension Protocol rule 4: passing minimal export + violating
# cases (wrong format version, unknown category) that FAIL loudly with no
# partial output. Fixture: tests/fixtures/woz-import/.
WOZ_TOOL="$TOOLS/archwright-import-woz.py"
WOZ_FIX="$TOOLS/../tests/fixtures/woz-import"
WOZ_TMP=$(mktemp -d)
WOZ_ART="$WOZ_TMP/design/discovery/woz/woz-mini-quest-2026-07-19.md"
rc=0; python3 "$WOZ_TOOL" "$WOZ_FIX/mini-export.json" -o "$WOZ_TMP/design" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ] && python3 "$VALIDATE" "$WOZ_ART" >/dev/null 2>&1; then
  report PASS "woz-import: mini export converts to a schema-valid discovery artifact"
else
  report FAIL "woz-import: mini export converts to a schema-valid discovery artifact" "exit=$rc"
fi
# Conservation semantics: active entries (D001/D003/D004) warn as unconsumed
# (status proposed), the superseded entry (D002) is excluded, and fenced
# sim-log D-mentions never count as consumption.
rc=0; WOZ_OUT=$(python3 "$VALIDATE" --links "$WOZ_TMP/design" 2>&1) || rc=$?
if [ "$rc" -eq 0 ] \
   && echo "$WOZ_OUT" | grep -q "D001' is neither consumed" \
   && echo "$WOZ_OUT" | grep -q "D004' is neither consumed" \
   && ! echo "$WOZ_OUT" | grep -q "D002'"; then
  report PASS "woz-import: SUPERSEDES excluded from conservation; fenced transcript mentions never consume"
else
  report FAIL "woz-import: SUPERSEDES excluded from conservation; fenced transcript mentions never consume" "exit=$rc"
fi
# Category mapping: woz 'aesthetic' → core 'experience'; no woz-only category survives
if grep -q '\*\*Category:\*\* experience' "$WOZ_ART" 2>/dev/null \
   && ! grep -q '\*\*Category:\*\* aesthetic' "$WOZ_ART" 2>/dev/null; then
  report PASS "woz-import: category mapping aesthetic → experience (consumer-side, grill Q2)"
else
  report FAIL "woz-import: category mapping aesthetic → experience (consumer-side, grill Q2)"
fi
# Violating: unknown format version = exit 1, no output written
rc=0; python3 "$WOZ_TOOL" "$WOZ_FIX/wrong-format.json" -o "$WOZ_TMP/d2" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 1 ] && [ ! -d "$WOZ_TMP/d2" ]; then
  report PASS "woz-import: unknown format version = exit 1, no partial output"
else
  report FAIL "woz-import: unknown format version = exit 1, no partial output" "exit=$rc"
fi
# Violating: unknown category = exit 1 (contract drift surfaces loudly)
rc=0; python3 "$WOZ_TOOL" "$WOZ_FIX/unknown-category.json" -o "$WOZ_TMP/d2" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 1 ] && [ ! -d "$WOZ_TMP/d2" ]; then
  report PASS "woz-import: unknown category = exit 1 (contract drift, no partial output)"
else
  report FAIL "woz-import: unknown category = exit 1 (contract drift, no partial output)" "exit=$rc"
fi
# Idempotent SUPERSEDES prepend: wizard_of_oz's canonical exports (salvage-run)
# embed the marker in decision text; the importer must not double it, and must
# still prepend when absent (mini-export path above proves that side). The
# naive unconditional prepend produced "SUPERSEDES D002. SUPERSEDES D002."
# (proven to FAIL pre-fix, 2026-07-19).
WOZ_ART3="$WOZ_TMP/d3/discovery/woz/woz-marker-quest-2026-07-19.md"
rc=0; python3 "$WOZ_TOOL" "$WOZ_FIX/embedded-marker.json" -o "$WOZ_TMP/d3" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ] \
   && grep -q 'SUPERSEDES D002\. Walking over' "$WOZ_ART3" 2>/dev/null \
   && ! grep -q 'SUPERSEDES D002\. SUPERSEDES D002\.' "$WOZ_ART3" 2>/dev/null; then
  report PASS "woz-import: embedded SUPERSEDES marker not doubled (idempotent prepend)"
else
  report FAIL "woz-import: embedded SUPERSEDES marker not doubled (idempotent prepend)" "exit=$rc"
fi
# Snapshot discipline: existing import refuses without --force (exit 2), --force refreshes
rc=0; python3 "$WOZ_TOOL" "$WOZ_FIX/mini-export.json" -o "$WOZ_TMP/design" >/dev/null 2>&1 || rc=$?
rc2=0; python3 "$WOZ_TOOL" --force "$WOZ_FIX/mini-export.json" -o "$WOZ_TMP/design" >/dev/null 2>&1 || rc2=$?
if [ "$rc" -eq 2 ] && [ "$rc2" -eq 0 ]; then
  report PASS "woz-import: existing import refuses (exit 2); --force refreshes the snapshot"
else
  report FAIL "woz-import: existing import refuses (exit 2); --force refreshes the snapshot" "refusal=$rc force=$rc2"
fi
rm -rf "$WOZ_TMP"

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
echo "=== Lifecycle Examples (ticket 028) ==="
# examples/{planned,partial,complete}: ONE toy product (Snackbox) at three
# lifecycle states. Unlike the frozen golden corpora above, these are living
# fixtures — they evolve with the methodology, and this section pins each
# state's EXPECTED check picture (incl. the partial state's deliberate FAILs,
# Extension Protocol rule 4).
EX="$TOOLS/../examples"
EX_OUT=$(mktemp)

# --- planned: full design, no code ---------------------------------------
rc=0; python3 "$VALIDATE" --links "$EX/planned/design" >/dev/null 2>&1 || rc=$?
rc2=0; python3 "$CHECK" --static "$EX/planned/design/specs" --json > "$EX_OUT" 2>/dev/null || rc2=$?
if [ "$rc" -eq 0 ] && [ "$rc2" -eq 0 ] \
   && grep -q '"pending": 3' "$EX_OUT" \
   && grep -q '"failed": 0' "$EX_OUT"; then
  report PASS "examples/planned: links resolve; static = 3 pending (target_status), 0 failed, exit 0"
else
  report FAIL "examples/planned: links resolve; static = 3 pending (target_status), 0 failed, exit 0" "links=$rc static=$rc2"
fi
EX_JAR="${ARCHWRIGHT_ALLOY_JAR:-$TOOLS/../.references/alloy6.jar}"
if [ -f "$EX_JAR" ] && command -v java >/dev/null 2>&1; then
  rc=0; python3 "$CHECK" "$EX/planned/design/specs/purchase-session.yaml" --json > "$EX_OUT" 2>/dev/null || rc=$?
  if [ "$rc" -eq 0 ] && grep -q '"status": "pass"' "$EX_OUT"; then
    report PASS "examples/planned: payment gate proven before any code (both ★★ invariants, Alloy)"
  else
    report FAIL "examples/planned: payment gate proven before any code (both ★★ invariants, Alloy)" "exit=$rc"
  fi
else
  report SKIP "examples/planned: payment gate proven before any code (alloy jar or java unavailable)"
fi

# --- partial: mixed picture — the deliberate-FAIL state -------------------
rc=0; python3 "$CHECK" --static "$EX/partial/design/specs" --json > "$EX_OUT" 2>/dev/null || rc=$?
if [ "$rc" -eq 1 ] \
   && grep -q '"remaining_delta": 2' "$EX_OUT" \
   && grep -q '"invariant": "single-balance-writer"' "$EX_OUT" \
   && grep -q '"invariant": "dispenser-isolation"' "$EX_OUT" \
   && grep -q '"pending": 1' "$EX_OUT" \
   && grep -q '"passed": 1' "$EX_OUT"; then
  report PASS "examples/partial: deliberate defect FAILs both owning specs (exit 1, remaining_delta 2)"
else
  report FAIL "examples/partial: deliberate defect FAILs both owning specs (exit 1, remaining_delta 2)" "exit=$rc"
fi
if grep -q '"baselined": true' "$EX_OUT" \
   && python3 -c "
import json,sys
d=json.load(open('$EX_OUT'))
b=[v for v in d['violations'] if v.get('baselined')]
sys.exit(0 if len(b)==1 and b[0]['invariant']=='ui-no-hardware-import'
         and b[0]['severity']=='warning' and b[0]['escalate'] is True else 1)
" 2>/dev/null; then
  report PASS "examples/partial: known debt baselined to warning, ★★ keeps escalate (CK-07)"
else
  report FAIL "examples/partial: known debt baselined to warning, ★★ keeps escalate (CK-07)"
fi
rc=0; python3 "$VALIDATE" --links "$EX/partial/design" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  report PASS "examples/partial: links resolve (design grew two specs mid-lifecycle)"
else
  report FAIL "examples/partial: links resolve (design grew two specs mid-lifecycle)" "exit=$rc"
fi

# --- complete: quiescence -------------------------------------------------
# Run static in a TMP COPY: the committed evidence ledger appends on every
# check run (activation by existence) — running in place would dirty the tree.
EX_TMP=$(mktemp -d)
cp -r "$EX/complete" "$EX_TMP/complete"
rc=0; python3 "$CHECK" --static "$EX_TMP/complete/design/specs" --json > "$EX_OUT" 2>/dev/null || rc=$?
if [ "$rc" -eq 0 ] \
   && grep -q '"passed": 5' "$EX_OUT" \
   && grep -q '"failed": 0' "$EX_OUT" \
   && grep -q '"pending": 0' "$EX_OUT"; then
  report PASS "examples/complete: quiescence — 5/5 static checks pass, pending activated by src/hardware"
else
  report FAIL "examples/complete: quiescence — 5/5 static checks pass, pending activated by src/hardware" "exit=$rc"
fi
# Ledger is live: committed snapshot holds the pass-streak promotion candidate,
# and the tmp-copy run advanced the streak past it (accumulation, not stasis).
if python3 -c "
import json,sys
snap=json.load(open('$EX/complete/design/.archwright-evidence.json'))
evs=[e for e in snap.get('events',[]) if e.get('event')=='promotion-candidate'
     and e.get('reason')=='pass-streak-5' and e.get('confidence')=='★']
after=json.load(open('$EX_TMP/complete/design/.archwright-evidence.json'))
streak=after.get('streaks',{}).get('constraint:no-dispense-outside-session#no-dispense-outside-session',0)
sys.exit(0 if len(evs)==1 and streak>5 else 1)
" 2>/dev/null; then
  report PASS "examples/complete: evidence ledger accumulating (committed promotion-candidate; streak advances on run)"
else
  report FAIL "examples/complete: evidence ledger accumulating (committed promotion-candidate; streak advances on run)"
fi
rc=0; python3 "$VALIDATE" --links "$EX/complete/design" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ] && [ ! -f "$EX/complete/.archwright-baseline.json" ]; then
  report PASS "examples/complete: links resolve; baseline gone (debt paid, ratchet emptied it)"
else
  report FAIL "examples/complete: links resolve; baseline gone (debt paid, ratchet emptied it)" "exit=$rc"
fi
rm -rf "$EX_TMP" "$EX_OUT"

echo ""
echo "=== Deploy Steering Ownership Guard (ticket 037) ==="
# deploy-skills.sh must never overwrite a steering file another project
# manages (crew-research collision, 2026-07-19). Manifest-based ownership:
# refresh what we wrote, skip-loudly what we didn't. The foreign-skip case
# is this section's REQUIRED violating scenario (Extension Protocol rule 4).
DEPLOY="$TOOLS/deploy-skills.sh"
DG_TMP=$(mktemp -d)
mkdir -p "$DG_TMP/p/.kiro/steering"
echo "FOREIGN steering content (crew-managed)" > "$DG_TMP/p/.kiro/steering/subagent-reliability.md"
DG_OUT=$(bash "$DEPLOY" --project "$DG_TMP/p" 2>&1 || true)
if echo "$DG_OUT" | grep -q "subagent-reliability.md SKIPPED" \
   && grep -q "FOREIGN steering content" "$DG_TMP/p/.kiro/steering/subagent-reliability.md"; then
  report PASS "deploy-guard: foreign steering file skipped loudly, content preserved"
else
  report FAIL "deploy-guard: foreign steering file skipped loudly, content preserved"
fi
if grep -q "archwright-conventions.md" "$DG_TMP/p/.kiro/steering/.archwright-deployed" 2>/dev/null \
   && [ -f "$DG_TMP/p/.kiro/steering/archwright-conventions.md" ]; then
  report PASS "deploy-guard: uncontested file deploys + manifest records it"
else
  report FAIL "deploy-guard: uncontested file deploys + manifest records it"
fi
# Our stale copy (manifest hash matches dest) must refresh, then rerun stays quiet-clean
echo "stale archwright copy" > "$DG_TMP/p/.kiro/steering/archwright-conventions.md"
DG_STALE=$(sha256sum "$DG_TMP/p/.kiro/steering/archwright-conventions.md" | cut -d' ' -f1)
awk -F'\t' -v h="$DG_STALE" 'BEGIN{OFS="\t"} $1=="archwright-conventions.md"{$2=h} {print}' \
  "$DG_TMP/p/.kiro/steering/.archwright-deployed" > "$DG_TMP/m" && mv "$DG_TMP/m" "$DG_TMP/p/.kiro/steering/.archwright-deployed"
bash "$DEPLOY" --project "$DG_TMP/p" >/dev/null 2>&1 || true
if ! grep -q "stale archwright copy" "$DG_TMP/p/.kiro/steering/archwright-conventions.md"; then
  report PASS "deploy-guard: our stale copy refreshes (manifest-matched overwrite)"
else
  report FAIL "deploy-guard: our stale copy refreshes (manifest-matched overwrite)"
fi
rm -rf "$DG_TMP"

echo ""
echo "=== Report Generator Conformance (ticket 041) ==="
# Extension Protocol rule 4: every checker proven on a VIOLATING case too.
RG_TMP=$(mktemp -d)
RG="$TOOLS/report/generate.py"

# Minimal canonical doc with one non-escalating violation + one skip.
cat > "$RG_TMP/check.json" <<'EOF'
{"status":"fail","scope":{"mode":"static","specs_checked":2},
 "violations":[{"spec_id":"demo-rule","spec_kind":"constraint","spec_path":"design/specs/demo-rule.md",
   "invariant":"demo-rule","confidence":"★","severity":"warning","escalate":false,
   "message":"Demo violation for conformance","evidence":["src/x.py:1:bad()"],
   "fingerprints":["abcdef0123456789_1"],"from_pattern":"pattern:p","from_force":"f",
   "suggested_route":"fix-implementation",
   "contrast_pair":{"expected":"the design says X","actual":"the code does Y"}}],
 "errors":[],"skips":[{"spec_id":"gap-rule","spec_path":"design/specs/gap-rule.md",
   "invariant":"gap-rule","reason":"backend unavailable"}],
 "coverage":{"checked":2,"passed":0,"failed":1,"skipped":1,"errors":0,"pending":0},
 "remaining_delta":1,"fingerprint_algo":"aw/v1","code_state":{"commit":"deadbeef","dirty":false}}
EOF
mkdir -p "$RG_TMP/design/models"

# Generation: needs-attention posture, bundle written.
rc=0; python3 "$RG" --check-json "$RG_TMP/check.json" --design "$RG_TMP/design" --project demo >/dev/null 2>&1 || rc=$?
if [ $rc -eq 0 ] && [ -f "$RG_TMP/design/report/report.html" ] && [ -f "$RG_TMP/design/report/REPORT.md" ] \
   && [ -f "$RG_TMP/design/report/report.json" ]; then
  report PASS "report: bundle generated (html+md+json) from a violating doc"
else
  report FAIL "report: bundle generated (html+md+json) from a violating doc" "exit=$rc"
fi
rc=0; python3 -c "
import json,sys
d=json.load(open('$RG_TMP/design/report/report.json'))
asks=d['asks']; assert asks['posture']=='needs-attention', asks['posture']
a=[x for x in asks['asks'] if x['source']['kind']=='violation'][0]
assert a['ask_type']=='approval' and a['ask_id']=='abcdef0123456789_1', a
sugg=[x for x in asks['asks'] if x['ask_type']=='suggestion']; assert sugg, 'skip did not become suggestion'
" 2>/dev/null || rc=$?
if [ $rc -eq 0 ]; then
  report PASS "report: asks derivation (violation->approval w/ fingerprint ask-id, skip->suggestion, posture)"
else
  report FAIL "report: asks derivation (violation->approval w/ fingerprint ask-id, skip->suggestion, posture)" "exit=$rc"
fi

# Escalating violation -> decision; ARCHWRIGHT_AUTO_APPROVE never touches it.
python3 - "$RG_TMP/check.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1])); d['violations'][0]['escalate']=True; d['violations'][0]['confidence']='★★'
json.dump(d, open(sys.argv[1],'w'))
EOF
rc=0; ARCHWRIGHT_AUTO_APPROVE=all python3 "$RG" --check-json "$RG_TMP/check.json" --design "$RG_TMP/design" --project demo >/dev/null 2>&1 || rc=$?
rc2=0; python3 -c "
import json
d=json.load(open('$RG_TMP/design/report/report.json'))
a=[x for x in d['asks']['asks'] if x['source']['kind']=='violation'][0]
assert a['ask_type']=='decision' and a['auto_approved']==False, a
assert d['asks']['posture']=='needs-attention'
" 2>/dev/null || rc2=$?
if [ $rc -eq 0 ] && [ $rc2 -eq 0 ]; then
  report PASS "report: escalate->decision; AUTO_APPROVE=all never auto-approves a decision (hard floor)"
else
  report FAIL "report: escalate->decision; AUTO_APPROVE=all never auto-approves a decision (hard floor)" "exit=$rc/$rc2"
fi

# Vocabulary completeness: unknown internal term = generation error (exit 2).
python3 - "$RG_TMP/check.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1])); d['violations'][0]['suggested_route']='fix-implementation'; d['violations'][0]['confidence']='☆'
json.dump(d, open(sys.argv[1],'w'))
EOF
rc=0; python3 "$RG" --check-json "$RG_TMP/check.json" --design "$RG_TMP/design" --project demo >/dev/null 2>&1 || rc=$?
if [ $rc -eq 2 ]; then
  report PASS "report: untranslated term is a generation ERROR (vocabulary completeness), exit 2"
else
  report FAIL "report: untranslated term is a generation ERROR (vocabulary completeness), exit 2" "exit=$rc"
fi

# Bundle constraints both directions: run the 3 bundle-targeting specs against
# a good bundle (pass) and a corrupted one (fail) — pending flags stripped.
python3 - "$RG_TMP/check.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1])); d['violations']=[]; d['status']='pass'
json.dump(d, open(sys.argv[1],'w'))
EOF
mkdir -p "$RG_TMP/proj/design/specs" "$RG_TMP/proj/design/report"
python3 "$RG" --check-json "$RG_TMP/check.json" --design "$RG_TMP/proj/design" --project demo >/dev/null 2>&1
for s in projections-one-way allclear-discloses-gaps violations-pin-to-diagram; do
  sed '/target_status: pending/d' "$TOOLS/../design/specs/$s.md" > "$RG_TMP/proj/design/specs/$s.md"
done
rc=0; python3 "$CHECK" --static "$RG_TMP/proj/design/specs" --target "$RG_TMP/proj" >/dev/null 2>&1 || rc=$?
if [ $rc -eq 0 ]; then
  report PASS "report: bundle constraints PASS on a good bundle (activated, no pending)"
else
  report FAIL "report: bundle constraints PASS on a good bundle (activated, no pending)" "exit=$rc"
fi
# Corrupt: strip the banner + hide the disclosure section on an all-clear page with skips.
python3 - <<EOF
from pathlib import Path
p = Path("$RG_TMP/proj/design/report")
html = p.joinpath("report.html").read_text(encoding="utf-8")
html = html.replace("generated by archwright-report — do not edit", "hand edited")
html = html.replace("WHAT ISN'T VERIFIED", "hidden").replace("couldn't be checked", "fine")
p.joinpath("report.html").write_text(html, encoding="utf-8")
md = p.joinpath("REPORT.md").read_text(encoding="utf-8")
p.joinpath("REPORT.md").write_text(md.replace("generated by archwright-report — do not edit", "x"), encoding="utf-8")
EOF
rc=0; OUT=$(python3 "$CHECK" --static "$RG_TMP/proj/design/specs" --target "$RG_TMP/proj" 2>&1) || rc=$?
if [ $rc -eq 1 ] && echo "$OUT" | grep -q "projections-one-way" && echo "$OUT" | grep -q "allclear-discloses-gaps"; then
  report PASS "report: corrupted bundle FAILs banner + disclosure constraints (non-vacuous)"
else
  report FAIL "report: corrupted bundle FAILs banner + disclosure constraints (non-vacuous)" "exit=$rc"
fi

# Reducer trace round-trip: the REAL page reducer's trace satisfies behavior:ask-lifecycle.
if command -v node >/dev/null 2>&1; then
  RT_ABS="$(cd "$TOOLS" && pwd)"
  rc=0; node -e "
const R = require('$RT_ABS/report/templates/page.js');
const a = R.newAsk('approval','off_');
['PRESENT','REROUTE','REPRESENT','RESPOND'].forEach(e => { if (!R.send(a,e)) throw new Error(e); });
const c = R.newAsk('decision','on_');
if (R.send(c,'AUTO_APPROVE')) { console.error('HARD FLOOR BREACH'); process.exit(1); }
require('fs').writeFileSync('$RG_TMP/trace.json', JSON.stringify(a.trace));
const page = R.newPage({commit:'deadbeef',dirty:false});
R.pageRecord(page,'abcdef0123456789_1',{kind:'approve-fix'});
const f = JSON.parse(R.exportResponses(page));
if (f.schema_version!==1 || !f.run || !f.responded_at || !f.responses['abcdef0123456789_1']) process.exit(1);
" 2>/dev/null || rc=$?
  rc2=0; python3 "$CHECK" --trace "$TOOLS/../design/specs/ask-lifecycle.yaml" "$RG_TMP/trace.json" >/dev/null 2>&1 || rc2=$?
  if [ $rc -eq 0 ] && [ $rc2 -eq 0 ]; then
    report PASS "report: page reducer trace validates vs ask-lifecycle; decision auto rejected; response export shape v1"
  else
    report FAIL "report: page reducer trace validates vs ask-lifecycle; decision auto rejected; response export shape v1" "exit=$rc/$rc2"
  fi
else
  report SKIP "report: page reducer trace round-trip (node unavailable)"
fi

# Quoted enum literals in trace guards (the fix this build exposed): a guard
# written as ask_type == 'approval' must evaluate, not silently fail.
rc=0; python3 -c "
import sys; sys.path.insert(0, '$TOOLS')
mod = __import__('archwright-check'.replace('-','_'))
" 2>/dev/null || rc=$?
QT_OUT=$(python3 "$CHECK" --trace "$TOOLS/../design/specs/ask-lifecycle.yaml" "$RG_TMP/trace.json" --json 2>/dev/null)
if echo "$QT_OUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d['status']=='pass' and not d.get('skips'), d
" 2>/dev/null; then
  report PASS "trace: quoted enum literals in guards evaluate (no skips, no silent guard failure)"
else
  report FAIL "trace: quoted enum literals in guards evaluate (no skips, no silent guard failure)"
fi

# exclude filtering (ticket 040): same spec passes WITH exclude, fails WITHOUT.
EX_DIR=$(mktemp -d)
mkdir -p "$EX_DIR/proj/src" "$EX_DIR/proj/tests" "$EX_DIR/specs"
echo "forbidden_call()" > "$EX_DIR/proj/tests/test_x.py"
echo "clean()" > "$EX_DIR/proj/src/main.py"
cat > "$EX_DIR/specs/with-exclude.md" <<'EOF'
---
kind: constraint
id: with-exclude
from_patterns: ["pattern:p"]
confidence: "★"
protects_experience: "test"
user_story: "test"
check:
  method: grep
  target: "."
  pattern: "forbidden_call"
  exclude: ["tests/"]
  expect: absent
---
# t
EOF
sed 's/id: with-exclude/id: without-exclude/; /exclude: \["tests\/"\]/d' "$EX_DIR/specs/with-exclude.md" > "$EX_DIR/specs/without-exclude.md"
rc1=0; python3 "$CHECK" "$EX_DIR/specs/with-exclude.md" --target "$EX_DIR/proj" >/dev/null 2>&1 || rc1=$?
rc2=0; python3 "$CHECK" "$EX_DIR/specs/without-exclude.md" --target "$EX_DIR/proj" >/dev/null 2>&1 || rc2=$?
if [ $rc1 -eq 0 ] && [ $rc2 -eq 1 ]; then
  report PASS "check: exclude filters matches (passes with, FAILS without — ticket 040, non-vacuous)"
else
  report FAIL "check: exclude filters matches (passes with, FAILS without — ticket 040, non-vacuous)" "with=$rc1 without=$rc2"
fi
rm -rf "$EX_DIR" "$RG_TMP"

# Model YAML parse errors fail --links loudly (guidance sync 2026-07-21): a
# silently-skipped broken model also disabled from_model resolution (vacuous).
MV_DIR=$(mktemp -d)
mkdir -p "$MV_DIR/design/models"
printf 'actors:\n  - id: x\n bad: {' > "$MV_DIR/design/models/broken.yaml"
rc=0; MV_OUT=$(python3 "$VALIDATE" --links "$MV_DIR/design" 2>&1) || rc=$?
if [ $rc -eq 1 ] && echo "$MV_OUT" | grep -q "model YAML parse error"; then
  report PASS "validate: broken model YAML FAILs --links loudly (never silent-skip)"
else
  report FAIL "validate: broken model YAML FAILs --links loudly (never silent-skip)" "exit=$rc"
fi
rm -rf "$MV_DIR"

echo "=== Coverage Modes (ticket 043) ==="
# Both modes shipped crashing (tuple unpack / bare-array .get) with zero suite
# coverage — the vacuous-checker class. Fixture: tests/fixtures/coverage/
# (1 bare-array filename match, 1 enveloped spec_id match, 1 deliberate gap,
# 1 orphan). Non-vacuity: the gap MUST surface as exit 1.
COV_FIX="$TOOLS/../tests/fixtures/coverage"

rc=0; TC_OUT=$(python3 "$CHECK" --trace-coverage "$COV_FIX/specs" "$COV_FIX/traces" 2>&1) || rc=$?
if [ $rc -eq 1 ] && echo "$TC_OUT" | grep -q "❌ crash recovery" && echo "$TC_OUT" | grep -q "✅ happy path"; then
  report PASS "trace-coverage: bare-array filename match + gap reported as exit 1 (non-vacuous)"
else
  report FAIL "trace-coverage: bare-array filename match + gap reported as exit 1 (non-vacuous)" "exit=$rc"
fi

if echo "$TC_OUT" | grep -q "✅ timeout" && echo "$TC_OUT" | grep -q "stray.trace"; then
  report PASS "trace-coverage: enveloped spec_id association + orphan trace surfaced"
else
  report FAIL "trace-coverage: enveloped spec_id association + orphan trace surfaced" "$TC_OUT"
fi

rc=0; TC_JSON=$(python3 "$CHECK" --trace-coverage "$COV_FIX/specs" "$COV_FIX/traces" --json 2>&1) || rc=$?
if [ $rc -eq 1 ] && echo "$TC_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
s = d['summary']
assert d['status'] == 'fail' and s['covered'] == 2 and s['uncovered'] == 1, s
assert s['orphan_traces'] == ['stray.trace'], s
" 2>/dev/null; then
  report PASS "trace-coverage: --json summary counts (2 covered / 1 gap / 1 orphan)"
else
  report FAIL "trace-coverage: --json summary counts (2 covered / 1 gap / 1 orphan)" "exit=$rc"
fi

# trace-coverage on the canonical bare-array trace-strict fixtures (the 043
# crash reproduction): must complete without crashing (exit 0 or 1, never 2)
rc=0; python3 "$CHECK" --trace-coverage "$TOOLS/../tests/fixtures/trace-strict" "$TOOLS/../tests/fixtures/trace-strict" >/dev/null 2>&1 || rc=$?
if [ $rc -le 1 ]; then
  report PASS "trace-coverage: canonical bare-array traces do not crash (043 repro)"
else
  report FAIL "trace-coverage: canonical bare-array traces do not crash (043 repro)" "exit=$rc"
fi

# --coverage: examples/complete has implemented specs; examples/planned is the
# gap scenario (design-only, no code — everything spec-ahead or no-target)
rc=0; CV_JSON=$(python3 "$CHECK" --coverage "$TOOLS/../examples/complete/design/specs" --target "$TOOLS/../examples/complete" --json 2>&1) || rc=$?
if [ $rc -eq 0 ] && echo "$CV_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['summary']['implemented'] > 0, d['summary']
" 2>/dev/null; then
  report PASS "coverage: parseable specs report without crashing, implemented > 0 (043 repro)"
else
  report FAIL "coverage: parseable specs report without crashing, implemented > 0 (043 repro)" "exit=$rc"
fi

rc=0; CV_PLAN=$(python3 "$CHECK" --coverage "$TOOLS/../examples/planned/design/specs" --target "$TOOLS/../examples/planned" --json 2>&1) || rc=$?
if [ $rc -eq 0 ] && echo "$CV_PLAN" | python3 -c "
import json, sys
d = json.load(sys.stdin)
s = d['summary']
assert s['implemented'] == 0 and s['spec_ahead'] > 0, s
" 2>/dev/null; then
  report PASS "coverage: design-only project reports spec-ahead gaps, exit 0 (informational)"
else
  report FAIL "coverage: design-only project reports spec-ahead gaps, exit 0 (informational)" "exit=$rc"
fi


echo ""
echo "=== Results: $PASS passed, $FAIL failed, $SKIP skipped ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
