"""Coverage reporting — trace-coverage and spec-coverage modes."""

import sys
import json
import yaml
from pathlib import Path

from check.common import load_spec, _project_root_for


def trace_coverage_report(specs_dir, traces_dir, json_output=False):
    """Report which behavior spec scenarios have matching trace files.

    Matches traces to specs by spec_id field in the trace JSON or by filename
    convention (stem contains the spec id slug). Reports covered/uncovered
    scenarios and orphan traces.

    Exit codes: 0 = all covered, 1 = gaps exist, 2 = error.
    """
    specs_path = Path(specs_dir)
    traces_path = Path(traces_dir)

    if not specs_path.exists():
        msg = f"Specs directory not found: {specs_path}"
        if json_output:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    # Collect traces. Association is by explicit spec_id/spec field (enveloped
    # dict shape) or by filename convention (canonical bare-array shape per
    # trace-schema.ts — the content carries no spec identity; ticket 030/043).
    trace_files = list(traces_path.glob("*.json")) if traces_path.exists() else []
    traces = []
    for tf in trace_files:
        try:
            data = json.loads(tf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data, dict):
            sid = data.get("spec_id", "") or data.get("spec", "")
            source = data.get("source", tf.stem)
        elif isinstance(data, list):
            sid = ""
            source = tf.stem
        else:
            continue
        traces.append({"sid": sid, "source": source, "stem": tf.stem})

    def _slug(s):
        return s.lower().replace(" ", "_").replace("-", "_")

    claimed = set()

    total_scenarios = 0
    covered_scenarios = 0
    spec_reports = []

    for f in sorted(specs_path.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError):
            continue
        if not isinstance(data, dict) or data.get("kind") != "behavior":
            continue
        spec_id = data.get("id", "")
        scenarios = data.get("scenarios", [])
        spec_slug = _slug(spec_id) if spec_id else ""
        traces_for_spec = []
        for t in traces:
            if t["sid"] == spec_id or (
                not t["sid"] and spec_slug and spec_slug in _slug(t["stem"])
            ):
                traces_for_spec.append(t["source"])
                claimed.add(t["stem"])

        scenario_results = []
        for s in scenarios:
            total_scenarios += 1
            name = s.get("name", "unnamed")
            name_slug = name.lower().replace(" ", "_").replace("-", "_")
            matched = any(name_slug in t.lower().replace("-", "_") for t in traces_for_spec)
            if matched:
                covered_scenarios += 1
            scenario_results.append({"name": name, "covered": matched})

        spec_reports.append({
            "spec_id": spec_id,
            "trace_count": len(traces_for_spec),
            "scenario_count": len(scenarios),
            "scenarios": scenario_results,
        })

    # Orphan traces: never claimed by any loaded spec (explicit sid with no
    # matching spec, or a bare-array trace whose filename matches no spec id)
    orphan_traces = sorted(
        {t["sid"] or t["stem"] for t in traces if t["stem"] not in claimed}
    )

    status = "pass" if covered_scenarios == total_scenarios else "fail"

    if json_output:
        doc = {
            "status": status,
            "scope": {"mode": "trace-coverage",
                      "specs_dir": str(specs_path),
                      "traces_dir": str(traces_path)},
            "summary": {
                "total_scenarios": total_scenarios,
                "covered": covered_scenarios,
                "uncovered": total_scenarios - covered_scenarios,
                "orphan_traces": orphan_traces,
            },
            "specs": spec_reports,
        }
        print(json.dumps(doc, indent=2, ensure_ascii=False))
    else:
        print("# Trace Coverage Report\n")
        for r in spec_reports:
            print(f"## {r['spec_id']} ({r['trace_count']} trace(s) / {r['scenario_count']} scenario(s))")
            for s in r["scenarios"]:
                icon = "✅" if s["covered"] else "❌"
                print(f"  {icon} {s['name']}")
            print()
        if orphan_traces:
            print(f"## Orphan traces (no matching spec): {', '.join(orphan_traces)}\n")
        print(f"## Summary: {covered_scenarios}/{total_scenarios} scenarios covered by traces")

    return 0 if status == "pass" else 1


def coverage_report(specs_dir, target_root=None, json_output=False):
    """Report spec→implementation coverage: which specs have their check.target
    present in the project and which are spec-ahead (target missing/empty).

    This is informational — exit code is always 0 on success, 2 on error.
    """
    specs_path = Path(specs_dir)
    if not specs_path.exists():
        msg = f"Specs directory not found: {specs_path}"
        if json_output:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    if target_root:
        project_root = Path(target_root)
    else:
        project_root = _project_root_for(specs_path)

    implemented = []
    spec_ahead = []
    no_target = []

    all_files = sorted(list(specs_path.rglob("*.yaml")) + list(specs_path.rglob("*.md")))

    for f in all_files:
        try:
            data, kind = load_spec(f)
        except Exception:
            continue
        if not isinstance(data, dict) or not kind:
            continue
        spec_id = data.get("id", "")
        check = data.get("check", {})
        target = check.get("target", "")

        if not target:
            no_target.append({"kind": kind, "id": spec_id})
            continue

        targets = target if isinstance(target, list) else [target]
        any_exists = False
        for t in targets:
            tp = project_root / t
            if tp.exists() and (tp.is_file() or (tp.is_dir() and any(tp.iterdir()))):
                any_exists = True
                break

        entry = {"kind": kind, "id": spec_id, "target": target}
        if any_exists:
            implemented.append(entry)
        else:
            spec_ahead.append(entry)

    total = len(implemented) + len(spec_ahead) + len(no_target)

    if json_output:
        doc = {
            "status": "pass",
            "scope": {"mode": "coverage", "specs_dir": str(specs_path),
                      "target_root": str(project_root)},
            "summary": {
                "total": total,
                "implemented": len(implemented),
                "spec_ahead": len(spec_ahead),
                "no_target": len(no_target),
            },
            "implemented": [f"{e['kind']}:{e['id']}" for e in implemented],
            "spec_ahead": [f"{e['kind']}:{e['id']} (target: {e['target']})" for e in spec_ahead],
            "no_target": [f"{e['kind']}:{e['id']}" for e in no_target],
        }
        print(json.dumps(doc, indent=2, ensure_ascii=False))
    else:
        print(f"# Spec Coverage Report: {specs_path}")
        print(f"  Project root: {project_root}\n")
        print(f"## Implemented ({len(implemented)})")
        for e in implemented:
            print(f"  ✓ {e['kind']}:{e['id']}")
        print()
        if spec_ahead:
            print(f"## Spec-Ahead ({len(spec_ahead)})")
            for e in spec_ahead:
                print(f"  ⚠ {e['kind']}:{e['id']} (target: {e['target']})")
            print()
        if no_target:
            print(f"## No Check Target ({len(no_target)})")
            for e in no_target:
                print(f"  ○ {e['kind']}:{e['id']}")
            print()
        print(f"## Summary: {len(implemented)}/{total} specs have matching implementation")

    return 0
