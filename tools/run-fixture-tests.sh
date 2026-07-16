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
      report SKIP "$(basename "$f" .yaml) (alloy jar unavailable)"
    else
      report FAIL "$(basename "$f" .yaml)" "$result"
    fi
  done
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $SKIP skipped ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
