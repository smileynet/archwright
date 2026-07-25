#!/usr/bin/env python3
"""archwright-validate: Validate pattern, spec, and discovery files against schemas.

Usage:
  archwright-validate [--json] <file>...          Validate individual files
  archwright-validate [--json] --links <dir>      Validate all links resolve

Discovery artifacts (kind: discovery, ADR 0011 / ticket 026): per-file mode
validates the frontmatter schema, ledger entry structure, and the nothing-
invented conservation direction; --links adds citation resolution and the
nothing-lost direction across the artifact set.

Output: per-file PASS/FAIL plus non-fatal `WARN:` lines (advisory quality
signals, e.g. a spec missing `protects_experience`) — warnings never affect
the exit code. `--json` emits the CK-03 document shape (see
check-output-schema.yaml) with warnings[] alongside violations[].

Exit codes: 0 = all valid (warnings allowed), 1 = validation failures,
2 = tool/input error.
"""

import sys
import os
import re
import yaml
import json
from pathlib import Path

SCHEMA_DIR = Path(__file__).parent
PATTERN_SCHEMA = SCHEMA_DIR / "pattern-schema.yaml"
SPEC_SCHEMA = SCHEMA_DIR / "spec-schema.yaml"

VALID_KINDS = {"pattern", "behavior", "contract", "constraint", "dependency", "boundary", "protocol", "force", "discovery", "model"}
VALID_CONFIDENCES = {"★★", "★", "—"}
VALID_SCALES = {"premise", "loops-systems", "verbs-interactions", "feel-finish"}
# gated = resolution ratified, activation gated on a named event (requires gated_on:).
# fog = unknown forces / unresolved tension — never repurpose for a ratified deferral (ticket 011).
VALID_PATTERN_STATUSES = {"active", "fog", "gated", "deprecated"}
VALID_POLARITIES = {"desire", "constraint"}
VALID_HARDNESS = {"hard", "soft"}
VALID_EVIDENCE_LEVELS = {"L1", "L2", "L3", "L4", "L5"}
LINK_REF_PATTERN = re.compile(r"^(behavior|contract|constraint|dependency|boundary|protocol|pattern|force):.+$")

# Discovery track (ADR 0011, ticket 026) — seam artifact schema + conservation.
VALID_DISCOVERY_STATUSES = {"proposed", "approved", "superseded"}
VALID_ORIGINS = {"user", "suggested", "inferred"}
CORE_CATEGORIES = {"scope", "experience", "structure", "technical", "meta"}
# Ledger entry heading: "### D001 — Title" (file-scoped numbering)
LEDGER_ENTRY_PATTERN = re.compile(r"^###\s+D(\d{3})\s+[—-]", re.MULTILINE)
# Citation anchors: bare D001 (file-scoped) or qualified artifact-id#D001
QUALIFIED_CITATION_PATTERN = re.compile(r"([a-z][a-z0-9-]+)#D(\d{3})")
BARE_CITATION_PATTERN = re.compile(r"(?<![#\w-])D(\d{3})\b")
SUPERSEDES_PATTERN = re.compile(r"SUPERSEDES\s+(?:([a-z][a-z0-9-]+)#)?D(\d{3})")
# Seam-output sections whose ELEMENTS (list items / table rows) must cite anchors
# (grill Q6 — nothing invented; granularity resolved 2026-07-19: element-level,
# matching the templates' per-bullet/per-row citation obligation).
OUTPUT_SECTIONS = {"hands to", "graduates to patterns"}
# Sections exempt from the citation obligation in ledger-less consumer artifacts
# (model seeds): the ledger itself, the deferral list, and gap/TODO lists.
CONSUMER_EXEMPT_SECTIONS = {"decisions", "unconsumed decisions", "not resolved here", "todo", "todos"}


def extract_frontmatter(path):
    """Extract YAML frontmatter from a markdown file.

    Fence-aware (ticket 039): fences are LINES matching ^---$, never the
    substring — a block scalar legitimately containing `---` must not
    truncate the frontmatter.
    """
    content = path.read_text(encoding="utf-8")
    m = re.match(r"---[ \t]*\r?\n", content)
    if not m:
        return None, "File does not start with YAML frontmatter (---)"
    body = content[m.end():]
    m2 = re.search(r"^---[ \t]*$", body, re.MULTILINE)
    if not m2:
        return None, "Malformed frontmatter: no closing ---"
    try:
        data = yaml.safe_load(body[: m2.start()])
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error in frontmatter: {e}"


def load_file(path):
    """Load a pattern or spec file, return (data, kind, errors)."""
    path = Path(path)
    errors = []

    if path.suffix == ".yaml" or path.suffix == ".yml":
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return None, None, ["File does not contain a YAML mapping"]
            kind = data.get("kind")
            # Model detection convention (ticket 048): model YAML carries no
            # frontmatter/kind — a mapping with a top-level `actors` key IS a
            # model (the same shape test collect_model_index and the report
            # generator use). An explicit `kind: model` is also accepted.
            if kind is None and "actors" in data:
                kind = "model"
            return data, kind, errors
        except yaml.YAMLError as e:
            return None, None, [f"YAML parse error: {e}"]
    elif path.suffix == ".md":
        data, err = extract_frontmatter(path)
        if err:
            return None, None, [err]
        if not isinstance(data, dict):
            return None, None, ["Frontmatter is not a YAML mapping"]
        return data, data.get("kind"), errors
    else:
        return None, None, [f"Unknown file extension: {path.suffix}"]


