"""Check backends: grep, script, semgrep — the cycle-breaker module.

This module is imported by both check/alloy.py (for contract specs' check
sections) and the CLI dispatch layer (for constraint/dependency specs).
Neither imports the other — breaking the former alloy↔backends cycle.
"""

import fnmatch
import json
import os
import re
import subprocess
import sys
import yaml
from pathlib import Path

from check.common import _EVIDENCE_CAP, _project_root_for


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
    # target_status: pending — a distinct status (CK-06): reported as
    # coverage.pending, never pass or fail (see archwright-derive skill).
    if check.get("target_status") == "pending":
        return [{
            "invariant": spec_id,
            "status": "pending",
            "confidence": confidence,
            "message": "target_status: pending — check target not yet implemented; activates when it exists",
        }]

    project_root = _project_root_for(spec_path)

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


def _include_match(path, include_globs, project_root=None):
    """True if the file matches any include glob. Bare globs match the file name;
    globs containing '/' match the project-relative POSIX path."""
    rel = None
    if project_root:
        try:
            rel = path.relative_to(project_root).as_posix()
        except ValueError:
            rel = path.as_posix()
    for g in include_globs:
        if "/" in g:
            if rel and fnmatch.fnmatch(rel, g):
                return True
        elif fnmatch.fnmatch(path.name, g):
            return True
    return False


def _python_grep(target_path, pattern, project_root=None, strip_comments=True, include=None):
    """Portable grep replacement: regex search over text files. Returns 'path:line:text' lines.
    Paths are emitted project-relative with forward slashes so only-in filters match portably.
    By default the comment portion of each line is stripped before matching (per-extension
    line-comment tokens) so commented-out code never triggers a constraint.
    `include`: optional list of globs limiting which files are searched (ticket 005) — a bare
    glob (`*.cs`) matches the file name; a glob containing `/` matches the project-relative
    POSIX path. Explicitly-named single-file targets are NOT filtered (unlike GNU grep
    --include, which silently filters those too — the field false-pass gotcha).
    Returns (matches_str, files_scanned) — the scan count lets callers detect vacuous
    absence claims (ticket 012: scanned nothing = proved nothing)."""
    rx = re.compile(pattern)
    out = []
    files_scanned = 0
    single_file = target_path.is_file()
    paths = [target_path] if single_file else None
    if paths is None:
        paths = []
        for p in target_path.rglob("*"):
            try:
                rel_parts = set(p.relative_to(target_path).parts)
            except ValueError:
                rel_parts = set(p.parts)
            if p.is_file() and not (rel_parts & _SKIP_DIRS):
                paths.append(p)
    for p in paths:
        if include and not single_file and not _include_match(p, include, project_root):
            continue
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
        files_scanned += 1
        try:
            shown = p.relative_to(project_root).as_posix() if project_root else p.as_posix()
        except ValueError:
            shown = p.as_posix()
        comment_token = _LINE_COMMENT.get(p.suffix) if strip_comments else None
        for i, line in enumerate(text.splitlines(), 1):
            if comment_token and comment_token in line:
                cpos = line.find(comment_token)
                if not any(m.start() < cpos for m in rx.finditer(line)):
                    continue
            elif not rx.search(line):
                continue
            out.append(f"{shown}:{i}:{line.strip()[:200]}")
    return "\n".join(out), files_scanned


