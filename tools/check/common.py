"""Shared constants and utility functions used across check modules."""

import os
import re
import subprocess
import yaml
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent.parent  # tools/ directory

FINGERPRINT_ALGO = "aw/v1"
_EVIDENCE_RX = re.compile(r"^(.*?):(\d+):(.*)$")
_EVIDENCE_CAP = 100  # evidence[] and fingerprints[] stay aligned; both capped

_SEVERITY = {"★★": "error", "★": "warning", "—": "info"}


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


def _fingerprint_base(spec_id, invariant, path, content):
    """aw/v1 fingerprint base: sha256 over NUL-joined identity inputs,
    truncated to 64 bits (16 hex chars — GitHub's primaryLocationLineHash
    width; collision space is per-project)."""
    import hashlib
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
