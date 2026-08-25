"""Trace replay — predicate evaluator + CK-03 document builder + check_trace."""

import json
import re
import sys
import yaml
from pathlib import Path

from check.common import _SEVERITY, _expected_for, _code_state, _project_root_for
from check.ledger import find_evidence_ledger, load_evidence_ledger, record_evidence, write_evidence_ledger
from archwright_common import state_events


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
    """Sentinel: a predicate the translator cannot evaluate (ticket 015).

    Returned instead of a silent True so callers can SKIP-with-reason.
    Refuses bool() coercion so unaudited call sites fail loudly.
    """
    def __init__(self, reason):
        self.reason = reason

    def __bool__(self):
        raise TypeError(f"Untranslatable predicate used as bool: {self.reason}")


def _unquote(token):
    """Strip matching quotes from an enum literal."""
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token


def translate_predicate(pred, state, current_spec_state=None):
    """Evaluate a spec predicate against a state dict.

    Returns True, False, or Untranslatable (three-valued — Kleene semantics).
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
        return r

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

    if current_spec_state is not None and re.match(r"^[a-z][a-z0-9_-]*$", pred):
        return pred == current_spec_state

    if pred in state:
        return bool(state[pred])

    return Untranslatable(f"unsupported predicate construct: '{pred}'")


def build_trace_document(spec_path, payload, data=None, active_invariants=None):
    """Ticket 016: map a trace result payload into the CK-03 document shape."""
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
        else:
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

    Exit codes: 0 pass / 1 fail / 2 error.
    """
    spec_path = Path(spec_path)
    trace_path = Path(trace_path)

    data = None
    active_invariants = []
    evidence_path = None
    evidence_ledger = None

    def _maybe_record(payload, code):
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

    states = data.get("states", {})
    invariants = data.get("invariants", [])
    initial_state = data.get("initial", "")
    check_block = data.get("check", {}).get("trace", {})
    check_invariant_ids = check_block.get("invariants", [inv["id"] for inv in invariants])

    active_invariants = [inv for inv in invariants if inv["id"] in check_invariant_ids]

    current_state = initial_state
    skipped_invariants = {}
    guards_skipped = []

    def _fail(payload):
        payload["invariants_skipped"] = [{"id": k, "reason": v}
                                         for k, v in skipped_invariants.items()]
        if guards_skipped:
            payload["guards_skipped"] = guards_skipped
        return _emit(payload, 1)

    for i, entry in enumerate(trace):
        event = entry.get("event", "")
        state_snapshot = entry.get("state", {})
        clock = entry.get("clock", i)

        if i == 0:
            if event != "INITIAL":
                return _fail({
                    "status": "fail", "assurance": "trace", "spec_id": data["id"],
                    "violation": {
                        "type": "protocol", "position": 0, "clock": clock,
                        "message": f"First trace event must be INITIAL, got '{event}'"
                    }
                })
            for inv in active_invariants:
                res = translate_predicate(inv["predicate"], state_snapshot, current_state)
                if isinstance(res, Untranslatable):
                    skipped_invariants.setdefault(inv["id"], res.reason)
                    continue
                if not res:
                    return _fail({
                        "status": "fail", "assurance": "trace", "spec_id": data["id"],
                        "violation": {
                            "invariant": inv["id"], "position": 0, "clock": clock,
                            "event": "INITIAL", "state": state_snapshot,
                            "expected": inv["predicate"],
                            "message": f"Invariant '{inv['id']}' violated at INITIAL state"
                        },
                        "provenance": {"from_force": inv.get("from_force"),
                                       "from_pattern": inv.get("from_pattern")}
                    })
            continue

        current_state_def = states.get(current_state, {})
        transitions = state_events(current_state_def)

        if event not in transitions:
            valid_events = list(transitions.keys())
            return _fail({
                "status": "fail", "assurance": "trace", "spec_id": data["id"],
                "violation": {
                    "type": "transition",
                    "invariant": f"valid-transition-from-{current_state}",
                    "position": i, "clock": clock, "event": event,
                    "state": state_snapshot, "current_spec_state": current_state,
                    "valid_events": valid_events,
                    "message": f"No transition for event '{event}' in state '{current_state}'. Valid: {valid_events}"
                },
                "provenance": {"from_force": current_state_def.get("from_force"),
                               "from_pattern": current_state_def.get("from_pattern")}
            })

        transition = transitions[event]
        if isinstance(transition, dict):
            transition = [transition]
        elif not isinstance(transition, list):
            transition = [{"target": str(transition)}]

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
                    guards_skipped.append({
                        "position": i, "event": event,
                        "predicate": guard_pred, "reason": g.reason,
                    })
                elif not g:
                    continue

            current_state = trans.get("target", current_state)
            transition_taken = True
            break

        if not transition_taken:
            return _fail({
                "status": "fail", "assurance": "trace", "spec_id": data["id"],
                "violation": {
                    "type": "guard", "position": i, "clock": clock,
                    "event": event, "state": state_snapshot,
                    "prev_state": prev_state, "current_spec_state": current_state,
                    "message": f"All guards failed for event '{event}' in state '{current_state}'"
                }
            })

        for inv in active_invariants:
            if inv["id"] in skipped_invariants:
                continue
            res = translate_predicate(inv["predicate"], state_snapshot, current_state)
            if isinstance(res, Untranslatable):
                skipped_invariants.setdefault(inv["id"], res.reason)
                continue
            if not res:
                return _fail({
                    "status": "fail", "assurance": "trace", "spec_id": data["id"],
                    "violation": {
                        "invariant": inv["id"], "position": i, "clock": clock,
                        "event": event, "state": state_snapshot,
                        "current_spec_state": current_state,
                        "expected": inv["predicate"],
                        "message": f"Invariant '{inv['id']}' violated after event '{event}' at position {i}"
                    },
                    "provenance": {"from_force": inv.get("from_force"),
                                   "from_pattern": inv.get("from_pattern")}
                })

    result = {
        "status": "pass", "assurance": "trace", "spec_id": data["id"],
        "steps_checked": len(trace), "final_state": current_state,
        "invariants_checked": [inv["id"] for inv in active_invariants
                               if inv["id"] not in skipped_invariants],
        "invariants_skipped": [{"id": k, "reason": v}
                               for k, v in skipped_invariants.items()],
    }
    if guards_skipped:
        result["guards_skipped"] = guards_skipped
    return _emit(result, 0)