def validate_force(data, path):
    """Validate a force file's frontmatter fields."""
    errors = []
    required = ["kind", "id", "polarity"]
    for field in required:
        if field not in data:
            errors.append(f"required field '{field}' missing")

    if data.get("kind") != "force":
        errors.append(f"kind must be 'force', got '{data.get('kind')}'")
    if data.get("polarity") and data["polarity"] not in VALID_POLARITIES:
        errors.append(f"invalid polarity '{data['polarity']}' — must be one of: {VALID_POLARITIES}")
    if data.get("hardness") and data["hardness"] not in VALID_HARDNESS:
        errors.append(f"invalid hardness '{data['hardness']}' — must be one of: {VALID_HARDNESS}")
    if data.get("evidence_level") and data["evidence_level"] not in VALID_EVIDENCE_LEVELS:
        errors.append(f"invalid evidence_level '{data['evidence_level']}' — must be one of: {VALID_EVIDENCE_LEVELS}")
    if data.get("id") and not re.match(r"^[a-z][a-z0-9-]+$", data["id"]):
        errors.append(f"id '{data['id']}' must be lowercase slug (a-z, 0-9, hyphens)")
    if data.get("polarity") == "constraint" and "hardness" not in data:
        errors.append("constraint forces require 'hardness' (hard|soft)")
    if data.get("polarity") == "desire" and data.get("serves"):
        errors.append("desires do not 'serve' other forces — they ARE the product-level forces")

    for ref in data.get("serves", []):
        if ":" in ref:
            errors.append(f"serves entry '{ref}' must be a bare force id (no 'kind:' prefix)")

    return errors


def validate_pattern(data, path):
    """Validate a pattern's frontmatter fields."""
    errors = []
    required = ["kind", "id", "name", "scale", "confidence"]
    for field in required:
        if field not in data:
            errors.append(f"required field '{field}' missing")

    if data.get("kind") != "pattern":
        errors.append(f"kind must be 'pattern', got '{data.get('kind')}'")
    if data.get("scale") and data["scale"] not in VALID_SCALES:
        errors.append(f"invalid scale '{data['scale']}' — must be one of: {VALID_SCALES}")
    if data.get("confidence") and data["confidence"] not in VALID_CONFIDENCES:
        errors.append(f"invalid confidence '{data['confidence']}' — must be one of: {VALID_CONFIDENCES}")
    if data.get("id") and not re.match(r"^[a-z][a-z0-9-]+$", data["id"]):
        errors.append(f"id '{data['id']}' must be lowercase slug (a-z, 0-9, hyphens)")

    # Status vocabulary (ticket 011): gated = resolution RATIFIED, activation
    # gated on a named future event. Distinct from fog (unknown forces /
    # unresolved tension — a HITL-blocking condition). Never repurpose fog
    # for a ratified deferral.
    status = data.get("status")
    if status and status not in VALID_PATTERN_STATUSES:
        errors.append(f"invalid status '{status}' — must be one of: {sorted(VALID_PATTERN_STATUSES)}")
    if status == "gated" and not (isinstance(data.get("gated_on"), str) and data["gated_on"].strip()):
        errors.append("status 'gated' requires a gated_on: field naming the unblocking event "
                      "(e.g. a spike verdict, an engine migration)")
    if data.get("gated_on") and status != "gated":
        errors.append(f"gated_on: is only meaningful with status 'gated' (status is '{status}')")

    for ref in data.get("resolves_into", []):
        if not LINK_REF_PATTERN.match(ref):
            errors.append(f"resolves_into ref '{ref}' must be 'kind:id' format")

    return errors


def validate_behavior(data, path):
    """Validate a behavior spec (YAML)."""
    errors = []
    required = ["kind", "id", "from_patterns", "initial", "states"]
    for field in required:
        if field not in data:
            errors.append(f"required field '{field}' missing")

    if data.get("kind") != "behavior":
        errors.append(f"kind must be 'behavior', got '{data.get('kind')}'")
    if data.get("confidence") and data["confidence"] not in VALID_CONFIDENCES:
        errors.append(f"invalid confidence '{data['confidence']}'")

    for ref in data.get("from_patterns", []):
        if not ref.startswith("pattern:"):
            errors.append(f"from_patterns ref '{ref}' must start with 'pattern:'")

    for link in data.get("links", []):
        if "target" in link and not LINK_REF_PATTERN.match(link["target"]):
            errors.append(f"link target '{link['target']}' must be 'kind:id' format")

    return errors


