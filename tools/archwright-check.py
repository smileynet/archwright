#!/usr/bin/env python3
"""archwright-check: Run verification checks against specs.

Usage:
  archwright-check <spec-file>...                Check individual specs
  archwright-check --all <dir>                   Check all specs in directory
  archwright-check --static <dir> [--target <root>]   Check constraint/dependency specs only
  archwright-check --trace <spec.yaml> <trace.json>   Validate a trace against a behavior spec

Dispatches by spec kind:
  behavior    → compile to Alloy, run model checker (if alloy6.jar available)
  constraint  → execute self-described check (grep, semgrep, script)
  dependency  → execute self-described check (grep, script)
  contract    → schema validation only (for now)
"""

import sys
import os
import re
import yaml
import subprocess
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def extract_frontmatter(path):
    """Extract YAML frontmatter from a markdown file."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


def load_spec(path):
    """Load a spec file, return (data, kind)."""
    path = Path(path)
    if path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data, data.get("kind")
    elif path.suffix == ".md":
        data = extract_frontmatter(path)
        if data:
            return data, data.get("kind")
    return None, None


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


def _alloy_field_name(name):
    """Mirror archwright-compile-alloy's _to_field: slug → camelCase assert name."""
    parts = name.replace("-", "_").split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def check_conformance(data, spec_path):
    """Check a constraint or dependency spec using its self-described check field."""
    check = data.get("check")
    if not check:
        return [{
            "invariant": data.get("id", "unknown"),
            "status": "skipped",
            "message": "No 'check' field in spec — cannot verify",
        }]

    method = check.get("method", "")
    spec_id = data.get("id", "unknown")
    confidence = data.get("confidence", "—")

    # Specs whose check target doesn't exist yet (system not implemented) declare
    # target_status: pending — report as skipped, not failed (see archwright-derive skill).
    if check.get("target_status") == "pending":
        return [{
            "invariant": spec_id,
            "status": "skipped",
            "confidence": confidence,
            "message": "target_status: pending — check target not yet implemented; activates when it exists",
        }]


    # Determine the working directory (look for project root)
    # Honor ARCHWRIGHT_PROJECT_ROOT env var if set, otherwise auto-detect
    env_root = os.environ.get("ARCHWRIGHT_PROJECT_ROOT")
    if env_root:
        project_root = Path(env_root)
    else:
        spec_dir = Path(spec_path).resolve().parent
        project_root = spec_dir
        for _ in range(5):
            if (project_root / "design").exists() or (project_root / "project.godot").exists():
                break
            project_root = project_root.parent

    if method == "grep":
        return _check_grep(check, spec_id, confidence, project_root)
    elif method == "script":
        return _check_script(check, spec_id, confidence, project_root)
    elif method == "semgrep":
        return _check_semgrep(check, spec_id, confidence, project_root)
    else:
        return [{
            "invariant": spec_id,
            "status": "error",
            "message": f"Unknown check method: {method}",
        }]


def _find_bash():
    """Locate a bash for command-mode checks (Git bash on Windows puts GNU grep on PATH)."""
    import shutil
    b = shutil.which("bash")
    if b:
        return b
    git = shutil.which("git")
    if git:
        cand = Path(git).parent.parent / "bin" / "bash.exe"
        if cand.exists():
            return str(cand)
    return None


_SKIP_DIRS = {".git", "Library", "Temp", "obj", "Build", ".vs", ".idea", "PackageCache", "node_modules"}

# Line-comment tokens per extension — a constraint keyword appearing only in a
# comment must not match (CK-05/B4). Heuristic truncation (not string-aware):
# Tier-1 grep is ★-grade conformance, documented as such.
_LINE_COMMENT = {
    ".gd": "#", ".py": "#", ".sh": "#", ".bash": "#", ".yaml": "#", ".yml": "#",
    ".toml": "#", ".rb": "#",
    ".ts": "//", ".tsx": "//", ".js": "//", ".jsx": "//", ".mjs": "//",
    ".cs": "//", ".c": "//", ".cpp": "//", ".h": "//", ".hpp": "//",
    ".java": "//", ".kt": "//", ".rs": "//", ".go": "//", ".swift": "//",
}


