#!/usr/bin/env python3
"""archwright-report generator: canonical check document -> report bundle.

Usage:
  python3 tools/report/generate.py --check-json <doc.json> [--design <dir>] [--out <dir>] [--project <name>]

Consumes ONLY the CK-03 canonical document + design/ YAML (models, vocabulary)
— never checker internals (dependency: report-reads-canonical-only).
Writes: report.html (interactive surface), REPORT.md (mirror), report.json
(canonical doc + model_view + asks derived blocks).

Exit codes: 0 = bundle written, 2 = input/tool error (incl. vocabulary
completeness failures — an untranslated term never ships).
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import derive
import render_html
import render_md
from vocab import GenerationError, Vocabulary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-json", required=True, help="CK-03 document (archwright-check --json output)")
    ap.add_argument("--design", default="design", help="design/ dir (models read from <design>/models)")
    ap.add_argument("--out", default=None, help="output dir (default <design>/report)")
    ap.add_argument("--project", default=None, help="project display name (default: cwd name)")
    ap.add_argument("--vocabulary", default=None, help="override vocabulary map YAML")
    args = ap.parse_args()

    try:
        doc = json.loads(Path(args.check_json).read_text(encoding="utf-8"))
        vocab = Vocabulary(args.vocabulary)
        model = derive.load_model(Path(args.design) / "models")

        auto = os.environ.get("ARCHWRIGHT_AUTO_APPROVE", "off")
        if auto not in ("off", "code-fixes", "all"):
            print(f"Error: ARCHWRIGHT_AUTO_APPROVE must be off|code-fixes|all, got '{auto}'")
            return 2

        asks_block = derive.build_asks(doc, vocab, auto_approve=auto)
        model_view = derive.build_model_view(model, doc, vocab)
        derive.pin_violations(asks_block, model_view, model)

        bundle = {
            "canonical": doc,
            "model_view": model_view,
            "asks": asks_block,
            "posture": derive.posture(doc, asks_block),
            "project": args.project or Path.cwd().name,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        }

        out = Path(args.out or (Path(args.design) / "report"))
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.html").write_text(
            render_html.render_html(bundle, model, vocab, out), encoding="utf-8")
        (out / "REPORT.md").write_text(render_md.render_md(bundle, vocab), encoding="utf-8")
        json_bundle = dict(doc)
        json_bundle["model_view"] = model_view
        json_bundle["asks"] = dict(asks_block, posture=bundle["posture"])
        (out / "report.json").write_text(json.dumps(json_bundle, indent=2), encoding="utf-8")
        print(f"Report bundle written to {out} (posture: {bundle['posture']})")
        return 0
    except GenerationError as e:
        print(f"Error: {e}")
        return 2
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"Error: cannot generate report: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
