#!/usr/bin/env python3
"""archwright-forces-gen: Generate durable per-force files from a force inventory.

Usage:
  archwright-forces-gen <inventory.yaml> [-o <forces-dir>]

Reads the working inventory (product_forces + forces lists, the shape the
archwright-forces skill produces) and emits one design/forces/<id>.md file per
force in the template shape (tools/templates/force.md). Mechanical projection —
the skill decides WHAT the forces are; this tool only formats them.

Exit codes: 0 = files written, 2 = tool/input error.
"""

import sys
import yaml
from pathlib import Path

VALID_POLARITIES = {"desire", "constraint-hard", "constraint-soft"}


def _title(slug):
    return slug.replace("-", " ").title()


def render_force(f, is_product):
    polarity = f.get("polarity", "")
    if polarity not in VALID_POLARITIES:
        raise ValueError(f"force '{f.get('id', '?')}': invalid polarity '{polarity}' "
                         f"(expected one of {sorted(VALID_POLARITIES)})")
    if not f.get("id") or not f.get("statement") or not f.get("provenance"):
        raise ValueError(f"force '{f.get('id', '?')}': id, statement, and provenance are required")

    pol = "desire" if polarity == "desire" else "constraint"
    fm = ["---", "kind: force", f"id: {f['id']}", f"polarity: {pol}"]
    if pol == "constraint":
        fm.append(f"hardness: {polarity.split('-')[1]}")
    fm.append(f"evidence_level: {f.get('evidence_level', 'L4')}")
    fm.append(f'source: "{"; ".join(p["source"] for p in f["provenance"])}"')
    if pol == "constraint" and f.get("serves"):
        serves = f["serves"] if isinstance(f["serves"], list) else [f["serves"]]
        fm.append(f"serves: [{', '.join(serves)}]")
    fm.append("---")

    who = f.get("who") or "the world (platform limits, prior decisions)"
    evidence = "\n".join(f'- `{p["source"]}`: "{p["quote"]}"' for p in f["provenance"])
    body = (f"\n# {_title(f['id'])}\n\n## Statement\n\n{f['statement']}\n\n"
            f"## Who Feels It\n\n{who.capitalize() if is_product else who}\n\n"
            f"## Evidence\n\n{evidence}\n")
    return "\n".join(fm) + "\n" + body


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        print("Usage: archwright-forces-gen <inventory.yaml> [-o <forces-dir>]")
        sys.exit(2)
    inv_path = Path(args[0])
    out_dir = Path("design/forces")
    if "-o" in args:
        idx = args.index("-o")
        if idx + 1 >= len(args):
            print("Error: -o requires a directory argument")
            sys.exit(2)
        out_dir = Path(args[idx + 1])

    try:
        inv = yaml.safe_load(inv_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error: cannot read inventory: {e}")
        sys.exit(2)
    if not isinstance(inv, dict):
        print("Error: inventory is not a YAML mapping")
        sys.exit(2)

    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    try:
        for f in inv.get("product_forces") or []:
            (out_dir / f"{f['id']}.md").write_text(render_force(f, True), encoding="utf-8")
            written += 1
        for f in inv.get("forces") or []:
            (out_dir / f"{f['id']}.md").write_text(render_force(f, False), encoding="utf-8")
            written += 1
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(2)

    if written == 0:
        print("Error: inventory contains no forces (product_forces/forces lists empty or missing)")
        sys.exit(2)
    print(f"Generated {written} force file(s) in {out_dir}")


if __name__ == "__main__":
    main()
