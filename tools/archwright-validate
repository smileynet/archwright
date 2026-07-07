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

VALID_KINDS = {"pattern", "behavior", "contract", "constraint", "dependency", "boundary", "protocol"}
VALID_CONFIDENCES = {"★★", "★", "—"}
VALID_SCALES = {"premise", "loops-systems", "verbs-interactions", "feel-finish"}
LINK_REF_PATTERN = re.compile(r"^(behavior|contract|constraint|dependency|boundary|protocol|pattern):.+$")


def extract_frontmatter(path):
    """Extract YAML frontmatter from a markdown file."""
    content = path.read_text()
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
            data = yaml.safe_load(path.read_text())
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


def validate_file(path):
    """Validate a single file. Returns (status, errors)."""
    path = Path(path)
    if not path.exists():
        return "error", [f"File not found: {path}"]

    data, kind, load_errors = load_file(path)
    if load_errors:
        return "error", load_errors

    if kind == "pattern":
        errors = validate_pattern(data, path)
    elif kind == "behavior":
        errors = validate_behavior(data, path)
    elif kind in ("constraint", "dependency"):
        errors = validate_constraint_or_dependency(data, path)
    elif kind in ("contract", "boundary", "protocol"):
        errors = []  # minimal validation for now
    else:
        errors = [f"unknown kind '{kind}'"]

    return ("pass" if not errors else "fail"), errors


def collect_all_refs(directory):
    """Scan all pattern/spec files and build a reference index."""
    directory = Path(directory)
    index = {}  # kind:id → path
    all_outgoing = []  # (source_path, target_ref)

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

    return index, all_outgoing


def validate_links(directory):
    """Validate all cross-references resolve."""
    index, all_outgoing = collect_all_refs(directory)
    errors = []

    for source_path, target_ref in all_outgoing:
        if target_ref not in index:
            errors.append(f"{source_path}: link target '{target_ref}' does not resolve")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: archwright-validate <file>... | --links <dir>")
        sys.exit(2)

    if sys.argv[1] == "--links":
        if len(sys.argv) < 3:
            print("Usage: archwright-validate --links <directory>")
            sys.exit(2)
        errors = validate_links(sys.argv[2])
        if errors:
            print(f"FAIL: {len(errors)} broken link(s)")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            print("PASS: all links resolve")
            sys.exit(0)

    exit_code = 0
    for filepath in sys.argv[1:]:
        status, errors = validate_file(filepath)
        path = Path(filepath)
        data, kind, _ = load_file(path)
        kind_str = f" (kind: {kind})" if kind else ""

        if status == "pass":
            print(f"PASS: {path}{kind_str}")
        else:
            print(f"FAIL: {path}{kind_str}")
            for e in errors:
                print(f"  - {e}")
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
