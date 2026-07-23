#!/usr/bin/env python3
"""score_s3.py — mechanical string diff of blind transcripts vs seeded ground truth.

Usage: python3 tools/report/probes/score_s3.py <truth.json> <answers-dir> [--json]

Answer files: <answers-dir>/<scheme>-<region>.md (free-text blind transcription of
one captured crop). Scoring is containment after whitespace normalization — the
transcript must contain each seeded string for its region VERBATIM (case-sensitive;
Unicode normalized only for whitespace runs). No fuzzy credit: the S3 floor is
about exact rule IDs and counts surviving OCR.

Exit: 0 = scored (regardless of accuracy), 2 = missing inputs.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def norm(s):
    return re.sub(r"\s+", " ", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("truth")
    ap.add_argument("answers_dir")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    truth = json.loads(Path(args.truth).read_text(encoding="utf-8"))
    adir = Path(args.answers_dir)
    if not adir.is_dir():
        print(f"ERROR: answers dir not found: {adir}", file=sys.stderr)
        return 2

    schemes = sorted({p.name.split("-", 1)[0] for p in adir.glob("*-*.md")})
    if not schemes:
        print(f"ERROR: no answer files (<scheme>-<region>.md) in {adir}", file=sys.stderr)
        return 2

    results = {"per_scheme": {}, "missing_files": []}
    for scheme in schemes:
        rows = []
        for item in truth["s3_strings"]:
            f = adir / f"{scheme}-{item['region']}.md"
            if not f.exists():
                key = f.name
                if key not in results["missing_files"]:
                    results["missing_files"].append(key)
                rows.append({**item, "hit": None})
                continue
            transcript = norm(f.read_text(encoding="utf-8"))
            rows.append({**item, "hit": norm(item["text"]) in transcript})
        scored = [r for r in rows if r["hit"] is not None]
        hits = sum(r["hit"] for r in scored)
        results["per_scheme"][scheme] = {
            "n": len(scored),
            "hits": hits,
            "pct": round(100 * hits / len(scored), 1) if scored else None,
            "misses": [r["text"] for r in scored if not r["hit"]],
            "rows": rows,
        }

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for scheme, s in results["per_scheme"].items():
            print(f"{scheme}: {s['hits']}/{s['n']} ({s['pct']}%)")
            for m in s["misses"]:
                print(f"  MISS: {m}")
        if results["missing_files"]:
            print(f"missing answer files: {results['missing_files']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