def validate_constraint_or_dependency(data, path):
    """Validate a constraint or dependency spec (frontmatter)."""
    errors = []
    required = ["kind", "id", "from_patterns", "confidence"]
    for field in required:
        if field not in data:
            errors.append(f"required field '{field}' missing")

    kind = data.get("kind")
    if kind not in ("constraint", "dependency"):
        errors.append(f"kind must be 'constraint' or 'dependency', got '{kind}'")
    if data.get("confidence") and data["confidence"] not in VALID_CONFIDENCES:
        errors.append(f"invalid confidence '{data['confidence']}'")

    for ref in data.get("from_patterns", []):
        if not ref.startswith("pattern:"):
            errors.append(f"from_patterns ref '{ref}' must start with 'pattern:'")

    for link in data.get("links", []):
        if "target" in link and not LINK_REF_PATTERN.match(link["target"]):
            errors.append(f"link target '{link['target']}' must be 'kind:id' format")

    if "check" not in data:
        errors.append("constraint/dependency spec should have a 'check' field")

    return errors


def validate_contract(data, path):
    """Validate a contract spec (mirrors tools/contract-schema.yaml)."""
    errors = []
    required = ["kind", "id", "from_patterns"]
    for field in required:
        if field not in data:
            errors.append(f"required field '{field}' missing")

    if data.get("id") and not re.match(r"^[a-z][a-z0-9-]+$", data["id"]):
        errors.append(f"id '{data['id']}' must be lowercase slug (a-z, 0-9, hyphens)")
    if data.get("confidence") and data["confidence"] not in VALID_CONFIDENCES:
        errors.append(f"invalid confidence '{data['confidence']}'")

    for ref in data.get("from_patterns", []):
        if not ref.startswith("pattern:"):
            errors.append(f"from_patterns ref '{ref}' must start with 'pattern:'")

    from_model = data.get("from_model")
    if from_model and not (isinstance(from_model, str) and from_model.startswith("model:") and len(from_model) > 6):
        errors.append(f"from_model '{from_model}' must be 'model:<actor-or-candidate-id>'")

    events = data.get("events") or {}
    if not isinstance(events, dict):
        errors.append("'events' must be a mapping of event name -> definition")
    else:
        for name, ev in events.items():
            if not isinstance(ev, dict):
                errors.append(f"event '{name}' must be a mapping")
                continue
            for key in ("producer", "consumers", "stability", "payload"):
                if key not in ev:
                    errors.append(f"event '{name}' missing required '{key}'")
            if "stability" in ev and ev["stability"] not in ("public", "internal"):
                errors.append(f"event '{name}' stability must be 'public' or 'internal'")
            for fname, fdef in (ev.get("payload") or {}).items():
                if not isinstance(fdef, dict) or "type" not in fdef:
                    errors.append(f"event '{name}' payload field '{fname}' missing 'type'")

    for fname, fdef in (data.get("fields") or {}).items():
        if not isinstance(fdef, dict) or "type" not in fdef:
            errors.append(f"field '{fname}' missing 'type'")

    for link in data.get("links", []):
        if "target" in link and not LINK_REF_PATTERN.match(link["target"]):
            errors.append(f"link target '{link['target']}' must be 'kind:id' format")

    return errors


_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_FENCE_RE = re.compile(r"^```.*?^```[^\n]*$", re.DOTALL | re.MULTILINE)
_CATEGORY_CACHE = None