def _check_grep(check, spec_id, confidence, project_root):
    """Run a grep-based check (pure-Python for target+pattern; bash for custom commands)."""
    target = check.get("target", ".")
    pattern = check.get("pattern", "")
    expect = check.get("expect", "absent")
    command = check.get("command")
    only_in = check.get("only_in")
    include = check.get("include")
    if isinstance(include, str):
        include = [include]

    if expect not in ("absent", "present", "only-in"):
        return [{"invariant": spec_id, "status": "error",
                 "message": f"unknown expect value '{expect}' — must be absent|present|only-in"}]
    if expect == "only-in" and not only_in:
        return [{"invariant": spec_id, "status": "error",
                 "message": "expect: only-in requires an only_in: key naming the allowed location"}]
    if include is not None and (not isinstance(include, list) or not all(isinstance(g, str) for g in include)):
        return [{"invariant": spec_id, "status": "error",
                 "message": "include: must be a glob string or list of glob strings"}]
    if include and command:
        return [{"invariant": spec_id, "status": "error",
                 "message": "include: applies to declarative target+pattern checks only — "
                            "fold the filter into the command itself"}]
    exclude = check.get("exclude")
    if isinstance(exclude, str):
        exclude = [exclude]
    if exclude is not None and (not isinstance(exclude, list) or not all(isinstance(s, str) for s in exclude)):
        return [{"invariant": spec_id, "status": "error",
                 "message": "exclude: must be a path-substring string or list of strings"}]
    if exclude and command:
        return [{"invariant": spec_id, "status": "error",
                 "message": "exclude: applies to declarative target+pattern checks only — "
                            "fold the filter into the command itself"}]

    if command:
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
            err = (result.stderr or "").lower()
            if result.returncode > 1 or "not recognized" in err or "command not found" in err:
                return [{"invariant": spec_id, "status": "error",
                         "message": f"check command failed (rc {result.returncode}): {(result.stderr or '')[:200]}"}]
            matches = result.stdout.strip()
        except Exception as e:
            return [{"invariant": spec_id, "status": "error", "message": str(e)}]
    else:
        targets = target if isinstance(target, list) else [target]
        target_paths = []
        for t in targets:
            tp = project_root / t
            if not tp.exists():
                hint = " (multiple roots? use a YAML list for target:)" \
                    if isinstance(target, str) and " " in target else ""
                return [{"invariant": spec_id, "status": "error",
                         "message": f"Target path not found: {tp}{hint}"}]
            target_paths.append(tp)

        try:
            all_matches = []
            files_scanned = 0
            for tp in target_paths:
                m, scanned = _python_grep(tp, pattern, project_root,
                                          strip_comments=not check.get("include_comments", False),
                                          include=include)
                files_scanned += scanned
                if m:
                    all_matches.append(m)
            matches = "\n".join(all_matches)
            if exclude:
                kept = [line for line in matches.splitlines()
                        if line.strip() and not any(
                            sub in line.split(":", 1)[0].replace("\\", "/") for sub in exclude)]
                matches = "\n".join(kept)
        except re.error as e:
            return [{"invariant": spec_id, "status": "error",
                     "message": f"invalid pattern: {e}"}]

        if expect in ("absent", "only-in") and files_scanned == 0:
            return [{"invariant": spec_id, "status": "skipped",
                     "message": f"vacuous {expect}-check: 0 files scanned under "
                                f"'{target}' (empty target or include filter matched "
                                f"nothing) — scanned nothing, proved nothing"}]

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
                "_all_matches": [l.strip() for l in lines],
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
                "_all_matches": [v.strip() for v in violations],
            }]
        else:
            return [{"invariant": spec_id, "status": "pass", "assurance": "conformance"}]

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
                "_all_matches": output.split("\n"),
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
    """Run a semgrep-based check for structural/AST patterns."""
    import tempfile

    target = check.get("target", ".")
    rule_inline = check.get("rule")
    rules_file = check.get("rules_file")
    expect = check.get("expect", "absent")
    include = check.get("include")
    if isinstance(include, str):
        include = [include]

    if expect not in ("absent", "present"):
        return [{"invariant": spec_id, "status": "error",
                 "message": f"semgrep: unknown expect value '{expect}' — must be absent|present"}]

    if check.get("exclude") is not None:
        return [{"invariant": spec_id, "status": "error",
                 "message": "exclude: not implemented for semgrep checks — use include: "
                            "globs or narrow the target (grep checks support exclude)"}]

    target_path = project_root / target
    if not target_path.exists():
        return [{"invariant": spec_id, "status": "error",
                 "message": f"Target path not found: {target_path}"}]

    rule_path = None
    tmp_file = None

    if rules_file:
        rule_path = Path(rules_file)
        if not rule_path.is_absolute():
            rule_path = project_root / rule_path
        if not rule_path.exists():
            return [{"invariant": spec_id, "status": "error",
                     "message": f"Rules file not found: {rule_path}"}]
    elif rule_inline:
        if isinstance(rule_inline, dict):
            rule_content = yaml.dump(
                {"rules": [rule_inline]}, default_flow_style=False)
        elif isinstance(rule_inline, str):
            rule_content = rule_inline
        else:
            return [{"invariant": spec_id, "status": "error",
                     "message": "semgrep check.rule must be a dict (single rule) or string (raw YAML)"}]
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", prefix="semgrep-rule-", delete=False)
        tmp_file.write(rule_content)
        tmp_file.close()
        rule_path = Path(tmp_file.name)
    else:
        return [{"invariant": spec_id, "status": "error",
                 "message": "semgrep check requires 'rule' (inline) or 'rules_file'"}]

    cmd = ["semgrep", "--json", "--no-git-ignore", "--config", str(rule_path)]
    if include:
        for glob in include:
            cmd.extend(["--include", glob])
    cmd.append(str(target_path))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
        output = json.loads(result.stdout) if result.stdout.strip() else {}
    except FileNotFoundError:
        return [{"invariant": spec_id, "status": "skipped",
                 "message": "semgrep not installed — install with: pipx install semgrep"}]
    except json.JSONDecodeError:
        return [{"invariant": spec_id, "status": "error",
                 "message": f"semgrep produced invalid JSON. stderr: {(result.stderr or '')[:200]}"}]
    finally:
        if tmp_file:
            try:
                os.unlink(tmp_file.name)
            except OSError:
                pass

    errors = output.get("errors", [])
    if errors and not output.get("results"):
        err_msgs = [e.get("message", str(e))[:100] for e in errors[:3]]
        return [{"invariant": spec_id, "status": "error",
                 "message": f"semgrep errors: {'; '.join(err_msgs)}"}]

    findings = output.get("results", [])

    if expect == "absent":
        if findings:
            evidence = []
            for f in findings[:_EVIDENCE_CAP]:
                path = f.get("path", "?")
                line = f.get("start", {}).get("line", "?")
                msg = f.get("extra", {}).get("message", f.get("check_id", ""))
                evidence.append(f"{path}:{line}:{msg}")
            return [{
                "invariant": spec_id,
                "status": "fail",
                "confidence": confidence,
                "assurance": "conformance",
                "message": f"semgrep found {len(findings)} match(es) — expected none",
                "violations": evidence[:5],
                "_all_matches": evidence,
                "from_pattern": _first_pattern(check),
            }]
        return [{"invariant": spec_id, "status": "pass", "assurance": "conformance"}]

    elif expect == "present":
        if findings:
            return [{"invariant": spec_id, "status": "pass", "assurance": "conformance"}]
        return [{
            "invariant": spec_id, "status": "fail", "confidence": confidence,
            "assurance": "conformance",
            "message": "semgrep found no matches — expected at least one",
            "from_pattern": _first_pattern(check),
        }]

    return [{"invariant": spec_id, "status": "pass", "assurance": "conformance"}]


def _first_pattern(check):
    """Extract from_pattern context if available."""
    return check.get("from_pattern", None)