def _python_grep(target_path, pattern, project_root=None, strip_comments=True):
    """Portable grep replacement: regex search over text files. Returns 'path:line:text' lines.
    Paths are emitted project-relative with forward slashes so only-in filters match portably.
    By default the comment portion of each line is stripped before matching (per-extension
    line-comment tokens) so commented-out code never triggers a constraint."""
    rx = re.compile(pattern)
    out = []
    paths = [target_path] if target_path.is_file() else None
    if paths is None:
        paths = []
        for p in target_path.rglob("*"):
            if p.is_file() and not (set(p.parts) & _SKIP_DIRS):
                paths.append(p)
    for p in paths:
        try:
            if p.stat().st_size > 5_000_000:
                continue
            with open(p, "rb") as f:
                head = f.read(8192)
                if b"\x00" in head:
                    continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        try:
            shown = p.relative_to(project_root).as_posix() if project_root else p.as_posix()
        except ValueError:
            shown = p.as_posix()
        comment_token = _LINE_COMMENT.get(p.suffix) if strip_comments else None
        for i, line in enumerate(text.splitlines(), 1):
            haystack = line.split(comment_token, 1)[0] if comment_token and comment_token in line else line
            if rx.search(haystack):
                out.append(f"{shown}:{i}:{line.strip()[:200]}")
    return "\n".join(out)


def _check_grep(check, spec_id, confidence, project_root):
    """Run a grep-based check (pure-Python for target+pattern; bash for custom commands)."""
    target = check.get("target", ".")
    pattern = check.get("pattern", "")
    expect = check.get("expect", "absent")
    command = check.get("command")
    only_in = check.get("only_in")

    # Unknown expect values are a TOOL ERROR, never a silent pass (CK-05/B4, A1/F3).
    if expect not in ("absent", "present", "only-in"):
        return [{"invariant": spec_id, "status": "error",
                 "message": f"unknown expect value '{expect}' — must be absent|present|only-in"}]
    if expect == "only-in" and not only_in:
        return [{"invariant": spec_id, "status": "error",
                 "message": "expect: only-in requires an only_in: key naming the allowed location"}]

    if command:
        # Custom command: prefer bash (grep/coreutils available), fall back to system shell.
        bash = _find_bash()
        try:
            if bash:
                result = subprocess.run(
                    [bash, "-c", command], capture_output=True, text=True,
                    cwd=str(project_root)
                )
            else:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True,
                    cwd=str(project_root)
                )
            # Loud failure: interpreter/tool missing must never read as "no matches".
            err = (result.stderr or "").lower()
            if result.returncode > 1 or "not recognized" in err or "command not found" in err:
                return [{"invariant": spec_id, "status": "error",
                         "message": f"check command failed (rc {result.returncode}): {(result.stderr or '')[:200]}"}]
            matches = result.stdout.strip()
        except Exception as e:
            return [{"invariant": spec_id, "status": "error", "message": str(e)}]
    else:
        target_path = project_root / target
        if not target_path.exists():
            return [{"invariant": spec_id, "status": "error",
                     "message": f"Target path not found: {target_path}"}]
        try:
            matches = _python_grep(target_path, pattern, project_root,
                                   strip_comments=not check.get("include_comments", False))
        except re.error as e:
            return [{"invariant": spec_id, "status": "error",
                     "message": f"invalid pattern: {e}"}]

    # Interpret results based on expect
    if expect == "absent":
        if matches:
            lines = matches.split("\n")
            return [{
                "invariant": spec_id,
                "status": "fail",
                "confidence": confidence,
                "assurance": "conformance",
                "message": f"Found {len(lines)} match(es) — expected none",
                "violations": [l.strip() for l in lines[:5]],
                "from_pattern": _first_pattern(check),
            }]
        else:
            return [{"invariant": spec_id, "status": "pass", "assurance": "conformance"}]

    elif expect == "present":
        if matches:
            return [{"invariant": spec_id, "status": "pass"}]
        else:
            return [{
                "invariant": spec_id,
                "status": "fail",
                "confidence": confidence,
                "message": "Expected match not found",
            }]

    elif expect == "only-in":
        if not matches:
            return [{"invariant": spec_id, "status": "pass",
                     "message": "No matches found (vacuously satisfied)"}]
        lines = matches.split("\n")
        violations = [l for l in lines if only_in not in l]
        if violations:
            return [{
                "invariant": spec_id,
                "status": "fail",
                "confidence": confidence,
                "assurance": "conformance",
                "message": f"Found {len(violations)} match(es) outside {only_in}",
                "violations": [v.strip() for v in violations[:5]],
            }]
        else:
            return [{"invariant": spec_id, "status": "pass", "assurance": "conformance"}]

    # Unreachable: expect validated above.
    return [{"invariant": spec_id, "status": "error",
             "message": f"unhandled expect value '{expect}'"}]


