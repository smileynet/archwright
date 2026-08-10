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
import yaml
import subprocess
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from archwright_common import state_events

SCRIPT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Violation fingerprinting (R32, aw/v1) — CK-07/CK-08 baseline plumbing.
# Identity = spec_id + invariant + normalized path + normalized evidence
# content. Line numbers NEVER enter the hash (SARIF 2.1.0 Appendix B: inserting
# lines above a result must not change its identity). Occurrence index among
# identical tuples is appended AFTER hashing (semgrep convention) so sibling
# duplicates stay visibly related. Algorithm changes bump the version tag —
# entries with an unknown algo are unmatchable, never guessed at.
# ---------------------------------------------------------------------------

FINGERPRINT_ALGO = "aw/v1"
BASELINE_FILENAME = ".archwright-baseline.json"
_EVIDENCE_RX = re.compile(r"^(.*?):(\d+):(.*)$")
_EVIDENCE_CAP = 100  # evidence[] and fingerprints[] stay aligned; both capped


def _fingerprint_base(spec_id, invariant, path, content):
    """aw/v1 fingerprint base: sha256 over NUL-joined identity inputs,
    truncated to 64 bits (16 hex chars — GitHub's primaryLocationLineHash
    width; collision space is per-project)."""
    norm_content = " ".join((content or "").split())
    basis = "\x00".join([spec_id or "", invariant or "", path or "", norm_content])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def _split_evidence(item):
    """Decompose a 'path:line:content' evidence string into (path, content),
    dropping the volatile line number. Items in another shape (script output,
    Alloy counterexample lines) hash whole as content with an empty path."""
    m = _EVIDENCE_RX.match(item)
    if m:
        return m.group(1), m.group(3)
    return "", item


def _find_up(start_dirs, filename):
    """Walk up from each start dir looking for filename; stop at the repo
    boundary (a file above the repo is never ours). Returns Path or None."""
    seen = set()
    for d in start_dirs:
        d = Path(d).resolve()
        if not d.is_dir():
            d = d.parent
        while d not in seen:
            seen.add(d)
            cand = d / filename
            if cand.is_file():
                return cand
            if (d / ".git").exists() or d.parent == d:
                break
            d = d.parent
    return None


def find_baseline(start_dirs, explicit=None):
    """Locate .archwright-baseline.json: explicit flag wins; otherwise walk up
    from each start dir. Returns a Path or None. No baseline = no suppression
    (never silently create one — baseline entries are a human decision)."""
    if explicit:
        return Path(explicit)
    return _find_up(start_dirs, BASELINE_FILENAME)