def _discovery_categories():
    """Valid ledger categories: core 5 ∪ union of all domain overlay extensions
    (script-relative tools/domains/*/discovery.yaml — grill Q2). Union, not
    per-domain strict: the validator has no domain-detection context; a category
    outside every known vocabulary is the mechanical floor it can enforce."""
    global _CATEGORY_CACHE
    if _CATEGORY_CACHE is None:
        cats = set(CORE_CATEGORIES)
        for f in sorted((SCHEMA_DIR / "domains").glob("*/discovery.yaml")):
            try:
                d = yaml.safe_load(f.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                continue
            if isinstance(d, dict):
                cats.update(d.get("category_extensions") or [])
        _CATEGORY_CACHE = cats
    return _CATEGORY_CACHE


def _discovery_body(path):
    """Markdown body after frontmatter, with HTML comments and fenced code
    stripped (template guidance comments and ASCII wireframes must never
    register as ledger entries, citations, or citable elements)."""
    content = path.read_text(encoding="utf-8")
    # Fence-aware (ticket 039): body starts after the closing fence LINE,
    # never after the next `---` substring.
    m = re.match(r"---[ \t]*\r?\n", content)
    if m:
        m2 = re.search(r"^---[ \t]*$", content[m.end():], re.MULTILINE)
        if m2:
            content = content[m.end() + m2.end():]
    return _FENCE_RE.sub("", _COMMENT_RE.sub("", content))


def _split_sections(body):
    """Split body into (heading_lowercase, text) pairs by ## headings.
    Text before the first ## gets heading ''."""
    sections = []
    heading, lines = "", []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            sections.append((heading, "\n".join(lines)))
            heading, lines = m.group(1).strip().lower(), []
        else:
            lines.append(line)
    sections.append((heading, "\n".join(lines)))
    return sections


def _parse_ledger(text):
    """Parse D{NNN} entries from a Decisions section: [{'num', 'text'}]."""
    parts = re.split(r"^###\s+D(\d{3})\b[^\n]*$", text, flags=re.MULTILINE)
    return [{"num": parts[i], "text": parts[i + 1]} for i in range(1, len(parts) - 1, 2)]


def _elements(text):
    """Citable elements in a section: list items and table data rows.
    The first two lines of a pipe-table run (header + separator) are skipped."""
    out = []
    pipe_run = 0
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            pipe_run += 1
            if pipe_run >= 3 and not re.match(r"^\|[\s:|-]+\|?$", s):
                out.append(s)
            continue
        pipe_run = 0
        if re.match(r"^[-*]\s+\S", s):
            out.append(s)
    return out


def _has_citation(text):
    return bool(BARE_CITATION_PATTERN.search(text) or QUALIFIED_CITATION_PATTERN.search(text))


def validate_discovery(data, path):
    """Validate a discovery artifact (ticket 026): frontmatter schema, ledger
    entry structure, and the within-file conservation direction (nothing
    invented — every seam-output element cites a ledger anchor, grill Q6).
    The cross-file direction (nothing lost) lives in --links.

    Conservation gates on status: approved = errors (graduation is the gate),
    proposed = warnings (session in progress), superseded = skipped entirely.
    Returns (errors, warnings)."""
    errors = []
    warnings = []
    for field in ("kind", "id", "status"):
        if field not in data:
            errors.append(f"required field '{field}' missing")

    if data.get("kind") != "discovery":
        errors.append(f"kind must be 'discovery', got '{data.get('kind')}'")
    if data.get("id") and not re.match(r"^[a-z][a-z0-9-]+$", data["id"]):
        errors.append(f"id '{data['id']}' must be lowercase slug (a-z, 0-9, hyphens)")
    status = data.get("status")
    if status and status not in VALID_DISCOVERY_STATUSES:
        errors.append(f"invalid status '{status}' — must be one of: {sorted(VALID_DISCOVERY_STATUSES)}")
    for ref in data.get("serves") or []:
        if isinstance(ref, str) and ":" in ref:
            errors.append(f"serves entry '{ref}' must be a bare force id (no 'kind:' prefix)")

    if status == "superseded":
        return errors, warnings  # excluded from every projection (ledger rule 1)

    sections = _split_sections(_discovery_body(path))
    valid_categories = _discovery_categories()

    # Ledger entry structure (format: tools/templates/discovery-ledger.md)
    entry_ids = set()
    for heading, text in sections:
        if heading != "decisions":
            continue
        for entry in _parse_ledger(text):
            eid = f"D{entry['num']}"
            if eid in entry_ids:
                errors.append(f"duplicate ledger entry id {eid} — anchors must be unique (append-only, never renumbered)")
            entry_ids.add(eid)
            for field in ("Category", "Origin", "Decision", "Rationale", "Alternatives"):
                if not re.search(rf"\*\*{field}:\*\*", entry["text"]):
                    errors.append(f"ledger entry {eid} missing required field '{field}'")
            m = re.search(r"\*\*Origin:\*\*\s*(\S+)", entry["text"])
            if m and m.group(1) not in VALID_ORIGINS:
                errors.append(f"ledger entry {eid} invalid origin '{m.group(1)}' — must be one of: {sorted(VALID_ORIGINS)}")
            m = re.search(r"\*\*Category:\*\*\s*(\S+)", entry["text"])
            if m and m.group(1) not in valid_categories:
                errors.append(f"ledger entry {eid} invalid category '{m.group(1)}' — must be core "
                              f"({sorted(CORE_CATEGORIES)}) or a domain overlay extension")

    # Nothing invented (element-level). Ledger-bearing artifacts: only the
    # designated seam-output sections carry the obligation. Ledger-less
    # consumers (model seeds): every non-exempt element must cite.
    orphans = []
    for heading, text in sections:
        if entry_ids:
            if heading not in OUTPUT_SECTIONS:
                continue
        elif heading in CONSUMER_EXEMPT_SECTIONS or heading == "":
            continue
        for element in _elements(text):
            if not _has_citation(element):
                orphans.append(f"conservation (nothing invented): element in '{heading or 'body'}' "
                               f"cites no ledger anchor — \"{element[:70]}\"")
    if status == "approved":
        errors.extend(orphans)
    else:
        warnings.extend(orphans)

    return errors, warnings


def validate_model(data, path):
    """Validate a domain model YAML (ticket 048).

    Detection convention: a YAML mapping with a top-level `actors` key is a
    model (see load_file) — models carry no frontmatter; `kind: model` is
    accepted but optional, so existing field models validate unmodified.

    Hard schema (errors): non-empty actors with unique slug ids; dict states
    carry ids; actor from_patterns are 'pattern:' refs; contract candidates
    carry event + producer, event names unique within the file, folds resolve
    to a non-folded candidate in the same file; spec_projections carry
    'kind:id' spec refs; boundary entities carry ids.

    Advisory (WARN): missing experiences / composition sections — the
    archwright-model skill emits them, but the examples corpus and both field
    projects' models predate the requirement (delta documented, ticket 048).

    Returns (errors, warnings)."""
    errors, warnings = [], []

    actors = data.get("actors")
    if not isinstance(actors, list) or not actors:
        errors.append("'actors' must be a non-empty list")
        actors = []
    seen_actors = set()
    for i, a in enumerate(actors):
        if not isinstance(a, dict) or not a.get("id"):
            errors.append(f"actor [{i}] missing required 'id'")
            continue
        aid = a["id"]
        if not re.match(r"^[a-z][a-z0-9-]+$", aid):
            errors.append(f"actor id '{aid}' must be lowercase slug (a-z, 0-9, hyphens)")
        if aid in seen_actors:
            errors.append(f"duplicate actor id '{aid}'")
        seen_actors.add(aid)
        for st in a.get("states") or []:
            if isinstance(st, dict) and not st.get("id"):
                errors.append(f"actor '{aid}' has a state without an 'id'")
        for ref in a.get("from_patterns") or []:
            if not str(ref).startswith("pattern:"):
                errors.append(f"actor '{aid}' from_patterns ref '{ref}' must start with 'pattern:'")

    boundary_ids = set()
    for i, be in enumerate(data.get("boundary_entities") or []):
        if not isinstance(be, dict) or not be.get("id"):
            errors.append(f"boundary_entities [{i}] missing required 'id'")
        else:
            boundary_ids.add(be["id"])

    cands = data.get("contract_candidates")
    events = {}
    if cands is not None and not isinstance(cands, list):
        errors.append("'contract_candidates' must be a list")
        cands = []
    for i, c in enumerate(cands or []):
        if not isinstance(c, dict) or not c.get("event"):
            errors.append(f"contract_candidates [{i}] missing required 'event'")
            continue
        ev = c["event"]
        if ev in events:
            errors.append(f"duplicate contract candidate event '{ev}' — candidate events "
                          f"must be unique within a model (cross-model collisions: ticket 050)")
        events[ev] = c
        if "shared" in c and not isinstance(c["shared"], bool):
            errors.append(f"contract candidate '{ev}' 'shared' must be a boolean "
                          f"(cross-model sharing opt-in, ticket 050)")
        if not c.get("producer"):
            errors.append(f"contract candidate '{ev}' missing required 'producer'")
        elif c["producer"] not in seen_actors | boundary_ids:
            warnings.append(f"contract candidate '{ev}' producer '{c['producer']}' names no "
                            f"actor or boundary entity in this model")
    for ev, c in events.items():
        fold = c.get("folded_into")
        if not fold:
            continue
        if fold == ev:
            errors.append(f"contract candidate '{ev}' is folded into itself")
        elif fold not in events:
            errors.append(f"contract candidate '{ev}' folded_into '{fold}' which is not a "
                          f"candidate in this model")
        elif events[fold].get("folded_into"):
            errors.append(f"contract candidate '{ev}' folds into '{fold}', which is itself "
                          f"folded — folds must target the protocol cluster owner directly")

    for i, proj in enumerate(data.get("spec_projections") or []):
        if not isinstance(proj, dict) or not proj.get("spec"):
            errors.append(f"spec_projections [{i}] missing required 'spec'")
        elif not LINK_REF_PATTERN.match(proj["spec"]):
            errors.append(f"spec_projections [{i}] spec ref '{proj['spec']}' must be 'kind:id' format")

    for i, exp in enumerate(data.get("experiences") or []):
        if not isinstance(exp, dict) or not exp.get("id"):
            errors.append(f"experiences [{i}] missing required 'id'")

    if "experiences" not in data:
        warnings.append("no 'experiences' section — the archwright-model skill records the "
                        "user experiences the actors protect; add them so specs can cite "
                        "protects_experience")
    if "composition" not in data:
        warnings.append("no 'composition' section — record how the actors compose "
                        "(root/stages/rationale) per the archwright-model output format")

    return errors, warnings


def validate_file(path):
    """Validate a single file. Returns (status, errors, warnings)."""
    path = Path(path)
    if not path.exists():
        return "error", [f"File not found: {path}"], []

    data, kind, load_errors = load_file(path)
    if load_errors:
        return "error", load_errors, []

    warnings = []
    if kind == "pattern":
        errors = validate_pattern(data, path)
    elif kind == "force":
        errors = validate_force(data, path)
    elif kind == "behavior":
        errors = validate_behavior(data, path)
    elif kind in ("constraint", "dependency"):
        errors = validate_constraint_or_dependency(data, path)
    elif kind == "contract":
        errors = validate_contract(data, path)
    elif kind == "discovery":
        errors, warnings = validate_discovery(data, path)
    elif kind == "model":
        errors, warnings = validate_model(data, path)
    elif kind in ("boundary", "protocol"):
        errors = []  # minimal validation for now
    else:
        errors = [f"unknown kind '{kind}'"]

    if kind in ("behavior", "contract", "constraint", "dependency") and not data.get("protects_experience"):
        warnings.append(
            "no 'protects_experience' — link a modeled experience id (preferred) or a "
            "product-force id, so the spec traces to what users feel"
        )

    if kind == "behavior":
        for inv in data.get("invariants") or []:
            if isinstance(inv, dict) and not inv.get("description"):
                warnings.append(
                    f"invariant '{inv.get('id', '?')}' has no 'description' — the report "
                    "renders invariants as plain-language statements (design-system#D002); "
                    "add one sentence a cold reader can follow"
                )

    return ("pass" if not errors else "fail"), errors, warnings


def _collect_from_force_refs(node, out):
    """Recursively collect all 'from_force' values from nested spec structures."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "from_force" and isinstance(value, str):
                out.append(value)
            else:
                _collect_from_force_refs(value, out)
    elif isinstance(node, list):
        for item in node:
            _collect_from_force_refs(item, out)


def collect_model_index(directory):
    """Index actor ids + contract-candidate events from design/models/*.yaml.

    Returns (model_ids, candidates, boundary_nonproducers, models_exist, parse_errors).
    Enforcement follows the force-inventory pattern: no model files ->
    from_model refs are not checked.

    Boundary entities (ticket 013): a boundary entity named as a PRODUCER in
    contract_candidates is a valid from_model target (field case: a
    configuration-authority producing a contract). Plain boundary entities
    (not producers) are NOT valid targets — from_model asserts contract
    provenance, and an element that produces nothing has no provenance role;
    they are indexed separately for a precise error message.
    """
    directory = Path(directory)
    model_ids = set()
    candidates = []  # (path, event_name, folded_into, shared)
    boundary_ids = set()
    producers = set()
    models_exist = False
    parse_errors = []

    for path in directory.rglob("*"):
        if path.suffix not in (".yaml", ".yml") or "models" not in path.parts:
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            # A broken model file must FAIL loudly: silently skipping it also
            # disables from_model resolution (models_exist stays False), making
            # the whole links pass partially vacuous (field incident 2026-07-21:
            # a '}#' comment-spacing bug hid the report model from validation
            # until the report generator crashed on it).
            parse_errors.append(f"{path}: model YAML parse error: {e}")
            continue
        if not isinstance(data, dict) or "actors" not in data:
            continue
        models_exist = True
        for actor in data.get("actors") or []:
            if isinstance(actor, dict) and actor.get("id"):
                model_ids.add(actor["id"])
        for cand in data.get("contract_candidates") or []:
            if isinstance(cand, dict) and cand.get("event"):
                model_ids.add(cand["event"])
                candidates.append(
                    (path, cand["event"], cand.get("folded_into"), bool(cand.get("shared")))
                )
                if cand.get("producer"):
                    producers.add(cand["producer"])
        for be in data.get("boundary_entities") or []:
            if isinstance(be, dict) and be.get("id"):
                boundary_ids.add(be["id"])

    # Producer boundary entities resolve; the rest get the precise error.
    model_ids |= boundary_ids & producers
    boundary_nonproducers = boundary_ids - producers - model_ids

    return model_ids, candidates, boundary_nonproducers, models_exist, parse_errors


def collect_all_refs(directory):
    """Scan all pattern/spec files and build a reference index."""
    directory = Path(directory)
    index = {}  # kind:id → path
    all_outgoing = []  # (source_path, target_ref)
    force_outgoing = []  # (source_path, force_ref) — validated only if a force inventory exists
    model_outgoing = []  # (source_path, model_ref) — validated only if model files exist
    event_coverage = {}  # event_name → [contract spec paths declaring it]

    for path in directory.rglob("*"):
        if path.suffix not in (".yaml", ".yml", ".md"):
            continue
        data, kind, _ = load_file(path)
        if not data or not kind:
            continue
        if kind == "model":
            continue  # models are indexed by collect_model_index (ticket 048 —
            # keeps --links ref/from_force enforcement scoped to patterns/specs)

        file_id = data.get("id")
        if file_id:
            ref = f"{kind}:{file_id}"
            index[ref] = path

        # Collect outgoing references
        for ref in data.get("resolves_into", []):
            all_outgoing.append((path, ref))
        for ref in data.get("from_patterns", []):
            all_outgoing.append((path, ref))
        for link in data.get("links", []):
            if "target" in link:
                all_outgoing.append((path, link["target"]))

        # Model provenance + contract event coverage
        from_model = data.get("from_model")
        if isinstance(from_model, str) and from_model.startswith("model:"):
            model_outgoing.append((path, from_model[len("model:"):]))
        if kind == "contract" and isinstance(data.get("events"), dict):
            for event_name in data["events"]:
                event_coverage.setdefault(event_name, []).append(path)

        # Force references: serves (bare force ids) + nested from_force fields
        for ref in data.get("serves", []):
            if isinstance(ref, str) and ":" not in ref:
                force_outgoing.append((path, f"force:{ref}"))
        from_force_refs = []
        _collect_from_force_refs(data, from_force_refs)
        for ref in from_force_refs:
            if ":" not in ref:
                force_outgoing.append((path, f"force:{ref}"))

    return index, all_outgoing, force_outgoing, model_outgoing, event_coverage


def collect_discovery_graph(directory):
    """Index ledger entries + citations across all kind: discovery artifacts
    (conservation cross-file direction, grill Q6 / ticket 026).

    Returns (entries, consumed, deferred, citations):
      entries:   {(artifact_id, 'D001'): {'path', 'status', 'superseded'}}
      consumed:  {(artifact_id, 'D001')} — cited outside Decisions/Unconsumed sections
      deferred:  {(artifact_id, 'D001')} — listed under an 'Unconsumed decisions' section
      citations: [(source_path, artifact_id, 'D001')] — every citation outside
                 Decisions sections, for anchor-resolution checking
    """
    directory = Path(directory)
    entries = {}
    consumed = set()
    deferred = set()
    citations = []
    supersedes_refs = []  # (source_path, source_artifact, target_artifact_or_None, dnum)

    for path in directory.rglob("*.md"):
        data, kind, _ = load_file(path)
        if kind != "discovery" or not isinstance(data, dict) or not data.get("id"):
            continue
        artifact_id = data["id"]
        status = data.get("status")
        for heading, text in _split_sections(_discovery_body(path)):
            if heading == "decisions":
                for entry in _parse_ledger(text):
                    key = (artifact_id, f"D{entry['num']}")
                    entries[key] = {"path": path, "status": status, "superseded": False}
                    for m in SUPERSEDES_PATTERN.finditer(entry["text"]):
                        supersedes_refs.append((path, artifact_id, m.group(1), f"D{m.group(2)}"))
                continue
            found = set()
            for m in QUALIFIED_CITATION_PATTERN.finditer(text):
                found.add((m.group(1), f"D{m.group(2)}"))
            for m in BARE_CITATION_PATTERN.finditer(text):
                found.add((artifact_id, f"D{m.group(1)}"))
            for key in found:
                citations.append((path, key[0], key[1]))
                (deferred if heading == "unconsumed decisions" else consumed).add(key)

    for path, source_artifact, target_artifact, dnum in supersedes_refs:
        key = (target_artifact or source_artifact, dnum)
        if key in entries:
            entries[key]["superseded"] = True
        else:
            citations.append((path, key[0], key[1]))  # broken SUPERSEDES ref → resolution error

    return entries, consumed, deferred, citations


def validate_links(directory):
    """Validate all cross-references resolve. Returns (errors, warnings)."""
    index, all_outgoing, force_outgoing, model_outgoing, event_coverage = collect_all_refs(directory)
    model_ids, candidates, boundary_nonproducers, models_exist, model_parse_errors = collect_model_index(directory)
    errors = []
    warnings = []
    errors.extend(model_parse_errors)

    for source_path, target_ref in all_outgoing:
        if target_ref not in index:
            errors.append(f"{source_path}: link target '{target_ref}' does not resolve")

    # Force refs are enforced only once a force inventory exists (backward compat:
    # projects without design/forces/ pass; adding the first force file activates enforcement)
    has_force_inventory = any(ref.startswith("force:") for ref in index)
    if has_force_inventory:
        for source_path, target_ref in force_outgoing:
            if target_ref not in index:
                errors.append(f"{source_path}: force ref '{target_ref}' does not resolve (serves/from_force)")

    # Model refs + candidate coverage — enforced only once model files exist (same pattern)
    if models_exist:
        for source_path, model_ref in model_outgoing:
            if model_ref in model_ids:
                continue
            if model_ref in boundary_nonproducers:
                errors.append(
                    f"{source_path}: from_model ref 'model:{model_ref}' names a boundary "
                    f"entity that is not a contract producer — from_model asserts contract "
                    f"provenance; only actors, contract candidates, and boundary entities "
                    f"named as a producer in contract_candidates resolve (ticket 013)"
                )
            else:
                errors.append(
                    f"{source_path}: from_model ref 'model:{model_ref}' does not resolve "
                    f"(no actor, contract candidate, or producer boundary entity with that "
                    f"id in design/models/)"
                )
        all_candidate_events = {e for _, e, _, _ in candidates}

        # Cross-model collision lint (ticket 050, ADR 0013): candidate event
        # names are a global namespace — the coverage matching below aliases
        # same-named events across models (field incident: two areas' unrelated
        # CELL_RESULT events produced a spurious "covered by 2 contract specs").
        # Same name in 2+ model files = error unless EVERY declaration opts in
        # with `shared: true` (deliberate cross-area event, one contract owns it).
        by_event = {}  # event -> {path: shared}
        for model_path, event_name, _, shared in candidates:
            by_event.setdefault(event_name, {})[model_path] = (
                by_event.get(event_name, {}).get(model_path, False) or shared
            )
        for event_name, decls in sorted(by_event.items()):
            if len(decls) > 1 and not all(decls.values()):
                names = ", ".join(str(p) for p in sorted(decls, key=str))
                errors.append(
                    f"contract candidate '{event_name}' is declared in {len(decls)} model files "
                    f"({names}) — candidate events are a global namespace; rename one (area-"
                    f"prefixed names) or mark EVERY declaration 'shared: true' if this is "
                    f"deliberately one cross-area event (ticket 050)"
                )
            elif len(decls) == 1 and next(iter(decls.values())):
                warnings.append(
                    f"{next(iter(decls))}: contract candidate '{event_name}' is marked "
                    f"'shared: true' but only one model declares it — drop the flag or "
                    f"add the counterpart declaration"
                )

        multi_covered_reported = set()
        for model_path, event_name, folded_into, _ in candidates:
            covering = event_coverage.get(event_name, [])
            if folded_into:
                # Folded candidate (ticket 013): its payload rides inside another
                # event's contract spec (protocol cluster). Coverage follows the fold.
                if covering:
                    names = ", ".join(str(p) for p in covering)
                    errors.append(
                        f"{model_path}: candidate '{event_name}' is folded into "
                        f"'{folded_into}' but ALSO directly covered ({names}) — "
                        f"a folded candidate must not have its own contract spec"
                    )
                elif folded_into not in all_candidate_events and folded_into not in event_coverage:
                    errors.append(
                        f"{model_path}: candidate '{event_name}' folded_into "
                        f"'{folded_into}' which is not a known candidate or contract event"
                    )
                elif not event_coverage.get(folded_into):
                    warnings.append(
                        f"{model_path}: candidate '{event_name}' folded into "
                        f"'{folded_into}', which has no contract spec yet"
                    )
                continue
            if not covering:
                warnings.append(
                    f"{model_path}: contract candidate '{event_name}' has no contract spec "
                    f"(run archwright-contract, or record an explicit skip note)"
                )
            elif len(covering) > 1 and event_name not in multi_covered_reported:
                # Shared events (ticket 050) are legitimately declared in 2+
                # models — report the ownership violation once per event.
                multi_covered_reported.add(event_name)
                names = ", ".join(str(p) for p in covering)
                errors.append(
                    f"contract candidate '{event_name}' is covered by {len(covering)} contract specs "
                    f"({names}) — exactly one spec must own each candidate"
                )

    # Discovery conservation, cross-file direction (ticket 026, grill Q6):
    # every citation resolves to a real ledger entry, and every ACTIVE entry of
    # an approved artifact is consumed or explicitly deferred (nothing lost).
    entries, consumed, deferred, citations = collect_discovery_graph(directory)
    if entries or citations:  # any citation activates resolution — no ledger anywhere is not a pass
        for source_path, artifact_id, dnum in citations:
            if (artifact_id, dnum) not in entries:
                errors.append(f"{source_path}: discovery citation '{artifact_id}#{dnum}' does not resolve "
                              f"(no such ledger entry)")
        for (artifact_id, dnum), meta in sorted(entries.items(), key=lambda kv: (str(kv[1]['path']), kv[0])):
            if meta["superseded"] or meta["status"] == "superseded":
                continue  # excluded from every projection (ledger rule 1)
            key = (artifact_id, dnum)
            if key in consumed or key in deferred:
                continue
            msg = (f"{meta['path']}: conservation (nothing lost): active entry '{artifact_id}#{dnum}' "
                   f"is neither consumed by an output nor listed under 'Unconsumed decisions'")
            if meta["status"] == "approved":
                errors.append(msg)
            else:
                warnings.append(msg)

    return errors, warnings


def _build_json_doc(mode, per_item):
    """CK-21: structural results in the CK-03 document shape (status, scope,
    violations[], coverage, remaining_delta) so agents consume validate and
    check output uniformly. Structural errors are violations (severity: error);
    non-fatal WARNs are warnings (severity: warning)."""
    violations = []
    warnings_out = []
    coverage = {"checked": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0, "pending": 0}

    for item_id, kind, errors, warns in per_item:
        coverage["checked"] += 1
        if errors:
            coverage["failed"] += 1
        else:
            coverage["passed"] += 1
        for e in errors:
            violations.append({
                "spec_id": item_id, "spec_kind": kind, "invariant": "structural",
                "severity": "error", "escalate": False, "message": e,
                "suggested_route": "fix-spec",
            })
        for w in warns:
            warnings_out.append({
                "spec_id": item_id, "spec_kind": kind, "invariant": "structural",
                "severity": "warning", "message": w,
            })

    return {
        "status": "fail" if violations else "pass",
        "scope": {"mode": mode, "specs_checked": coverage["checked"], "target": None},
        "violations": violations,
        "warnings": warnings_out,
        "errors": [],
        "coverage": coverage,
        "remaining_delta": len(violations),
    }


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    json_output = "--json" in sys.argv[1:]

    if not args:
        print("Usage: archwright-validate [--json] <file>... | --links <dir>")
        sys.exit(2)

    if args[0] == "--links":
        if len(args) < 2:
            print("Usage: archwright-validate [--json] --links <directory>")
            sys.exit(2)
        errors, warnings = validate_links(args[1])
        if json_output:
            doc = _build_json_doc("links", [(args[1], "links", errors, warnings)])
            print(json.dumps(doc, indent=2, ensure_ascii=False))
        else:
            if errors:
                print(f"FAIL: {len(errors)} broken link(s)")
                for e in errors:
                    print(f"  - {e}")
            else:
                print("PASS: all links resolve")
            for w in warnings:
                print(f"  WARN: {w}")
        sys.exit(1 if errors else 0)

    exit_code = 0
    per_item = []
    for filepath in args:
        status, errors, warnings = validate_file(filepath)
        path = Path(filepath)
        data, kind, _ = load_file(path)
        kind_str = f" (kind: {kind})" if kind else ""
        per_item.append((str(path), kind, errors, warnings))

        if not json_output:
            if status == "pass":
                print(f"PASS: {path}{kind_str}")
            else:
                print(f"FAIL: {path}{kind_str}")
                for e in errors:
                    print(f"  - {e}")
            for w in warnings:
                print(f"  WARN: {w}")
        if status != "pass":
            exit_code = 1

    if json_output:
        print(json.dumps(_build_json_doc("validate", per_item), indent=2, ensure_ascii=False))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