def _check_script(check, spec_id, confidence, project_root):
    """Run a script-based check."""
    command = check.get("command", "")
    expect = check.get("expect", "absent")

    try:
        bash = _find_bash()
        if bash:
            result = subprocess.run(
                [bash, "-c", command], capture_output=True, text=True,
                cwd=str(project_root)
            )
        else:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                cwd=str(project_root)
            )
        err = (result.stderr or "").lower()
        if result.returncode > 1 or "not recognized" in err or "command not found" in err:
            return [{"invariant": spec_id, "status": "error",
                     "message": f"check script failed (rc {result.returncode}): {(result.stderr or '')[:200]}"}]
        output = result.stdout.strip()
    except Exception as e:
        return [{"invariant": spec_id, "status": "error", "message": str(e)}]

    if expect == "absent":
        if output:
            return [{
                "invariant": spec_id, "status": "fail", "confidence": confidence,
                "message": f"Script produced output — expected none",
                "violations": output.split("\n")[:5],
            }]
        return [{"invariant": spec_id, "status": "pass"}]
    elif expect == "present":
        if output:
            return [{"invariant": spec_id, "status": "pass"}]
        return [{
            "invariant": spec_id, "status": "fail", "confidence": confidence,
            "message": "Script produced no output — expected some",
        }]

    return [{"invariant": spec_id, "status": "pass"}]


def _check_semgrep(check, spec_id, confidence, project_root):
    """Run a semgrep-based check (placeholder)."""
    return [{
        "invariant": spec_id, "status": "skipped",
        "message": "semgrep checks not yet implemented",
    }]


def _first_pattern(check):
    """Extract from_pattern context if available."""
    return check.get("from_pattern", None)


_SEVERITY = {"★★": "error", "★": "warning", "—": "info"}


