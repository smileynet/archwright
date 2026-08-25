"""Evidence ledger (ADR 0009) — read/write/dedup.

Machine evidence events (demotion/promotion candidates) are auto-appended
so confidence stops being write-once; human RATIFICATION never happens
in this file (it happens in the artifact: confidence field + Evidence line;
★★ transitions always block for HITL — ADR 0007).
"""

import sys
import json
from pathlib import Path

from check.common import _find_up


EVIDENCE_FILENAME = ".archwright-evidence.json"
PROMOTION_STREAK_DEFAULT = 5


def find_evidence_ledger(start_dirs, explicit=None):
    """Locate the evidence ledger. Explicit flag wins (missing file = will be
    created on write); otherwise only an EXISTING file activates the ledger."""
    if explicit:
        return Path(explicit)
    return _find_up(start_dirs, EVIDENCE_FILENAME)


def load_evidence_ledger(path):
    """Parse the ledger. Missing file = empty ledger (valid only under an
    explicit --evidence). Malformed JSON = ValueError (exit 2 upstream) —
    same discipline as the baseline: never guess at a corrupt ledger."""
    path = Path(path)
    if not path.is_file():
        return {"events": [], "streaks": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"cannot read evidence ledger {path}: {e}")
    if not isinstance(data, dict):
        raise ValueError(f"evidence ledger {path}: top level must be an object")
    data.setdefault("events", [])
    data.setdefault("streaks", {})
    if not isinstance(data["events"], list) or not isinstance(data["streaks"], dict):
        raise ValueError(f"evidence ledger {path}: 'events' must be a list, 'streaks' an object")
    return data


def _event_identity(ev):
    """Dedup key: identical re-observation of known evidence appends nothing;
    new evidence (fingerprints), a changed confidence, or a different reason
    is a new event. Timestamps never enter identity."""
    return (ev.get("event"), ev.get("key"), ev.get("invariant"),
            ev.get("confidence"), ev.get("reason"),
            tuple(sorted(ev.get("fingerprints") or [])))


def record_evidence(ledger, per_file, violations_by_spec, code_state=None):
    """Apply one check run to the ledger (ADR 0009). Returns events appended.

    - demotion-candidate: FAIL on a ★★ or ★ spec/invariant. Baselined
      violations emit nothing (the baseline entry IS the human adjudication);
      '—' fails emit nothing (no confidence claim to demote).
    - promotion-candidate: pass streak reaches config.promotion_streak
      (default 5) per (key, invariant) — fail resets, error/skip neither
      counts nor resets (proves nothing) — or a deeper-tier pass: a ★/—
      invariant passing a mechanical (bounded) check. ★★ never promotes.
    - Contract/pattern results are schema-only, not evidence: excluded.
    - code_state (ticket 018): appended events carry the git commit + dirty
      flag of the checked tree, like `at` — dedup identity UNCHANGED (a
      re-observation at a new commit of unchanged evidence appends nothing;
      staleness is judged by consumers, not re-recorded).
    """
    from datetime import datetime, timezone

    streak_target = ledger.get("config", {}).get(
        "promotion_streak", PROMOTION_STREAK_DEFAULT)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existing = {_event_identity(e) for e in ledger["events"]
                if isinstance(e, dict)}
    appended = []

    def _append(ev):
        if _event_identity(ev) not in existing:
            existing.add(_event_identity(ev))
            ev["at"] = now
            if code_state is not None:
                ev["code_state"] = code_state
            ledger["events"].append(ev)
            appended.append(ev)

    for spec_path, kind, results in per_file:
        if kind not in ("behavior", "constraint", "dependency"):
            continue
        doc_violations = violations_by_spec.get(str(spec_path), {})
        for r in results:
            spec_id = r.get("spec_id", "unknown")
            invariant = r.get("invariant")
            key = f"{kind}:{spec_id}"
            skey = f"{key}#{invariant}"
            conf = r.get("confidence", "—")
            status = r["status"]

            if status == "fail":
                ledger["streaks"].pop(skey, None)
                v = doc_violations.get(invariant, {})
                if v.get("baselined"):
                    continue
                if conf not in ("★★", "★"):
                    continue
                _append({
                    "event": "demotion-candidate",
                    "key": key,
                    "invariant": invariant,
                    "confidence": conf,
                    "assurance": r.get("assurance"),
                    "fingerprints": v.get("fingerprints", []),
                    "from_pattern": r.get("from_pattern"),
                    "from_force": r.get("from_force"),
                    "message": r.get("message"),
                })
            elif status == "pass":
                if conf == "★★":
                    continue  # top tier — nothing to promote toward
                # Deeper-tier pass: heuristic-confidence invariant survived a
                # mechanical check — immediate promotion candidate.
                if r.get("assurance") == "bounded":
                    _append({
                        "event": "promotion-candidate",
                        "key": key,
                        "invariant": invariant,
                        "confidence": conf,
                        "reason": "deeper-check-pass (bounded/mechanical)",
                        "fingerprints": [],
                    })
                streak = ledger["streaks"].get(skey, 0) + 1
                ledger["streaks"][skey] = streak
                if streak == streak_target:
                    _append({
                        "event": "promotion-candidate",
                        "key": key,
                        "invariant": invariant,
                        "confidence": conf,
                        "reason": f"pass-streak-{streak_target}",
                        "fingerprints": [],
                    })
            # skipped/pending/error: neither counts nor resets — proves nothing.
    return appended


def write_evidence_ledger(path, ledger):
    """Persist the ledger. A write failure after checks ran must not change
    the run's verdict: warn on stderr, exit code untouched."""
    try:
        Path(path).write_text(
            json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
        return True
    except OSError as e:
        print(f"WARNING: evidence ledger not written ({e}) — events from this "
              f"run are lost", file=sys.stderr)
        return False
