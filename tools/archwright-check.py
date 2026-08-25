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


# Alloy behavior/contract checking — canonical source: check/alloy.py
# Tombstone re-export for parse_alloy_verdicts (ticket 096 fixture compatibility)
from check.alloy import (
    check_behavior, check_contract, parse_alloy_verdicts,
    probe_behavior, _find_alloy_jar, _alloy_field_name,
)

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


from check.trace import check_trace, translate_predicate, Untranslatable


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