def load_baseline(path):
    """Parse the baseline file. Returns (data, matchable-fingerprint-set).
    Entries with an unknown algo are retained in data but excluded from
    matching (stale, never guessed). Raises ValueError on malformed JSON."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"cannot read baseline {path}: {e}")
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError(f"baseline {path}: 'entries' must be a list")
    fps = {e["fingerprint"] for e in entries
           if isinstance(e, dict) and "fingerprint" in e
           and e.get("algo", FINGERPRINT_ALGO) == FINGERPRINT_ALGO}
    return data, fps


# ---------------------------------------------------------------------------
# Evidence ledger (ADR 0009) — tool-owned sibling of the baseline.
# Machine evidence events (demotion/promotion candidates) are auto-appended
# here so confidence stops being write-once; human RATIFICATION never happens
# in this file (it happens in the artifact: confidence field + Evidence line;
# ★★ transitions always block for HITL — ADR 0007).
#
# Activation by existence: writes happen only when the ledger file already
# exists (discovered up-tree like the baseline) or --evidence names one
# explicitly (create-if-missing — the flag states intent). No file, no flag =
# events stay session-ephemeral (the ADR's accepted gap, opted out of per
# project by touching design/.archwright-evidence.json). This also keeps
# checked-in fixture trees clean.
# ---------------------------------------------------------------------------

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


def _code_state(root):
    """Git identity of the checked tree (ticket 018, EDA signoff precedent):
    {'commit': <hash>, 'dirty': <bool>} — evidence recorded at a commit can be
    told apart from evidence about some other code state. A dirty tree means
    the commit does NOT fully identify the checked code; consumers treat such
    evidence as unverifiable for signoff-grade claims.

    Git absent / not a repo = {'commit': None, 'dirty': None, 'reason': ...} —
    a coverage statement on the field, never a crash (unlike --changed-only,
    nothing here REQUIRES git; identity is best-effort)."""
    import shutil
    if shutil.which("git") is None:
        return {"commit": None, "dirty": None, "reason": "git not on PATH"}
    r = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return {"commit": None, "dirty": None,
                "reason": "not a git repository (or no commits yet)"}
    s = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                       capture_output=True, text=True)
    return {"commit": r.stdout.strip(),
            "dirty": bool(s.stdout.strip()) if s.returncode == 0 else None}


def extract_frontmatter(path):
    """Extract YAML frontmatter from a markdown file.

    Fence-aware (ticket 039): fences are LINES matching ^---$, never the
    substring — a block scalar legitimately containing `---` (e.g. a grep
    for fence lines) must not truncate the frontmatter. Block-scalar content
    is indented, so it can never match a fence-line pattern.
    """
    content = path.read_text(encoding="utf-8")
    m = re.match(r"---[ \t]*\r?\n", content)
    if not m:
        return None
    body = content[m.end():]
    m2 = re.search(r"^---[ \t]*$", body, re.MULTILINE)
    if not m2:
        return None
    return yaml.safe_load(body[: m2.start()])


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


def _project_root_for(spec_path):
    """Determine the project root for a spec: ARCHWRIGHT_PROJECT_ROOT env
    (set by --target) wins, else walk up from the spec dir looking for a
    project marker."""
    env_root = os.environ.get("ARCHWRIGHT_PROJECT_ROOT")
    if env_root:
        return Path(env_root)
    spec_dir = Path(spec_path).resolve().parent
    project_root = spec_dir
    for _ in range(5):
        if (project_root / "design").exists() or (project_root / "project.godot").exists():
            break
        project_root = project_root.parent
    return project_root


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
            # Check only the relative path parts so system directories
            # (e.g. Windows %TEMP% containing 'Temp') don't false-skip.
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
                # Positional check, NOT truncation: a match counts only if it starts
                # before the comment token. Truncating at the token broke any pattern
                # containing the token itself — e.g. "http://" contains "//", so TLS
                # checks in //-comment languages could never match (false PASS).
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

    # Unknown expect values are a TOOL ERROR, never a silent pass (CK-05/B4, A1/F3).
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
    # exclude: path-substring filter (ticket 040 — was documented but unimplemented;
    # a silently-ignored field is worse than a rejected one).
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
        # target: single path or list of paths (ticket 006) — matches are unioned
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

        # Ticket 012: an absence claim over zero scanned files is vacuous —
        # a check that scanned nothing proved nothing. SKIP-with-reason, never
        # PASS. Applies to both absence polarities (absent, only-in); a present
        # check over zero files already FAILs loudly. Command-mode checks are
        # exempt (the command author owns their semantics).
        if expect in ("absent", "only-in") and files_scanned == 0:
            return [{"invariant": spec_id, "status": "skipped",
                     "message": f"vacuous {expect}-check: 0 files scanned under "
                                f"'{target}' (empty target or include filter matched "
                                f"nothing) — scanned nothing, proved nothing"}]

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
    """Run a semgrep-based check for structural/AST patterns.

    Spec fields:
      check.method: semgrep
      check.target: path (relative to project root) to scan
      check.rule: inline semgrep rule (dict — written to a temp file)
      check.rules_file: path to a .yaml rule file (alternative to inline)
      check.expect: absent (default) | present
      check.include: glob or list of globs to filter scanned files (optional)
    """
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

    # Ticket 040: exclude is implemented for grep only. A silently-ignored
    # field is worse than a rejected one — error loudly until implemented here.
    if check.get("exclude") is not None:
        return [{"invariant": spec_id, "status": "error",
                 "message": "exclude: not implemented for semgrep checks — use include: "
                            "globs or narrow the target (grep checks support exclude)"}]

    target_path = project_root / target
    if not target_path.exists():
        return [{"invariant": spec_id, "status": "error",
                 "message": f"Target path not found: {target_path}"}]

    # Determine rule source
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
        # Write inline rule to temp file
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

    # Build command
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

    # Check for semgrep-level errors (not findings)
    errors = output.get("errors", [])
    if errors and not output.get("results"):
        err_msgs = [e.get("message", str(e))[:100] for e in errors[:3]]
        return [{"invariant": spec_id, "status": "error",
                 "message": f"semgrep errors: {'; '.join(err_msgs)}"}]

    findings = output.get("results", [])

    # Interpret based on expect
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


def main():
    if len(sys.argv) < 2:
        print("Usage: archwright-check <spec>... | --all <dir> | --static <dir> [--target <root>] "
              "[--changed-only [--base <ref>]] | --trace <spec> <trace> [--evidence <file>] | "
              "--probe <spec> | --trace-coverage <specs-dir> <traces-dir> | "
              "--coverage <specs-dir> [--target <root>] | "
              "--pbt <spec> --step <module.py> [--emit <dir>] [--examples N]\n"
              "Common flags: --json  --baseline <file>  --update-baseline  --evidence <file>")
        sys.exit(2)

    # Handle --trace mode early (different flow). --json (anywhere after
    # --trace) switches output to the CK-03 document shape (ticket 016);
    # --evidence <file> names an explicit evidence ledger (ADR 0009).
    if sys.argv[1] == "--trace":
        rest = sys.argv[2:]
        trace_json = "--json" in rest
        trace_evidence = None
        trace_args = []
        i = 0
        while i < len(rest):
            if rest[i] == "--json":
                pass
            elif rest[i] == "--evidence":
                i += 1
                if i < len(rest):
                    trace_evidence = rest[i]
            else:
                trace_args.append(rest[i])
            i += 1
        if len(trace_args) < 2:
            print(json.dumps({"status": "error", "message": "Usage: archwright-check --trace <spec.yaml> <trace.json> [--json] [--evidence <file>]"}))
            sys.exit(2)
        sys.exit(check_trace(trace_args[0], trace_args[1], json_output=trace_json,
                             evidence_arg=trace_evidence))

    # Handle --probe mode early (different flow)
    if sys.argv[1] == "--probe":
        if len(sys.argv) < 3:
            print("Usage: archwright-check --probe <behavior-spec.yaml>")
            sys.exit(2)
        sys.exit(probe_behavior(sys.argv[2]))

    # Handle --trace-coverage mode early (different flow)
    if sys.argv[1] == "--trace-coverage":
        if len(sys.argv) < 4:
            print("Usage: archwright-check --trace-coverage <specs-dir> <traces-dir> [--json]")
            sys.exit(2)
        tc_json = "--json" in sys.argv[4:]
        try:
            sys.exit(trace_coverage_report(sys.argv[2], sys.argv[3], json_output=tc_json))
        except Exception as e:  # exit-code contract: tool error = 2 (ticket 043)
            print(f"ERROR: trace-coverage failed: {e}", file=sys.stderr)
            sys.exit(2)

    # Handle --coverage mode early (different flow)
    if sys.argv[1] == "--coverage":
        if len(sys.argv) < 3:
            print("Usage: archwright-check --coverage <specs-dir> [--target <root>] [--json]")
            sys.exit(2)
        cov_target = None
        cov_json = "--json" in sys.argv[3:]
        rest = [a for a in sys.argv[3:] if a != "--json"]
        for idx, a in enumerate(rest):
            if a == "--target" and idx + 1 < len(rest):
                cov_target = rest[idx + 1]
        try:
            sys.exit(coverage_report(sys.argv[2], target_root=cov_target, json_output=cov_json))
        except Exception as e:  # exit-code contract: tool error = 2 (ticket 043)
            print(f"ERROR: coverage failed: {e}", file=sys.stderr)
            sys.exit(2)

    # Handle --pbt mode early (different flow)
    if sys.argv[1] == "--pbt":
        rest = sys.argv[2:]
        pbt_spec = None
        pbt_step = None
        pbt_emit = None
        pbt_json = "--json" in rest
        pbt_examples = 200
        args_remaining = [a for a in rest if a != "--json"]
        i = 0
        while i < len(args_remaining):
            if args_remaining[i] == "--step" and i + 1 < len(args_remaining):
                pbt_step = args_remaining[i + 1]
                i += 2
            elif args_remaining[i] == "--emit" and i + 1 < len(args_remaining):
                pbt_emit = args_remaining[i + 1]
                i += 2
            elif args_remaining[i] == "--examples" and i + 1 < len(args_remaining):
                pbt_examples = int(args_remaining[i + 1])
                i += 2
            elif pbt_spec is None:
                pbt_spec = args_remaining[i]
                i += 1
            else:
                i += 1
        if not pbt_spec or not pbt_step:
            print("Usage: archwright-check --pbt <spec.yaml> --step <step_module.py> "
                  "[--emit <dir>] [--examples N] [--json]")
            sys.exit(2)
        # Import and run the PBT adapter
        pbt_adapter = Path(__file__).parent / "stacks" / "python" / "pbt_harness" / "adapter.py"
        if not pbt_adapter.exists():
            print(f"ERROR: PBT adapter not found: {pbt_adapter}", file=sys.stderr)
            sys.exit(2)
        import importlib.util
        pbt_mod_spec = importlib.util.spec_from_file_location("pbt_adapter", str(pbt_adapter))
        pbt_mod = importlib.util.module_from_spec(pbt_mod_spec)
        pbt_mod_spec.loader.exec_module(pbt_mod)
        result = pbt_mod.load_and_run(pbt_spec, pbt_step, max_examples=pbt_examples)
        if pbt_json:
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

    files = []
    target_root = None
    static_only = False
    json_output = False
    mode = "files"
    baseline_arg = None
    evidence_arg = None
    update_baseline = False
    changed_only = False
    base_ref = "HEAD"

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
        elif args[i] == "--baseline":
            i += 1
            if i < len(args):
                baseline_arg = args[i]
        elif args[i] == "--evidence":
            i += 1
            if i < len(args):
                evidence_arg = args[i]
        elif args[i] == "--update-baseline":
            update_baseline = True
        elif args[i] == "--changed-only":
            changed_only = True
        elif args[i] == "--base":
            i += 1
            if i < len(args):
                base_ref = args[i]
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
