#!/usr/bin/env python3
"""archwright-check: Run verification checks against specs.

Usage:
  archwright-check <spec-file>...                Check individual specs
  archwright-check --all <dir>                   Check all specs in directory
  archwright-check --static <dir> [--target <root>]   Check constraint/dependency specs only
  archwright-check --trace <spec.yaml> <trace.json> [--json]   Validate a trace against a behavior spec (--json: CK-03 document)
  archwright-check --probe <spec.yaml>           Non-vacuity probe: a false invariant MUST FAIL
  ... [--baseline <file>]                        Explicit baseline (else .archwright-baseline.json auto-discovered up to the git root)
  ... [--update-baseline]                        Ratchet (CK-08): remove entries that no longer reproduce; NEVER adds.
                                                 Refuses on errored runs and with --changed-only (a scoped/incomplete
                                                 run cannot prove a violation is gone).
  ... [--evidence <file>]                        Explicit evidence ledger (else an EXISTING .archwright-evidence.json auto-discovered up-tree)
  ... [--changed-only [--base <ref>]]            Only check specs affected by the git diff vs <ref> (default HEAD): the spec
                                                 file changed, or a changed/untracked file sits under a check.target path.
                                                 Specs without a file target (behavior/contract/command-mode) always run.

Baseline (CK-07): suppresses fully-fingerprint-matched constraint/dependency
violations to warnings (baselined: true). A baselined ★★ keeps escalate: true;
behavior/trace violations are never suppressed. remaining_delta counts
violations after suppression.

Evidence ledger (ADR 0009): when active (existing file up-tree, or --evidence),
pass/fail runs auto-append confidence evidence events — demotion-candidate
(FAIL on a ★★/★, unless baselined) and promotion-candidate (pass streak per
config.promotion_streak, default 5, or a ★/— invariant passing a bounded
check). Tool-owned; human ratification happens in the artifact (★★ moves are
always HITL). Bootstrap per project: echo '{}' > design/.archwright-evidence.json

Dispatches by spec kind:
  behavior    → compile to Alloy, run model checker (if alloy6.jar available)
  constraint  → execute self-described check (grep, semgrep, script)
  dependency  → execute self-described check (grep, script)
  contract    → schema validation only (for now)
"""

import sys
import os
import re
import fnmatch
import hashlib
import argparse
import yaml
import subprocess
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from archwright_common import state_events

SCRIPT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Shared constants and utilities — canonical source: check/common.py
# Tombstone re-exports for backward compatibility during extraction.
# ---------------------------------------------------------------------------
from check.common import (
    FINGERPRINT_ALGO, _EVIDENCE_RX, _EVIDENCE_CAP, _SEVERITY,
    _find_up, extract_frontmatter, load_spec, _project_root_for,
    _code_state, _extract_section, _expected_for,
    _fingerprint_base, _split_evidence,
)

from check.baseline import BASELINE_FILENAME, find_baseline, load_baseline


# Evidence ledger (ADR 0009) — canonical source: check/ledger.py
from check.ledger import (
    EVIDENCE_FILENAME, PROMOTION_STREAK_DEFAULT,
    find_evidence_ledger, load_evidence_ledger,
    _event_identity, record_evidence, write_evidence_ledger,
)


# ---------------------------------------------------------------------------
# Changed-only scope selection (CK-19) — `--changed-only [--base <ref>]`.
# Affected = the spec file itself changed, OR any changed file sits under one
# of the spec's check.target paths. Specs without a target path (behavior,
# contract, command/script-mode checks) can't be scoped by file overlap and
# are treated as always affected — over-checking is safe, silent skipping is
# not. Git failures are tool errors (exit 2), never an empty "nothing
# changed" pass.
# ---------------------------------------------------------------------------


