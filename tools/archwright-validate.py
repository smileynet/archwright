#!/usr/bin/env python3
"""archwright-validate: Validate pattern and spec files against schemas.

Usage:
  archwright-validate <file>...          Validate individual files
  archwright-validate --links <dir>      Validate all links resolve
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

VALID_KINDS = {"pattern", "behavior", "contract", "constraint", "dependency", "boundary", "protocol", "force"}
VALID_CONFIDENCES = {"★★", "★", "—"}
VALID_SCALES = {"premise", "loops-systems", "verbs-interactions", "feel-finish"}
VALID_POLARITIES = {"desire", "constraint"}
VALID_HARDNESS = {"hard", "soft"}
VALID_EVIDENCE_LEVELS = {"L1", "L2", "L3", "L4", "L5"}
LINK_REF_PATTERN = re.compile(r"^(behavior|contract|constraint|dependency|boundary|protocol|pattern|force):.+$")


def extract_frontmatter(path):
    """Extract YAML frontmatter from a markdown file."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None, "File does not start with YAML frontmatter (---)"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Malformed frontmatter: no closing ---"
    try:
        data = yaml.safe_load(parts[1])
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
            return data, data.get("kind"), errors
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


def validate_file(path):
    """Validate a single file. Returns (status, errors, warnings)."""
    path = Path(path)
    if not path.exists():
        return "error", [f"File not found: {path}"], []

    data, kind, load_errors = load_file(path)
    if load_errors:
        return "error", load_errors, []

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
    elif kind in ("boundary", "protocol"):
        errors = []  # minimal validation for now
    else:
        errors = [f"unknown kind '{kind}'"]

    warnings = []
    if kind in ("behavior", "contract", "constraint", "dependency") and not data.get("protects_experience"):
        warnings.append(
            "no 'protects_experience' — link a modeled experience id (preferred) or a "
            "product-force id, so the spec traces to what users feel"
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

    Returns (model_ids, candidates, boundary_nonproducers, models_exist).
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
    candidates = []  # (path, event_name, folded_into)
    boundary_ids = set()
    producers = set()
    models_exist = False

    for path in directory.rglob("*"):
        if path.suffix not in (".yaml", ".yml") or "models" not in path.parts:
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
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
                candidates.append((path, cand["event"], cand.get("folded_into")))
                if cand.get("producer"):
                    producers.add(cand["producer"])
        for be in data.get("boundary_entities") or []:
            if isinstance(be, dict) and be.get("id"):
                boundary_ids.add(be["id"])

    # Producer boundary entities resolve; the rest get the precise error.
    model_ids |= boundary_ids & producers
    boundary_nonproducers = boundary_ids - producers - model_ids

    return model_ids, candidates, boundary_nonproducers, models_exist


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


def validate_links(directory):
    """Validate all cross-references resolve. Returns (errors, warnings)."""
    index, all_outgoing, force_outgoing, model_outgoing, event_coverage = collect_all_refs(directory)
    model_ids, candidates, boundary_nonproducers, models_exist = collect_model_index(directory)
    errors = []
    warnings = []

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
        all_candidate_events = {e for _, e, _ in candidates}
        for model_path, event_name, folded_into in candidates:
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
            elif len(covering) > 1:
                names = ", ".join(str(p) for p in covering)
                errors.append(
                    f"contract candidate '{event_name}' is covered by {len(covering)} contract specs "
                    f"({names}) — exactly one spec must own each candidate"
                )

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