def _extract_section(md_path, header):
    """Extract the body of a '## <header>' section from a markdown spec."""
    try:
        text = Path(md_path).read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(rf"^##\s+{re.escape(header)}\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else None


def _expected_for(r, data, spec_path):
    """The 'expected' side of a contrast pair: the rule as the design states it."""
    if Path(spec_path).suffix == ".md":
        rule = _extract_section(spec_path, "Rule")
        if rule:
            return rule
    # Behavior specs: the violated invariant's own description + predicate
    for inv in data.get("invariants", []):
        if inv.get("id") == r.get("invariant"):
            desc = inv.get("description", "")
            pred = inv.get("predicate", "")
            return f"{desc} ({pred})" if desc else pred
    return data.get("user_story") or data.get("id", "")


def enrich_results(results, data, spec_path):
    """CK-09/CK-10: attach spec_id, severity, escalate, provenance,
    suggested_route, and contrast_pair to results."""
    from_patterns = data.get("from_patterns", [])
    default_pattern = from_patterns[0] if from_patterns else None
    default_force = data.get("from_force") or data.get("protects_experience")

    for r in results:
        r.setdefault("spec_id", data.get("id", "unknown"))
        if r["status"] == "fail":
            conf = r.get("confidence") or data.get("confidence", "—")
            r["confidence"] = conf
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
    all_skip = all(r["status"] == "skipped" for r in results)
    skips = [r for r in results if r["status"] == "skipped"]

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
        lines.append(f"  ○ SKIP: {path.name} (kind: {kind})")
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
        results = [{"invariant": data.get("id", "?"), "status": "pass",
                    "message": "contract validation: schema only (no runtime check)"}]
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


def translate_predicate(pred, state, current_spec_state=None):
    """Evaluate a spec predicate against a state dict."""
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
        return not translate_predicate(pred[4:], state, current_spec_state)

    # Binary operators (lowest precedence first, respecting braces/parens)
    idx = _find_op(pred, " implies ")
    if idx >= 0:
        lhs, rhs = pred[:idx].strip(), pred[idx+9:].strip()
        return not translate_predicate(lhs, state, current_spec_state) or translate_predicate(rhs, state, current_spec_state)

    idx = _find_op(pred, " or ")
    if idx >= 0:
        return any(translate_predicate(p, state, current_spec_state) for p in _split_op(pred, " or "))

    idx = _find_op(pred, " and ")
    if idx >= 0:
        return all(translate_predicate(p, state, current_spec_state) for p in _split_op(pred, " and "))

    # Atoms
    if " in {" in pred:
        match = re.match(r"(\w+)\s+in\s+\{([^}]+)\}", pred)
        if match:
            var = match.group(1)
            values = [v.strip() for v in match.group(2).split(",")]
            actual = str(state.get(var, ""))
            return actual in values

    if " == " in pred:
        lhs, rhs = pred.split(" == ", 1)
        lval = str(state.get(lhs.strip(), lhs.strip()))
        rval = str(state.get(rhs.strip(), rhs.strip()))
        return lval == rval

    if " != " in pred:
        lhs, rhs = pred.split(" != ", 1)
        lval = str(state.get(lhs.strip(), lhs.strip()))
        rval = str(state.get(rhs.strip(), rhs.strip()))
        return lval != rval

    # Bare identifier: state name reference
    if current_spec_state is not None and re.match(r"^[a-z][a-z0-9-]*$", pred):
        return pred == current_spec_state

    if pred in state:
        return bool(state[pred])

    return True


def check_trace(spec_path, trace_path):
    """Validate a JSON trace against a behavior spec."""
    spec_path = Path(spec_path)
    trace_path = Path(trace_path)
    
    # Load spec
    if spec_path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    else:
        print(json.dumps({"status": "error", "message": "Trace checking requires a YAML behavior spec"}))
        return 2
    
    if data.get("kind") != "behavior":
        print(json.dumps({"status": "error", "message": f"Expected kind: behavior, got: {data.get('kind')}"}))
        return 2
    
    # Load trace
    try:
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(json.dumps({"status": "error", "message": f"Failed to parse trace: {e}"}))
        return 2
    
    if not isinstance(trace, list) or len(trace) == 0:
        print(json.dumps({"status": "error", "message": "Trace must be a non-empty JSON array"}))
        return 2
    
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
    
    for i, entry in enumerate(trace):
        event = entry.get("event", "")
        state_snapshot = entry.get("state", {})
        clock = entry.get("clock", i)
        
        # First entry: validate initial state
        if i == 0:
            if event != "INITIAL":
                print(json.dumps({
                    "status": "fail",
                    "assurance": "trace",
                    "spec_id": data["id"],
                    "violation": {
                        "type": "protocol",
                        "position": 0,
                        "clock": clock,
                        "message": f"First trace event must be INITIAL, got '{event}'"
                    }
                }))
                return 1
            # Check invariants at initial state
            for inv in active_invariants:
                if not translate_predicate(inv["predicate"], state_snapshot, current_state):
                    print(json.dumps({
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
                    }))
                    return 1
            continue
        
        # Find valid transition from current state
        current_state_def = states.get(current_state, {})
        # YAML parses 'on:' as True (boolean) — handle both
        transitions = current_state_def.get("on") or current_state_def.get(True, {})
        
        if event not in transitions:
            valid_events = list(transitions.keys())
            print(json.dumps({
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
            }))
            return 1
        
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
                if not translate_predicate(guard_pred, prev_state, current_state):
                    continue  # Guard failed, try next
            
            # Transition accepted
            current_state = trans.get("target", current_state)
            transition_taken = True
            break
        
        if not transition_taken:
            print(json.dumps({
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
            }))
            return 1
        
        # Check invariants after transition
        for inv in active_invariants:
            if not translate_predicate(inv["predicate"], state_snapshot, current_state):
                print(json.dumps({
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
                }))
                return 1
    
    # All steps passed
    print(json.dumps({
        "status": "pass",
        "assurance": "trace",
        "spec_id": data["id"],
        "steps_checked": len(trace),
        "final_state": current_state,
        "invariants_checked": [inv["id"] for inv in active_invariants]
    }))
    return 0


def build_document(mode, target_root, per_file):
    """Build the CK-03 output document from per-file results.

    Schema: status, scope, violations[], coverage, remaining_delta.
    Each violation carries spec_id, invariant, confidence, severity, escalate,
    from_pattern, from_force, suggested_route, contrast_pair, evidence.
    """
    violations = []
    errors = []
    coverage = {"checked": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0, "pending": 0}

    for spec_path, kind, results in per_file:
        coverage["checked"] += 1
        statuses = {r["status"] for r in results}
        if "fail" in statuses:
            coverage["failed"] += 1
        elif "error" in statuses:
            coverage["errors"] += 1
        elif statuses == {"skipped"}:
            coverage["skipped"] += 1
            if any("pending" in r.get("message", "") for r in results):
                coverage["pending"] += 1
        else:
            coverage["passed"] += 1

        for r in results:
            if r["status"] == "fail":
                violations.append({
                    "spec_id": r.get("spec_id"),
                    "spec_kind": kind,
                    "spec_path": str(spec_path),
                    "invariant": r.get("invariant"),
                    "confidence": r.get("confidence", "—"),
                    "severity": r.get("severity", "info"),
                    "escalate": r.get("escalate", False),
                    "message": r.get("message"),
                    "evidence": r.get("violations", []),
                    "from_pattern": r.get("from_pattern"),
                    "from_force": r.get("from_force"),
                    "suggested_route": r.get("suggested_route"),
                    "contrast_pair": r.get("contrast_pair"),
                })
            elif r["status"] == "error":
                errors.append({
                    "spec_id": r.get("spec_id"),
                    "spec_path": str(spec_path),
                    "message": r.get("message"),
                    "suggested_route": r.get("suggested_route", "fix-check"),
                })

    if errors:
        status = "error"
    elif violations:
        status = "fail"
    else:
        status = "pass"

    return {
        "status": status,
        "scope": {"mode": mode, "specs_checked": coverage["checked"],
                  "target": str(target_root) if target_root else None},
        "violations": violations,
        "errors": errors,
        "coverage": coverage,
        # Baseline suppression arrives with CK-07; until then delta = all violations.
        "remaining_delta": len(violations),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: archwright-check <spec>... | --all <dir> | --static <dir> [--target <root>] | --trace <spec> <trace>")
        sys.exit(2)

    # Handle --trace mode early (different flow)
    if sys.argv[1] == "--trace":
        if len(sys.argv) < 4:
            print(json.dumps({"status": "error", "message": "Usage: archwright-check --trace <spec.yaml> <trace.json>"}))
            sys.exit(2)
        sys.exit(check_trace(sys.argv[2], sys.argv[3]))

    files = []
    target_root = None
    static_only = False
    json_output = False
    mode = "files"

    # Parse args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--all":
            mode = "all"
            i += 1
            if i < len(args):
                directory = Path(args[i])
                files = sorted(
                    [f for f in directory.rglob("*") if f.suffix in (".yaml", ".yml", ".md")]
                )
        elif args[i] == "--static":
            static_only = True
            mode = "static"
            i += 1
            if i < len(args):
                directory = Path(args[i])
                files = sorted(
                    [f for f in directory.rglob("*") if f.suffix in (".yaml", ".yml", ".md")]
                )
        elif args[i] == "--target":
            i += 1
            if i < len(args):
                target_root = Path(args[i]).resolve()
        elif args[i] == "--json":
            json_output = True
        else:
            files.append(Path(args[i]))
        i += 1

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

    per_file = []
    for f in files:
        kind, results = check_file(f)
        per_file.append((f, kind, results))
        if not json_output:
            print(format_result(f, kind, results))

    doc = build_document(mode, target_root, per_file)
    if json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))

    # Exit code contract (CK-04): 0 = pass, 1 = violations, 2 = tool error.
    sys.exit({"pass": 0, "fail": 1, "error": 2}[doc["status"]])


if __name__ == "__main__":
    main()