def _git_changed_files(base, root):
    """Absolute paths of files changed vs <base> (committed + working tree)
    plus untracked files (a NEW file can violate a constraint too).
    Raises ValueError on any git failure — loud, never a silent empty set."""
    import shutil
    if shutil.which("git") is None:
        raise ValueError("--changed-only requires git on PATH")
    def _git(*args):
        r = subprocess.run(["git", "-C", str(root)] + list(args),
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError(f"git {args[0]} failed: {(r.stderr or '').strip()[:200]}")
        return r.stdout
    git_root = Path(_git("rev-parse", "--show-toplevel").strip())
    changed = set()
    for line in _git("diff", "--name-only", base).splitlines():
        if line.strip():
            changed.add((git_root / line.strip()).resolve())
    for line in _git("ls-files", "--others", "--exclude-standard").splitlines():
        if line.strip():
            changed.add((git_root / line.strip()).resolve())
    return changed


def _spec_affected(spec_path, changed):
    """True if this spec must be re-checked given the changed-file set."""
    spec_path = Path(spec_path).resolve()
    if spec_path in changed:
        return True  # the spec itself changed
    data, kind = load_spec(spec_path)
    if not data:
        return True  # unparseable — let the normal check path report the error
    check = data.get("check") or {}
    targets = check.get("target")
    if not targets or check.get("command"):
        # No file target to scope by (behavior/contract specs, command-mode
        # checks whose scope only the command knows): always affected.
        return True
    targets = [targets] if isinstance(targets, str) else targets
    project_root = _project_root_for(spec_path)
    for t in targets:
        tp = (project_root / t).resolve()
        for c in changed:
            if c == tp or tp in c.parents:
                return True
    return False


def _find_alloy_jar():
    """Locate alloy6.jar: env override, then relative to this script, then legacy path."""
    env = os.environ.get("ARCHWRIGHT_ALLOY_JAR")
    if env and Path(env).exists():
        return Path(env)
    candidates = [
        SCRIPT_DIR.parent / ".references" / "alloy6.jar",
        Path.home() / "code" / "archwright" / ".references" / "alloy6.jar",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def check_behavior(data, spec_path):
    """Check a behavior spec: compile to Alloy, run the model checker, parse verdicts."""
    import shutil
    import tempfile

    results = []
    invariants = data.get("invariants", [])

    def skip_all(message, assurance="none"):
        return [{
            "invariant": inv.get("id", "unknown"),
            "status": "skipped",
            "message": message,
            "confidence": inv.get("confidence", "—"),
            "assurance": assurance,
        } for inv in invariants]

    alloy_jar = _find_alloy_jar()
    if alloy_jar is None:
        return skip_all("Alloy JAR not found — set ARCHWRIGHT_ALLOY_JAR or place alloy6.jar in .references/")

    java = shutil.which("java")
    if java is None:
        return skip_all("java not on PATH — required to run alloy6.jar")

    # Split invariants: mechanically checkable (have alloy:) vs prose-only
    checkable = [inv for inv in invariants if inv.get("alloy")]
    prose_only = [inv for inv in invariants if not inv.get("alloy")]

    for inv in prose_only:
        results.append({
            "invariant": inv.get("id", "unknown"),
            "status": "skipped",
            "message": "no `alloy:` expression — prose predicate not mechanically checkable; add one for ★★ verification",
            "confidence": inv.get("confidence", "—"),
            "assurance": "none",
        })

    if not checkable:
        return results

    # Compile spec → .als and execute in a temp dir (Alloy writes solution files to cwd)
    compiler = SCRIPT_DIR / "archwright-compile-alloy.py"
    with tempfile.TemporaryDirectory(prefix="archwright-alloy-") as tmp:
        als_path = Path(tmp) / (Path(spec_path).stem + ".als")
        comp = subprocess.run(
            [sys.executable, str(compiler), str(spec_path), "-o", str(als_path)],
            capture_output=True, text=True,
        )
        if comp.returncode != 0 or not als_path.exists():
            return results + [{
                "invariant": inv.get("id", "unknown"),
                "status": "error",
                "message": f"Alloy compilation failed: {(comp.stderr or comp.stdout)[:200]}",
            } for inv in checkable]

        # The compiler skips invariants the model can't reliably check
        # (uncompiled guard/assign taint) — honor those as skipped, not errors.
        compiler_skips = {}
        for m in re.finditer(r"^SKIP-INVARIANT:\s*([\w-]+):\s*(.+)$", comp.stdout or "", re.MULTILINE):
            compiler_skips[m.group(1)] = m.group(2).strip()
        still_checkable = []
        for inv in checkable:
            inv_id = inv.get("id", "unknown")
            if inv_id in compiler_skips:
                results.append({
                    "invariant": inv_id,
                    "status": "skipped",
                    "message": compiler_skips[inv_id],
                    "confidence": inv.get("confidence", "—"),
                    "assurance": "none",
                })
            else:
                still_checkable.append(inv)
        checkable = still_checkable
        if not checkable:
            return results

        try:
            run = subprocess.run(
                [java, "-Djava.awt.headless=true", "-jar", str(alloy_jar), "exec", str(als_path)],
                capture_output=True, text=True, cwd=tmp, timeout=120,
            )
        except subprocess.TimeoutExpired:
            return results + [{
                "invariant": inv.get("id", "unknown"),
                "status": "error",
                "message": "Alloy solver timed out (120s)",
            } for inv in checkable]

        # Verdict lines (stderr): "NN. check <assertName>  ...  SAT|UNSAT"
        # UNSAT = no counterexample within scope (pass, bounded). SAT = violation.
        combined = (run.stderr or "") + "\n" + (run.stdout or "")
        verdicts = parse_alloy_verdicts(combined)

        if not verdicts:
            return results + [{
                "invariant": inv.get("id", "unknown"),
                "status": "error",
                "message": f"Alloy produced no verdict: {combined.strip()[:300]}",
            } for inv in checkable]

        for inv in checkable:
            assert_name = _alloy_field_name(inv.get("id", "unknown"))
            verdict = verdicts.get(assert_name)
            entry = {
                "invariant": inv.get("id", "unknown"),
                "confidence": inv.get("confidence", "—"),
                "assurance": "bounded",
            }
            if verdict == "UNSAT":
                entry["status"] = "pass"
                entry["message"] = "no counterexample within scope (bounded, not proof)"
            elif verdict == "SAT":
                entry["status"] = "fail"
                entry["message"] = "counterexample found — invariant violated"
                sol = Path(tmp) / (als_path.stem) / f"{assert_name}-solution-0.md"
                if sol.exists():
                    entry["violations"] = [l for l in sol.read_text(encoding="utf-8").splitlines()[:20] if l.strip()]
                entry["from_pattern"] = inv.get("from_pattern")
                entry["from_force"] = inv.get("from_force")
            else:
                entry["status"] = "error"
                entry["message"] = f"no verdict for assertion '{assert_name}' (got: {verdicts})"
            results.append(entry)

    return results


def parse_alloy_verdicts(combined_output):
    """Parse SAT/UNSAT verdicts from Alloy 6 exec CLI combined stdout+stderr.

    Expected format (undocumented, unversioned — Alloy 6.2.0+):
        NN. check <assertName>  ...  SAT|UNSAT

    Returns a dict mapping assertion names to verdict strings ("SAT" or "UNSAT").
    Returns empty dict if no verdicts found (caller should treat as error — the
    format may have changed or the solver produced no output).

    The regex is pinned to the observed output of the SHA-256-verified jar in
    tools/alloy-runtime.json. On jar upgrades, the fixture suite's format-break
    test will fail loudly (exit 2) if the format changes.
    """
    verdicts = {}
    for m in re.finditer(r"check\s+(\w+)\b[^\n]*?\b(UNSAT|SAT)\b", combined_output):
        verdicts[m.group(1)] = m.group(2)
    return verdicts


def _alloy_field_name(name):
    """Mirror archwright-compile-alloy's _to_field: slug → camelCase assert name."""
    parts = name.replace("-", "_").split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def check_contract(data, spec_path):
    """Check a contract spec: structural_invariants via Alloy + check section via conformance.

    Both paths run in one invocation (grill 2026-08-01 Q2). If neither section
    is present, falls back to the schema-only pass-through.
    """
    results = []
    has_structural = bool(data.get("structural_invariants"))
    has_check = bool(data.get("check"))

    if not has_structural and not has_check:
        return [{"invariant": data.get("id", "?"), "status": "pass",
                 "message": "contract validation: schema only (no runtime check)"}]

    # Path 1: structural_invariants → Alloy
    if has_structural:
        results.extend(_check_structural_invariants(data, spec_path))

    # Path 2: check section → grep/semgrep/script (reuse conformance logic)
    if has_check:
        results.extend(check_conformance(data, spec_path))

    return results


def _check_structural_invariants(data, spec_path):
    """Compile structural_invariants to Alloy and run the model checker."""
    import shutil
    import tempfile

    results = []
    invariants = data.get("structural_invariants", [])

    def skip_all(message, assurance="none"):
        return [{
            "invariant": inv.get("id", "unknown"),
            "status": "skipped",
            "message": message,
            "confidence": inv.get("confidence", "—"),
            "assurance": assurance,
        } for inv in invariants]

    alloy_jar = _find_alloy_jar()
    if alloy_jar is None:
        return skip_all("Alloy JAR not found — set ARCHWRIGHT_ALLOY_JAR or place alloy6.jar in .references/")

    java = shutil.which("java")
    if java is None:
        return skip_all("java not on PATH — required to run alloy6.jar")

    # All invariants need alloy: expression
    checkable = [inv for inv in invariants if inv.get("alloy")]
    prose_only = [inv for inv in invariants if not inv.get("alloy")]

    for inv in prose_only:
        results.append({
            "invariant": inv.get("id", "unknown"),
            "status": "skipped",
            "message": "no `alloy:` expression — structural predicate not mechanically checkable",
            "confidence": inv.get("confidence", "—"),
            "assurance": "none",
        })

    if not checkable:
        return results

    # Compile contract spec → .als using the contract-specific compiler
    compiler = SCRIPT_DIR / "archwright-compile-contract-alloy.py"
    with tempfile.TemporaryDirectory(prefix="archwright-contract-alloy-") as tmp:
        als_path = Path(tmp) / (Path(spec_path).stem + ".als")
        comp = subprocess.run(
            [sys.executable, str(compiler), str(spec_path), "-o", str(als_path)],
            capture_output=True, text=True,
        )
        if comp.returncode != 0 or not als_path.exists():
            return results + [{
                "invariant": inv.get("id", "unknown"),
                "status": "error",
                "message": f"Contract Alloy compilation failed: {(comp.stderr or comp.stdout)[:200]}",
            } for inv in checkable]

        try:
            run = subprocess.run(
                [java, "-Djava.awt.headless=true", "-jar", str(alloy_jar), "exec", str(als_path)],
                capture_output=True, text=True, cwd=tmp, timeout=120,
            )
        except subprocess.TimeoutExpired:
            return results + [{
                "invariant": inv.get("id", "unknown"),
                "status": "error",
                "message": "Alloy solver timed out (120s)",
            } for inv in checkable]

        # Parse verdicts: SAT = counterexample found (FAIL), UNSAT = no counterexample (PASS)
        combined = (run.stderr or "") + "\n" + (run.stdout or "")
        verdicts = {}
        for m in re.finditer(r"check\s+(\w+)\b[^\n]*?\b(UNSAT|SAT)\b", combined):
            verdicts[m.group(1)] = m.group(2)

        if not verdicts:
            return results + [{
                "invariant": inv.get("id", "unknown"),
                "status": "error",
                "message": f"Alloy produced no verdict: {combined.strip()[:300]}",
            } for inv in checkable]

        for inv in checkable:
            assert_name = _alloy_field_name(inv.get("id", "unknown"))
            verdict = verdicts.get(assert_name)
            entry = {
                "invariant": inv.get("id", "unknown"),
                "confidence": inv.get("confidence", "—"),
                "assurance": "bounded",
            }
            if verdict == "UNSAT":
                entry["status"] = "pass"
                entry["message"] = "no counterexample within scope (structural model, bounded)"
            elif verdict == "SAT":
                entry["status"] = "fail"
                entry["message"] = "counterexample found — structural invariant violated in data model"
                entry["from_pattern"] = data.get("from_patterns", [None])[0] if data.get("from_patterns") else None
            else:
                entry["status"] = "error"
                entry["message"] = f"no verdict for assertion '{assert_name}' (got: {verdicts})"
            results.append(entry)

    return results


from check.conformance import check_conformance


def enrich_results(results, data, spec_path):
    """CK-09/CK-10: attach spec_id, severity, escalate, provenance,
    suggested_route, and contrast_pair to results."""
    from_patterns = data.get("from_patterns", [])
    default_pattern = from_patterns[0] if from_patterns else None
    default_force = data.get("from_force") or data.get("protects_experience")

    for r in results:
        r.setdefault("spec_id", data.get("id", "unknown"))
        # Every result carries a confidence (pass results feed evidence-ledger
        # streaks at the right tier — ADR 0009); fail keeps its own if set.
        if not r.get("confidence"):
            r["confidence"] = data.get("confidence", "—")
        if r["status"] == "fail":
            conf = r["confidence"]
            r["severity"] = _SEVERITY.get(conf, "info")
            if conf == "★★":
                r["escalate"] = True  # ★★ violations always route to a human (C2)
            if not r.get("from_pattern"):
                r["from_pattern"] = default_pattern
            if not r.get("from_force"):
                r["from_force"] = default_force
            # Heuristic (CK-09): failing check on existing code = implementation
            # drifted (fix-implementation); a broken check itself is status=error.
            r["suggested_route"] = "fix-implementation"
            actual = (r.get("violations") or [r.get("message", "")])[0]
            r["contrast_pair"] = {"expected": _expected_for(r, data, spec_path),
                                  "actual": actual}
        elif r["status"] == "error":
            r["suggested_route"] = "fix-check"
    return results


def format_result(spec_path, kind, results):
    """Format check results for human-readable output."""
    path = Path(spec_path)
    lines = []

    has_fail = any(r["status"] == "fail" for r in results)
    has_error = any(r["status"] == "error" for r in results)
    all_skip = all(r["status"] in ("skipped", "pending") for r in results)
    has_pending = any(r["status"] == "pending" for r in results)
    skips = [r for r in results if r["status"] in ("skipped", "pending")]

    if has_fail or has_error:
        lines.append(f"  ✗ FAIL: {path.name} (kind: {kind})")
        for r in results:
            if r["status"] in ("fail", "error"):
                conf = r.get("confidence", "")
                conf_str = f" ({conf})" if conf else ""
                esc = " [ESCALATE]" if r.get("escalate") else ""
                lines.append(f"    invariant: {r['invariant']}{conf_str}{esc}")
                lines.append(f"    {r['message']}")
                if r.get("from_pattern") or r.get("from_force"):
                    lines.append(f"    provenance: pattern={r.get('from_pattern')} force={r.get('from_force')} route={r.get('suggested_route')}")
                for v in r.get("violations", []):
                    lines.append(f"      {v}")
    elif all_skip:
        label = "PENDING" if has_pending else "SKIP"
        lines.append(f"  ○ {label}: {path.name} (kind: {kind})")
        for r in results:
            lines.append(f"    {r.get('message', '')}")
    else:
        lines.append(f"  ✓ PASS: {path.name} (kind: {kind})")
        for r in skips:
            lines.append(f"    ○ {r['invariant']}: {r.get('message', '')}")

    return "\n".join(lines)


def check_file(spec_path):
    """Check a single spec file. Returns (kind, results) — structured results
    enriched with provenance/contrast pairs (CK-09/CK-10)."""
    data, kind = load_spec(spec_path)
    if not data:
        return None, [{"invariant": "?", "spec_id": str(spec_path), "status": "error",
                       "message": f"could not parse {spec_path}",
                       "suggested_route": "fix-check"}]

    if kind == "behavior":
        results = check_behavior(data, spec_path)
    elif kind in ("constraint", "dependency"):
        results = check_conformance(data, spec_path)
    elif kind == "contract":
        results = check_contract(data, spec_path)
    elif kind == "pattern":
        results = [{"invariant": data.get("id", "?"), "status": "skipped",
                    "message": "patterns are not checked — check their resolved specs"}]
    else:
        results = [{"invariant": "?", "status": "error",
                    "message": f"unknown kind: {kind}", "suggested_route": "fix-check"}]

    return kind, enrich_results(results, data, spec_path)


def _find_op(pred, op):
    """Find operator position outside braces/parens."""
    depth_p, depth_b = 0, 0
    for i in range(len(pred) - len(op) + 1):
        c = pred[i]
        if c == "(": depth_p += 1
        elif c == ")": depth_p -= 1
        elif c == "{": depth_b += 1
        elif c == "}": depth_b -= 1
        if depth_p == 0 and depth_b == 0 and pred[i:i+len(op)] == op:
            return i
    return -1


def _split_op(pred, op):
    """Split on operator respecting braces/parens."""
    parts, depth_p, depth_b, start = [], 0, 0, 0
    for i in range(len(pred) - len(op) + 1):
        c = pred[i]
        if c == "(": depth_p += 1
        elif c == ")": depth_p -= 1
        elif c == "{": depth_b += 1
        elif c == "}": depth_b -= 1
        if depth_p == 0 and depth_b == 0 and pred[i:i+len(op)] == op:
            parts.append(pred[start:i].strip())
            start = i + len(op)
    parts.append(pred[start:].strip())
    return parts


class Untranslatable:
    """Sentinel: a predicate (or atom) the translator cannot evaluate (ticket 015).

    Returned by translate_predicate instead of a silent True so callers can
    SKIP-with-reason at the invariant/guard granularity — mirroring the
    Alloy-side taint discipline (ticket 008). Refuses bool() coercion so any
    unaudited call site fails loudly instead of silently passing.
    """
    def __init__(self, reason):
        self.reason = reason

    def __bool__(self):
        raise TypeError(f"Untranslatable predicate used as bool: {self.reason}")


def _unquote(token):
    """Strip matching quotes from an enum literal ('approval' / "approval") —
    the quoted form is what the Alloy backend requires in guards, so the trace
    evaluator must accept the same syntax (ticket 041 field finding)."""
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token


def translate_predicate(pred, state, current_spec_state=None):
    """Evaluate a spec predicate against a state dict.

    Returns True, False, or Untranslatable (three-valued — Kleene semantics
    for composites: a composite is decided only when its translatable parts
    decide it; otherwise the Untranslatable propagates).
    """
    pred = pred.strip()

    # Strip balanced outer parens
    if pred.startswith("(") and pred.endswith(")"):
        depth = 0
        for i, c in enumerate(pred):
            if c == "(": depth += 1
            elif c == ")": depth -= 1
            if depth == 0 and i < len(pred) - 1:
                break
        else:
            pred = pred[1:-1].strip()

    # Prefix operators first (before binary splits)
    if pred.startswith("always "):
        inner = pred[7:].strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1]
        return translate_predicate(inner, state, current_spec_state)

    if pred.startswith("not "):
        r = translate_predicate(pred[4:], state, current_spec_state)
        if isinstance(r, Untranslatable):
            return r
        return not r

    # Binary operators (lowest precedence first, respecting braces/parens)
    idx = _find_op(pred, " implies ")
    if idx >= 0:
        lhs, rhs = pred[:idx].strip(), pred[idx+9:].strip()
        l = translate_predicate(lhs, state, current_spec_state)
        if l is False:
            return True
        r = translate_predicate(rhs, state, current_spec_state)
        if r is True:
            return True
        if isinstance(l, Untranslatable):
            return l
        if isinstance(r, Untranslatable):
            return r
        return r  # l is True, r is False

    idx = _find_op(pred, " or ")
    if idx >= 0:
        untranslatable = None
        for p in _split_op(pred, " or "):
            r = translate_predicate(p, state, current_spec_state)
            if r is True:
                return True
            if isinstance(r, Untranslatable) and untranslatable is None:
                untranslatable = r
        return untranslatable if untranslatable is not None else False

    idx = _find_op(pred, " and ")
    if idx >= 0:
        untranslatable = None
        for p in _split_op(pred, " and "):
            r = translate_predicate(p, state, current_spec_state)
            if r is False:
                return False
            if isinstance(r, Untranslatable) and untranslatable is None:
                untranslatable = r
        return untranslatable if untranslatable is not None else True

    # Atoms
    if " in {" in pred:
        match = re.match(r"(\w+)\s+in\s+\{([^}]+)\}", pred)
        if match:
            var = match.group(1)
            values = [_unquote(v.strip()) for v in match.group(2).split(",")]
            actual = str(state.get(var, ""))
            return actual in values

    if " == " in pred:
        lhs, rhs = pred.split(" == ", 1)
        lval = str(state.get(lhs.strip(), _unquote(lhs.strip())))
        rval = str(state.get(rhs.strip(), _unquote(rhs.strip())))
        return lval == rval

    if " != " in pred:
        lhs, rhs = pred.split(" != ", 1)
        lval = str(state.get(lhs.strip(), _unquote(lhs.strip())))
        rval = str(state.get(rhs.strip(), _unquote(rhs.strip())))
        return lval != rval

    # Numeric comparisons (<=, >=, <, >) — var-to-var or var-to-literal.
    # Order matters: check two-char operators before one-char.
    for op, fn in ((" <= ", lambda a, b: a <= b), (" >= ", lambda a, b: a >= b),
                   (" < ", lambda a, b: a < b), (" > ", lambda a, b: a > b)):
        if op in pred:
            lhs, rhs = pred.split(op, 1)
            lraw = state.get(lhs.strip(), lhs.strip())
            rraw = state.get(rhs.strip(), rhs.strip())
            try:
                return fn(float(lraw), float(rraw))
            except (TypeError, ValueError):
                return Untranslatable(
                    f"non-numeric operands in comparison: '{pred}'")

    # Bare identifier: state name reference
    if current_spec_state is not None and re.match(r"^[a-z][a-z0-9_-]*$", pred):
        return pred == current_spec_state

    if pred in state:
        return bool(state[pred])

    return Untranslatable(f"unsupported predicate construct: '{pred}'")


def build_trace_document(spec_path, payload, data=None, active_invariants=None):
    """Ticket 016: map a trace result payload into the CK-03 document shape
    (check-output-schema.yaml) so archwright-passup routes trace violations
    uniformly with static ones.

    Coverage counts INVARIANTS declared checkable (not specs); a structural
    failure (protocol/transition/guard — no spec invariant) adds one to
    `checked` so passed+failed+skipped always sums to checked.
    """
    status = payload["status"]
    data = data or {}
    spec_id = payload.get("spec_id") or data.get("id")
    active_ids = [inv["id"] for inv in (active_invariants or [])]

    skips = []
    for s in payload.get("invariants_skipped", []):
        skips.append({"spec_id": spec_id, "spec_path": str(spec_path),
                      "invariant": s["id"], "reason": s["reason"]})
    for g in payload.get("guards_skipped", []):
        skips.append({
            "spec_id": spec_id, "spec_path": str(spec_path), "invariant": None,
            "reason": (f"guard '{g['predicate']}' untranslatable at position "
                       f"{g['position']} (event '{g['event']}'): {g['reason']}"),
        })

    violations, errors = [], []
    structural = 0
    if status == "fail":
        v = payload["violation"]
        spec_inv = next((i for i in (data.get("invariants") or [])
                         if i.get("id") == v.get("invariant")), None)
        if spec_inv is None:
            structural = 1
        conf = (spec_inv or {}).get("confidence") or data.get("confidence", "—")
        prov = payload.get("provenance") or {}
        from_patterns = data.get("from_patterns") or []
        from_pattern = (prov.get("from_pattern")
                        or (from_patterns[0] if from_patterns else None))
        from_force = (prov.get("from_force") or data.get("from_force")
                      or data.get("protects_experience"))
        if spec_inv:
            expected = _expected_for({"invariant": spec_inv["id"]}, data, spec_path)
        elif v.get("type") == "transition":
            expected = (f"an event in {v.get('valid_events')} from state "
                        f"'{v.get('current_spec_state')}'")
        elif v.get("type") == "guard":
            expected = (f"a guard-satisfying transition for event '{v.get('event')}' "
                        f"in state '{v.get('current_spec_state')}'")
        else:  # protocol
            expected = "first trace event 'INITIAL'"
        actual = (f"event '{v.get('event')}' at trace position {v['position']} "
                  f"(clock {v['clock']})")
        if v.get("state") is not None:
            actual += f" with state {json.dumps(v['state'], sort_keys=True)}"
        violations.append({
            "spec_id": spec_id,
            "spec_kind": "behavior",
            "spec_path": str(spec_path),
            "invariant": v.get("invariant") or f"trace-{v.get('type', 'invariant')}",
            "confidence": conf,
            "severity": _SEVERITY.get(conf, "info"),
            "escalate": conf == "★★",
            "message": v["message"],
            "evidence": [actual],
            "from_pattern": from_pattern,
            "from_force": from_force,
            "suggested_route": "fix-implementation",
            "contrast_pair": {"expected": expected, "actual": actual},
        })
    elif status == "error":
        errors.append({"spec_id": spec_id, "spec_path": str(spec_path),
                       "message": payload.get("message", ""),
                       "suggested_route": "fix-check"})

    skipped = len(payload.get("invariants_skipped", []))
    checked = len(active_ids) + structural
    failed = 1 if status == "fail" else 0
    coverage = {
        "checked": checked,
        "passed": 0 if status == "error" else max(0, checked - skipped - failed),
        "failed": failed,
        "skipped": skipped,
        "errors": 1 if status == "error" else 0,
        "pending": 0,
    }

    if status == "error":
        doc_status = "error"
    elif violations:
        doc_status = "fail"
    else:
        doc_status = "pass"

    return {
        "status": doc_status,
        "scope": {"mode": "trace", "specs_checked": 1, "target": None},
        "violations": violations,
        "errors": errors,
        "skips": skips,
        "coverage": coverage,
        "remaining_delta": len(violations),
    }


def check_trace(spec_path, trace_path, json_output=False, evidence_arg=None):
    """Validate a JSON trace against a behavior spec.

    Output contract (ticket 016): the bespoke replay shape (trace-schema.ts)
    by default; with json_output=True, the CK-03 document (check-output-schema
    .yaml) so archwright-passup routes trace violations uniformly with static
    ones. Exit codes unchanged: 0 pass / 1 fail / 2 error.

    Evidence (ADR 0009): pass/fail runs feed the evidence ledger when one is
    active (existing file up-tree or explicit --evidence). Trace events carry
    fingerprints: [] — aw/v1 hashes static path+content, which traces don't
    have (CK-07 scope cut, upheld); identity = key + invariant + confidence.
    """
    spec_path = Path(spec_path)
    trace_path = Path(trace_path)

    data = None
    active_invariants = []
    evidence_path = None
    evidence_ledger = None

    def _maybe_record(payload, code):
        """Record trace evidence: on pass, streak credit per checked invariant;
        on fail, one demotion-candidate for the violated invariant (structural
        violations use spec-level confidence). Errors prove nothing. Invariants
        that merely didn't fail on a FAILED trace get no streak credit — the
        replay stopped early, so their coverage is incomplete."""
        if evidence_ledger is None or code not in (0, 1) or data is None:
            return None
        spec_id = data.get("id", "unknown")
        results = []
        if code == 0:
            skipped = {s["id"] for s in payload.get("invariants_skipped", [])}
            for inv in active_invariants:
                if inv["id"] in skipped:
                    continue
                results.append({"status": "pass", "spec_id": spec_id,
                                "invariant": inv["id"],
                                "confidence": inv.get("confidence", "—"),
                                "assurance": "trace"})
        else:
            v = payload.get("violation", {})
            spec_inv = next((i for i in (data.get("invariants") or [])
                             if i.get("id") == v.get("invariant")), None)
            prov = payload.get("provenance") or {}
            results.append({
                "status": "fail", "spec_id": spec_id,
                "invariant": v.get("invariant") or f"trace-{v.get('type', 'invariant')}",
                "confidence": (spec_inv or {}).get("confidence") or data.get("confidence", "—"),
                "assurance": "trace",
                "from_pattern": prov.get("from_pattern"),
                "from_force": prov.get("from_force"),
                "message": v.get("message"),
            })
        appended = record_evidence(evidence_ledger,
                                   [(spec_path, "behavior", results)], {},
                                   code_state=_code_state(_project_root_for(spec_path)))
        write_evidence_ledger(evidence_path, evidence_ledger)
        return {"path": str(evidence_path), "events_appended": len(appended)}

    def _emit(payload, code):
        ev_info = _maybe_record(payload, code)
        if json_output:
            doc = build_trace_document(spec_path, payload, data, active_invariants)
            doc["code_state"] = _code_state(_project_root_for(spec_path))
            if ev_info:
                doc["evidence_ledger"] = ev_info
            print(json.dumps(doc, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(payload))
            if ev_info and ev_info["events_appended"]:
                # stderr: the bespoke shape is a single parseable stdout line
                print(f"evidence: {ev_info['events_appended']} event(s) appended "
                      f"to {ev_info['path']}", file=sys.stderr)
        return code

    # Load spec
    if spec_path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    else:
        return _emit({"status": "error", "message": "Trace checking requires a YAML behavior spec"}, 2)

    if data.get("kind") != "behavior":
        return _emit({"status": "error", "message": f"Expected kind: behavior, got: {data.get('kind')}"}, 2)

    # Evidence ledger (ADR 0009): load before replay so a malformed ledger is
    # a tool error (exit 2), never a silently-dropped recording.
    evidence_path = find_evidence_ledger([spec_path.parent], explicit=evidence_arg)
    if evidence_path:
        try:
            evidence_ledger = load_evidence_ledger(evidence_path)
        except ValueError as e:
            evidence_path = None
            return _emit({"status": "error", "message": str(e)}, 2)

    # Load trace
    try:
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return _emit({"status": "error", "message": f"Failed to parse trace: {e}"}, 2)

    if not isinstance(trace, list) or len(trace) == 0:
        return _emit({"status": "error", "message": "Trace must be a non-empty JSON array"}, 2)
    
    # Extract spec components
    states = data.get("states", {})
    invariants = data.get("invariants", [])
    initial_state = data.get("initial", "")
    check_block = data.get("check", {}).get("trace", {})
    check_invariant_ids = check_block.get("invariants", [inv["id"] for inv in invariants])
    
    # Filter invariants to those declared checkable
    active_invariants = [inv for inv in invariants if inv["id"] in check_invariant_ids]
    
    # Replay trace
    current_state = initial_state
    # Ticket 015: untranslatable predicates SKIP-with-reason, never silent-pass.
    # Sticky per-invariant: once untranslatable at any step, the invariant is
    # skipped for the rest of the trace and excluded from invariants_checked.
    skipped_invariants = {}  # id -> reason
    guards_skipped = []      # [{position, event, predicate, reason}]

    def _fail(payload):
        """Emit a fail result carrying any skips accumulated before the failure
        point — a failing trace must not hide coverage gaps a passing one reports."""
        payload["invariants_skipped"] = [{"id": k, "reason": v}
                                         for k, v in skipped_invariants.items()]
        if guards_skipped:
            payload["guards_skipped"] = guards_skipped
        return _emit(payload, 1)
    
    for i, entry in enumerate(trace):
        event = entry.get("event", "")
        state_snapshot = entry.get("state", {})
        clock = entry.get("clock", i)
        
        # First entry: validate initial state
        if i == 0:
            if event != "INITIAL":
                return _fail({
                    "status": "fail",
                    "assurance": "trace",
                    "spec_id": data["id"],
                    "violation": {
                        "type": "protocol",
                        "position": 0,
                        "clock": clock,
                        "message": f"First trace event must be INITIAL, got '{event}'"
                    }
                })
            # Check invariants at initial state
            for inv in active_invariants:
                res = translate_predicate(inv["predicate"], state_snapshot, current_state)
                if isinstance(res, Untranslatable):
                    skipped_invariants.setdefault(inv["id"], res.reason)
                    continue
                if not res:
                    return _fail({
                        "status": "fail",
                        "assurance": "trace",
                        "spec_id": data["id"],
                        "violation": {
                            "invariant": inv["id"],
                            "position": 0,
                            "clock": clock,
                            "event": "INITIAL",
                            "state": state_snapshot,
                            "expected": inv["predicate"],
                            "message": f"Invariant '{inv['id']}' violated at INITIAL state"
                        },
                        "provenance": {
                            "from_force": inv.get("from_force"),
                            "from_pattern": inv.get("from_pattern")
                        }
                    })
            continue
        
        # Find valid transition from current state
        current_state_def = states.get(current_state, {})
        transitions = state_events(current_state_def)
        
        if event not in transitions:
            valid_events = list(transitions.keys())
            return _fail({
                "status": "fail",
                "assurance": "trace",
                "spec_id": data["id"],
                "violation": {
                    "type": "transition",
                    "invariant": f"valid-transition-from-{current_state}",
                    "position": i,
                    "clock": clock,
                    "event": event,
                    "state": state_snapshot,
                    "current_spec_state": current_state,
                    "valid_events": valid_events,
                    "message": f"No transition for event '{event}' in state '{current_state}'. Valid: {valid_events}"
                },
                "provenance": {
                    "from_force": current_state_def.get("from_force"),
                    "from_pattern": current_state_def.get("from_pattern")
                }
            })
        
        transition = transitions[event]
        
        # Handle single transition (dict) vs multiple (list)
        if isinstance(transition, dict):
            transition = [transition]
        elif not isinstance(transition, list):
            transition = [{"target": str(transition)}]
        
        # Try each transition (evaluate guards)
        transition_taken = False
        prev_state = trace[i-1].get("state", {}) if i > 0 else state_snapshot
        
        for trans in transition:
            if isinstance(trans, str):
                trans = {"target": trans}
            guard = trans.get("guard", {})
            guard_pred = guard.get("predicate") if isinstance(guard, dict) else None
            
            if guard_pred:
                g = translate_predicate(guard_pred, prev_state, current_state)
                if isinstance(g, Untranslatable):
                    # Untranslatable guard: SKIP the guard — transition accepted
                    # with a note, never a silent pass presented as evaluated.
                    guards_skipped.append({
                        "position": i,
                        "event": event,
                        "predicate": guard_pred,
                        "reason": g.reason,
                    })
                elif not g:
                    continue  # Guard failed, try next
            
            # Transition accepted
            current_state = trans.get("target", current_state)
            transition_taken = True
            break
        
        if not transition_taken:
            return _fail({
                "status": "fail",
                "assurance": "trace",
                "spec_id": data["id"],
                "violation": {
                    "type": "guard",
                    "position": i,
                    "clock": clock,
                    "event": event,
                    "state": state_snapshot,
                    "prev_state": prev_state,
                    "current_spec_state": current_state,
                    "message": f"All guards failed for event '{event}' in state '{current_state}'"
                }
            })
        
        # Check invariants after transition
        for inv in active_invariants:
            if inv["id"] in skipped_invariants:
                continue  # sticky skip — partial checking would be misleading
            res = translate_predicate(inv["predicate"], state_snapshot, current_state)
            if isinstance(res, Untranslatable):
                skipped_invariants.setdefault(inv["id"], res.reason)
                continue
            if not res:
                return _fail({
                    "status": "fail",
                    "assurance": "trace",
                    "spec_id": data["id"],
                    "violation": {
                        "invariant": inv["id"],
                        "position": i,
                        "clock": clock,
                        "event": event,
                        "state": state_snapshot,
                        "current_spec_state": current_state,
                        "expected": inv["predicate"],
                        "message": f"Invariant '{inv['id']}' violated after event '{event}' at position {i}"
                    },
                    "provenance": {
                        "from_force": inv.get("from_force"),
                        "from_pattern": inv.get("from_pattern")
                    }
                })
    
    # All steps passed (exit 0 even with skips — consistent with behavior-check
    # SKIPs: a skip is a coverage statement, not a pass; JSON makes it visible)
    result = {
        "status": "pass",
        "assurance": "trace",
        "spec_id": data["id"],
        "steps_checked": len(trace),
        "final_state": current_state,
        "invariants_checked": [inv["id"] for inv in active_invariants
                               if inv["id"] not in skipped_invariants],
        "invariants_skipped": [{"id": k, "reason": v}
                               for k, v in skipped_invariants.items()],
    }
    if guards_skipped:
        result["guards_skipped"] = guards_skipped
    return _emit(result, 0)


def build_document(mode, target_root, per_file, baseline_fps=None, baseline_path=None,
                   baseline_entries=0, scope_extra=None):
    """Build the CK-03 output document from per-file results.

    Schema: status, scope, violations[], coverage, remaining_delta.
    Each violation carries spec_id, invariant, confidence, severity, escalate,
    from_pattern, from_force, suggested_route, contrast_pair, evidence, and
    aw/v1 fingerprints (CK-07) aligned 1:1 with evidence[].

    Baseline (CK-07): when baseline_fps is provided, a constraint/dependency
    violation whose fingerprints are ALL baselined is suppressed — severity
    drops to warning, baselined: true, but escalate is UNTOUCHED (a baselined
    ★★ still routes to a human; the baseline is not a back door around C2).
    Behavior/trace violations are never suppressed (design violations, not
    adoptable debt). Document status and remaining_delta count only
    non-baselined violations; coverage counts raw check outcomes.
    """
    violations = []
    errors = []
    skips = []
    coverage = {"checked": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0, "pending": 0}
    fp_counter = {}

    def _next_fp(base):
        n = fp_counter.get(base, 0)
        fp_counter[base] = n + 1
        return f"{base}_{n}"

    for spec_path, kind, results in per_file:
        coverage["checked"] += 1
        statuses = {r["status"] for r in results}
        if "fail" in statuses:
            coverage["failed"] += 1
        elif "error" in statuses:
            coverage["errors"] += 1
        elif statuses <= {"skipped", "pending"}:
            # CK-06: target_status: pending is its own disjoint bucket —
            # neither pass nor fail nor skipped. Buckets sum to checked.
            if "pending" in statuses:
                coverage["pending"] += 1
            else:
                coverage["skipped"] += 1
        else:
            coverage["passed"] += 1

        for r in results:
            if r["status"] == "fail":
                spec_id = r.get("spec_id")
                invariant = r.get("invariant")
                evidence = (r.get("_all_matches") or r.get("violations") or [])[:_EVIDENCE_CAP]
                fingerprints = []
                for item in evidence:
                    p, c = _split_evidence(item)
                    fingerprints.append(_next_fp(_fingerprint_base(spec_id, invariant, p, c)))
                if not fingerprints:
                    # No located evidence (e.g. expect: present found nothing) —
                    # the absence itself is the violation; identity = spec+invariant.
                    fingerprints = [_next_fp(_fingerprint_base(spec_id, invariant, "", ""))]
                violation = {
                    "spec_id": spec_id,
                    "spec_kind": kind,
                    "spec_path": str(spec_path),
                    "invariant": invariant,
                    "confidence": r.get("confidence", "—"),
                    "severity": r.get("severity", "info"),
                    "escalate": r.get("escalate", False),
                    "message": r.get("message"),
                    "evidence": evidence,
                    "fingerprints": fingerprints,
                    "from_pattern": r.get("from_pattern"),
                    "from_force": r.get("from_force"),
                    "suggested_route": r.get("suggested_route"),
                    "contrast_pair": r.get("contrast_pair"),
                }
                if baseline_fps is not None:
                    suppressible = kind in ("constraint", "dependency")
                    if suppressible and all(fp in baseline_fps for fp in fingerprints):
                        violation["baselined"] = True
                        violation["severity"] = "warning"
                    else:
                        violation["baselined"] = False
                violations.append(violation)
            elif r["status"] == "error":
                errors.append({
                    "spec_id": r.get("spec_id"),
                    "spec_path": str(spec_path),
                    "message": r.get("message"),
                    "suggested_route": r.get("suggested_route", "fix-check"),
                })
            elif r["status"] in ("skipped", "pending"):
                # Skips carry their reason into the document (Extension Protocol
                # rule 1: SKIP-with-reason, never silent) — a skip is a coverage
                # statement, not a pass. Pending targets (CK-06) are counted in
                # coverage.pending but surface their reason here too.
                skips.append({
                    "spec_id": r.get("spec_id"),
                    "spec_path": str(spec_path),
                    "invariant": r.get("invariant"),
                    "reason": r.get("message"),
                })

    new_violations = [v for v in violations if not v.get("baselined")]
    if errors:
        status = "error"
    elif new_violations:
        status = "fail"
    else:
        status = "pass"

    doc = {
        "status": status,
        "scope": {"mode": mode, "specs_checked": coverage["checked"],
                  "target": str(target_root) if target_root else None,
                  **(scope_extra or {})},
        "violations": violations,
        "errors": errors,
        "skips": skips,
        "coverage": coverage,
        "fingerprint_algo": FINGERPRINT_ALGO,
        # CK-07: violations remaining after baseline suppression — the number
        # a fix loop is trying to drive to zero.
        "remaining_delta": len(new_violations),
    }
    if baseline_fps is not None:
        doc["baseline"] = {
            "path": str(baseline_path),
            "entries": baseline_entries,
            "suppressed": len(violations) - len(new_violations),
        }
    return doc


def probe_behavior(spec_path):
    """Non-vacuity probe (Extension Protocol rule 4 applied to authoring):
    replace the spec's invariants with one deliberately-false invariant
    (`always M.current != <reachable-state>`) and run the Alloy check.
    The probe MUST FAIL — a checker that passes a false invariant is vacuous.

    Exit meaning: 0 = probe produced a counterexample (checker non-vacuous),
    1 = probe PASSED (model vacuous — stutter-only or unreachable states),
    2 = tool error / not probeable (no transitions, jar missing, etc.).
    """
    import tempfile

    data, kind = load_spec(Path(spec_path))
    if kind != "behavior":
        print(f"Error: --probe requires a behavior spec (got kind: {kind})")
        return 2

    # Pick a syntactically-reachable non-initial state (a transition target).
    initial = data.get("initial")
    target_state = None
    for state_name, state_def in (data.get("states") or {}).items():
        for _event, trans in state_events(state_def).items():
            if isinstance(trans, dict):
                t = trans.get("target", state_name)
                if t != initial:
                    target_state = t
                    break
        if target_state:
            break
    if target_state is None:
        print("Error: no transition leaves the initial state — nothing to probe "
              "(a transition-less machine is vacuous by construction)")
        return 2

    sig = "".join(p.capitalize() for p in target_state.replace("-", "_").split("_"))
    probe = dict(data)
    probe["id"] = f"{data.get('id', 'spec')}-probe"
    probe["invariants"] = [{
        "id": "vacuity-probe",
        "type": "temporal",
        "predicate": f"deliberately false: {target_state} is never reached",
        "alloy": f"always M.current != {sig}",
        "confidence": "★★",
        "description": "MUST FAIL — proves the checker can produce a counterexample on this model",
    }]

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as tmp:
        yaml.dump(probe, tmp, allow_unicode=True, sort_keys=False)
        tmp_path = tmp.name
    try:
        results = check_behavior(probe, tmp_path)
    finally:
        os.unlink(tmp_path)

    statuses = {r.get("status") for r in results}
    if "fail" in statuses:
        print(f"PROBE OK: false invariant produced a counterexample "
              f"(state '{target_state}' reachable) — checker is non-vacuous for this spec")
        return 0
    if "error" in statuses:
        for r in results:
            if r.get("status") == "error":
                print(f"PROBE ERROR: {r.get('message', '')}")
        return 2
    if "skipped" in statuses and "pass" not in statuses:
        for r in results:
            print(f"PROBE SKIP: {r.get('message', '')}")
        return 2
    print(f"PROBE VACUOUS: the deliberately-false invariant PASSED — the model cannot "
          f"reach '{target_state}'; do not trust PASSes from this spec's checks")
    return 1


from check.coverage import trace_coverage_report, coverage_report


class _CheckParser(argparse.ArgumentParser):
    """ArgumentParser subclass that exits 2 on parse errors (matching existing contract)."""

    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}\n")
        sys.exit(2)


def _build_check_parser():
    parser = _CheckParser(
        prog="archwright-check",
        description=(
            "Verify archwright specs against implementation.\n\n"
            "Modes (mutually exclusive):\n"
            "  <spec>...                     Check specific spec file(s)\n"
            "  --all <dir>                   Check all specs in a directory\n"
            "  --static <dir>                Batch static check (constraint + dependency only)\n"
            "  --trace <spec> <trace>        Validate a trace against a behavior spec\n"
            "  --probe <spec>                Non-vacuity probe on a behavior spec\n"
            "  --trace-coverage <sdir> <tdir> Report trace coverage\n"
            "  --coverage <specs-dir>        Report spec→implementation coverage\n"
            "  --pbt <spec> --step <mod.py>  Property-based testing via Hypothesis"
        ),
        epilog="Exit codes: 0 = pass, 1 = violations/fail, 2 = usage/tool error",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    # Mode selection
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all", metavar="DIR", dest="all_dir",
                      help="Check all specs in DIR")
    mode.add_argument("--static", metavar="DIR", dest="static_dir",
                      help="Batch static check (constraint + dependency kinds only)")
    mode.add_argument("--trace", nargs=2, metavar=("SPEC", "TRACE"),
                      help="Validate a trace JSON against a behavior spec")
    mode.add_argument("--probe", metavar="SPEC",
                      help="Non-vacuity probe on a behavior spec")
    mode.add_argument("--trace-coverage", nargs=2, metavar=("SPECS_DIR", "TRACES_DIR"),
                      dest="trace_coverage",
                      help="Report which behavior specs have matching traces")
    mode.add_argument("--coverage", metavar="SPECS_DIR",
                      help="Report spec→implementation coverage")
    mode.add_argument("--pbt", metavar="SPEC",
                      help="Property-based testing via Hypothesis")

    # Common options
    parser.add_argument("--json", dest="json_output", action="store_true",
                        help="Emit CK-03 JSON document instead of human-readable output")
    parser.add_argument("--target", metavar="ROOT",
                        help="Target project root for check resolution")
    parser.add_argument("--baseline", metavar="FILE",
                        help="Explicit baseline file path (CK-07)")
    parser.add_argument("--update-baseline", action="store_true",
                        help="Remove resolved entries from baseline (CK-08)")
    parser.add_argument("--evidence", metavar="FILE",
                        help="Explicit evidence ledger path (ADR 0009)")
    parser.add_argument("--changed-only", action="store_true",
                        help="Check only specs affected by git diff (CK-19)")
    parser.add_argument("--base", metavar="REF", default="HEAD",
                        help="Git ref for --changed-only diff (default: HEAD)")

    # PBT-specific options
    parser.add_argument("--step", metavar="MODULE",
                        help="Step function module for --pbt")
    parser.add_argument("--emit", metavar="DIR",
                        help="Emit directory for --pbt generated tests")
    parser.add_argument("--examples", type=int, default=200,
                        help="Number of PBT examples (default: 200)")

    # Positional spec files
    parser.add_argument("files", nargs="*", metavar="SPEC",
                        help="Spec files to check (default mode)")

    return parser


def main():
    parser = _build_check_parser()

    # No args at all → exit 2 with usage (preserve existing behavior)
    if len(sys.argv) < 2:
        parser.print_usage(sys.stderr)
        sys.exit(2)

    args = parser.parse_args()

    # --- Dispatch early-return modes ---

    if args.trace:
        sys.exit(check_trace(args.trace[0], args.trace[1],
                             json_output=args.json_output,
                             evidence_arg=args.evidence))

    if args.probe:
        sys.exit(probe_behavior(args.probe))

    if args.trace_coverage:
        try:
            sys.exit(trace_coverage_report(args.trace_coverage[0],
                                           args.trace_coverage[1],
                                           json_output=args.json_output))
        except Exception as e:
            print(f"ERROR: trace-coverage failed: {e}", file=sys.stderr)
            sys.exit(2)

    if args.coverage:
        try:
            sys.exit(coverage_report(args.coverage,
                                     target_root=args.target,
                                     json_output=args.json_output))
        except Exception as e:
            print(f"ERROR: coverage failed: {e}", file=sys.stderr)
            sys.exit(2)

    if args.pbt:
        if not args.step:
            parser.error("--pbt requires --step <step_module.py>")
        pbt_adapter = Path(__file__).parent / "stacks" / "python" / "pbt_harness" / "adapter.py"
        if not pbt_adapter.exists():
            print(f"ERROR: PBT adapter not found: {pbt_adapter}", file=sys.stderr)
            sys.exit(2)
        import importlib.util
        pbt_mod_spec = importlib.util.spec_from_file_location("pbt_adapter", str(pbt_adapter))
        pbt_mod = importlib.util.module_from_spec(pbt_mod_spec)
        pbt_mod_spec.loader.exec_module(pbt_mod)
        result = pbt_mod.load_and_run(args.pbt, args.step, max_examples=args.examples)
        if args.json_output:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            status = result.get("status", "error")
            if status == "pass":
                print(f"PBT PASS: {result.get('examples_run', '?')} examples, all invariants held")
            elif status == "fail":
                print(f"PBT FAIL: {result.get('message', 'invariant violated')}")
            else:
                print(f"PBT ERROR: {result.get('message', 'unknown error')}")
        sys.exit({"pass": 0, "fail": 1, "error": 2}.get(result.get("status"), 2))

    # --- Main loop modes (--all, --static, or bare files) ---

    files = []
    target_root = Path(args.target).resolve() if args.target else None
    static_only = False
    json_output = args.json_output
    mode = "files"
    baseline_arg = args.baseline
    evidence_arg = args.evidence
    update_baseline = args.update_baseline
    changed_only = args.changed_only
    base_ref = args.base

    if args.all_dir:
        mode = "all"
        directory = Path(args.all_dir)
        files = sorted(
            [f for f in directory.rglob("*") if f.suffix in (".yaml", ".yml", ".md")]
        )
    elif args.static_dir:
        static_only = True
        mode = "static"
        directory = Path(args.static_dir)
        files = sorted(
            [f for f in directory.rglob("*") if f.suffix in (".yaml", ".yml", ".md")]
        )
    else:
        files = [Path(f) for f in args.files]

    if not files:
        if json_output:
            print(json.dumps(build_document(mode, target_root, []), indent=2, ensure_ascii=False))
        sys.exit(0)  # No specs = nothing to check = pass

    # If --static, filter to constraint/dependency only
    if static_only:
        filtered = []
        for f in files:
            data, kind = load_spec(f)
            if kind in ("constraint", "dependency"):
                filtered.append(f)
        files = filtered

    if target_root:
        os.environ["ARCHWRIGHT_PROJECT_ROOT"] = str(target_root)

    # Changed-only scope selection (CK-19): filter to specs affected by the
    # git diff vs --base (default HEAD = uncommitted work; CI passes e.g.
    # --base origin/main). Zero affected specs = a legitimate pass (nothing
    # changed that any spec watches); git failures are exit 2, never an
    # empty-diff false pass.
    scope_extra = None
    if changed_only:
        try:
            changed = _git_changed_files(base_ref, target_root or Path.cwd())
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(2)
        total = len(files)
        files = [f for f in files if _spec_affected(f, changed)]
        scope_extra = {"changed_only": True, "base": base_ref,
                       "specs_total": total,
                       "specs_unaffected": total - len(files)}
        if not json_output:
            print(f"  changed-only: {len(files)}/{total} spec(s) affected by diff vs {base_ref}")

    # Baseline discovery (CK-07): explicit --baseline wins; otherwise walk up
    # from the spec dirs. Missing = no suppression (never silently created).
    baseline_path = find_baseline([f.parent for f in files], explicit=baseline_arg)
    baseline_data, baseline_fps = None, None
    if baseline_arg and (baseline_path is None or not baseline_path.is_file()):
        print(f"ERROR: baseline file not found: {baseline_arg}", file=sys.stderr)
        sys.exit(2)
    if baseline_path:
        try:
            baseline_data, baseline_fps = load_baseline(baseline_path)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(2)
    if update_baseline and changed_only:
        print("ERROR: --update-baseline cannot run with --changed-only — a scoped "
              "run only re-proves the affected specs, so entries belonging to "
              "unaffected specs would read as 'resolved' and be wrongly dropped. "
              "Ratchet on full-scope runs only (same principle as the errored-run "
              "refusal: an incomplete run cannot prove a violation is gone)",
              file=sys.stderr)
        sys.exit(2)
    if update_baseline and baseline_path is None:
        print(f"ERROR: --update-baseline requires an existing {BASELINE_FILENAME} — "
              "baseline entries are created by humans, never by the tool (CK-08)",
              file=sys.stderr)
        sys.exit(2)

    # Evidence ledger (ADR 0009): explicit --evidence wins (created on write);
    # otherwise only an EXISTING file up-tree activates recording.
    evidence_path = find_evidence_ledger([f.parent for f in files], explicit=evidence_arg)
    evidence_ledger = None
    if evidence_path:
        try:
            evidence_ledger = load_evidence_ledger(evidence_path)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(2)

    per_file = []
    for f in files:
        kind, results = check_file(f)
        per_file.append((f, kind, results))
        if not json_output:
            print(format_result(f, kind, results))

    doc = build_document(mode, target_root, per_file,
                         baseline_fps=baseline_fps, baseline_path=baseline_path,
                         baseline_entries=len(baseline_data.get("entries", [])) if baseline_data else 0,
                         scope_extra=scope_extra)
    # Commit-binding (ticket 018): the git identity of the checked tree.
    code_state = _code_state(target_root or _project_root_for(files[0]))
    doc["code_state"] = code_state

    # Evidence recording (ADR 0009): errored runs prove nothing — record only
    # from clean pass/fail runs (same discipline as the baseline ratchet).
    if evidence_ledger is not None and doc["status"] != "error":
        violations_by_spec = {}
        for v in doc["violations"]:
            violations_by_spec.setdefault(v["spec_path"], {})[v["invariant"]] = v
        appended = record_evidence(evidence_ledger, per_file, violations_by_spec,
                                   code_state=code_state)
        write_evidence_ledger(evidence_path, evidence_ledger)
        doc["evidence_ledger"] = {"path": str(evidence_path),
                                  "events_appended": len(appended)}
        if not json_output and appended:
            print(f"  evidence: {len(appended)} event(s) appended to {evidence_path}")

    # Baseline ratchet (CK-08): remove entries whose violations no longer
    # reproduce; NEVER add (accepting new debt is a human decision). An errored
    # run proves nothing about absence — refuse to shrink the baseline on it.
    if update_baseline:
        if doc["status"] == "error":
            print("ERROR: run had tool errors — an errored run cannot prove a "
                  "violation is gone; baseline not updated", file=sys.stderr)
            sys.exit(2)
        live_fps = {fp for v in doc["violations"] for fp in v.get("fingerprints", [])}
        entries = baseline_data.get("entries", [])
        kept = [e for e in entries
                if isinstance(e, dict) and e.get("fingerprint") in live_fps]
        removed = len(entries) - len(kept)
        baseline_data["entries"] = kept
        baseline_path.write_text(
            json.dumps(baseline_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
        print(f"baseline: removed {removed} resolved entr{'y' if removed == 1 else 'ies'}, "
              f"kept {len(kept)} — entries only ever decrease (CK-08)", file=sys.stderr)

    if json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
    elif baseline_fps is not None:
        b = doc["baseline"]
        print(f"  baseline: {b['suppressed']} violation(s) suppressed by {b['path']} "
              f"({b['entries']} entries); remaining_delta={doc['remaining_delta']}")

    # Exit code contract (CK-04): 0 = pass, 1 = violations, 2 = tool error.
    sys.exit({"pass": 0, "fail": 1, "error": 2}[doc["status"]])


if __name__ == "__main__":
    main()
