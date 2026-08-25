"""Alloy behavior + contract checking, verdict parsing, and non-vacuity probe."""

import os
import re
import subprocess
import sys
import yaml
from pathlib import Path

from check.common import SCRIPT_DIR, _fingerprint_base, load_spec
from check.conformance import check_conformance
from archwright_common import state_events


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
    """Check a contract spec: structural_invariants via Alloy + check section via conformance."""
    results = []
    has_structural = bool(data.get("structural_invariants"))
    has_check = bool(data.get("check"))

    if not has_structural and not has_check:
        return [{"invariant": data.get("id", "?"), "status": "pass",
                 "message": "contract validation: schema only (no runtime check)"}]

    if has_structural:
        results.extend(_check_structural_invariants(data, spec_path))

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


def probe_behavior(spec_path):
    """Non-vacuity probe: replace invariants with a false one, verify it FAILs.

    Exit meaning: 0 = probe produced a counterexample (checker non-vacuous),
    1 = probe PASSED (model vacuous), 2 = tool error / not probeable.
    """
    import tempfile

    data, kind = load_spec(Path(spec_path))
    if kind != "behavior":
        print(f"Error: --probe requires a behavior spec (got kind: {kind})")
        return 2

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
