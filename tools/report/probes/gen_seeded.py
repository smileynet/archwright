#!/usr/bin/env python3
"""gen_seeded.py — seeded report pages with known ground truth (ticket 047).

Generates HTML variants that mimic tools/report/templates/report.html geometry
(same CSS, h2-delimited sections, header h1, .verdict) so capture.mjs discovers
identical regions. Every visible fact is recorded in ground-truth.json — the
probe scorecards diff blind answers against this file, never against memory.

Usage: python3 tools/report/probes/gen_seeded.py [-o <outdir>]
Output: <outdir>/pages/{base,v01..v10}.html + <outdir>/ground-truth.json
Exit: 0 = generated, 2 = error.

Variants:
  base          — all elements present (S1 question target + S3 string target)
  v01,v03,v05,v07,v09 — one known element REMOVED each (S2 absence probes)
  v02,v04,v06,v08,v10 — intact controls, same questions (S2 presence probes)
"""

import argparse
import json
import sys
from pathlib import Path

# Style copied from tools/report/templates/report.html so seeded pages render
# at the exact geometry the real capture pipeline sees (light + dark).
STYLE = """
:root { color-scheme: light dark;
  --success:#1a7f37; --danger:#cf222e; --warning:#9a6700; --neutral:#6e7781; --info:#0969da;
  --fg:#1f2328; --bg:#ffffff; --card:#f6f8fa; --border:#d1d9e0; }
@media (prefers-color-scheme: dark) { :root {
  --success:#3fb950; --danger:#f85149; --warning:#d29922; --neutral:#8b949e; --info:#58a6ff;
  --fg:#e6edf3; --bg:#0d1117; --card:#161b22; --border:#30363d; } }
body { font-family: system-ui, sans-serif; font-size:15px; color:var(--fg); background:var(--bg);
  max-width:900px; margin:0 auto; padding:16px; }
h1 { font-size:20px; line-height:26px; } h2 { font-size:15px; letter-spacing:.05em; }
code, pre { font-family: ui-monospace, monospace; }
.count { font-variant-numeric: tabular-nums; }
.card { background:var(--card); border:1px solid var(--border); border-radius:8px; padding:16px; margin:8px 0; }
.status-pass{color:var(--success)} .status-fail{color:var(--danger)}
.status-warn{color:var(--warning)} .status-skip{color:var(--neutral)}
.glyph{margin-right:8px} .verdict{font-size:20px; margin:24px 0}
.rec{font-weight:600}
.meta{color:var(--neutral); font-size:12.5px}
table{border-collapse:collapse} td{padding:4px 12px 4px 0}
"""

# ---------------------------------------------------------------------------
# Seeded facts. Any string listed in S3_STRINGS must appear VERBATIM on the
# base page — score_s3.py fails loudly if generation breaks that link.
# ---------------------------------------------------------------------------

FACTS = {
    "project": "Snackbox",
    "checked_date": "2026-07-23",
    "run_label": "run k47",
    "verdict": "2 of 21 checks failing \u2014 decisions waiting",
    "verdict_glyph": "\u2717",
    "asks": [
        "constraint:cart-guard-17",
        "behavior:relay-fsm",
        "dependency:report-reads-canonical-only",
    ],
    "check_rows": [
        ("constraint:no-direct-db-writes", "pass", "\u2713"),
        ("behavior:oven-door-interlock", "pass", "\u2713"),
        ("behavior:relay-fsm", "fail", "\u2717"),
        ("contract:order-placed-v2", "warn", "\u26a0"),
        ("dependency:ui-never-imports-storage", "skip", "\u25cb"),
    ],
    "coverage_pct": "94%",
    "coverage_line": "17 of 18 specs implemented",
    "streak_line": "12-run pass streak",
    "promotion_line": "promotion candidate: constraint:cart-guard-17",
    "recommendation": "Recommendation: ratify the demotion of behavior:relay-fsm to \u2605",
}

# S3 ground truth: exact strings + the capture region each lives in.
S3_STRINGS = [
    {"text": "Snackbox \u2014 Design Check", "region": "header"},
    {"text": "checked 2026-07-23", "region": "header"},
    {"text": "run k47", "region": "header"},
    {"text": "2 of 21 checks failing \u2014 decisions waiting", "region": "verdict"},
    {"text": "constraint:cart-guard-17", "region": "section-needs-attention"},
    {"text": "behavior:relay-fsm", "region": "section-needs-attention"},
    {"text": "dependency:report-reads-canonical-only", "region": "section-needs-attention"},
    {"text": "constraint:no-direct-db-writes", "region": "section-checks"},
    {"text": "behavior:oven-door-interlock", "region": "section-checks"},
    {"text": "contract:order-placed-v2", "region": "section-checks"},
    {"text": "dependency:ui-never-imports-storage", "region": "section-checks"},
    {"text": "pass", "region": "section-checks"},
    {"text": "fail", "region": "section-checks"},
    {"text": "warn", "region": "section-checks"},
    {"text": "skip", "region": "section-checks"},
    {"text": "94%", "region": "section-coverage"},
    {"text": "17 of 18 specs implemented", "region": "section-coverage"},
    {"text": "12-run pass streak", "region": "section-stability"},
    {"text": "promotion candidate: constraint:cart-guard-17", "region": "section-stability"},
    {"text": "Recommendation: ratify the demotion of behavior:relay-fsm to \u2605",
     "region": "section-stability"},
]

# S2 variants: (variant id, removed element key or None, run label suffix).
# Each removal is paired with the intact control asked the SAME question.
S2_VARIANTS = [
    ("v01", "verdict_glyph"),
    ("v02", None),           # control for v01
    ("v03", "stability_section"),
    ("v04", None),           # control for v03
    ("v05", "warn_glyph"),
    ("v06", None),           # control for v05
    ("v07", "recommendation"),
    ("v08", None),           # control for v07
    ("v09", "run_label"),
    ("v10", None),           # control for v09
]

S2_QUESTIONS = {
    "verdict_glyph": "What text and what symbols or glyphs, if any, appear in the "
                     "large verdict line near the top of the page?",
    "stability_section": "What section headings are visible on the page? List them "
                         "exactly as written.",
    "warn_glyph": "Transcribe the rows of the checks table, including any symbols "
                  "that appear in each row.",
    "recommendation": "What recommendation text, if any, appears anywhere on the page?",
    "run_label": "What metadata (dates, run labels, or similar) is visible in the "
                 "page header?",
}


def render(removed=None, run_suffix=""):
    f = FACTS
    run_label = "" if removed == "run_label" else f["run_label"] + run_suffix

    verdict_glyph = "" if removed == "verdict_glyph" else (
        f'<span class="glyph status-fail">{f["verdict_glyph"]}</span>')

    asks = "\n".join(
        f'<li><code>{a}</code> \u2014 decision waiting</li>' for a in f["asks"])

    rows = []
    for rule, status, glyph in f["check_rows"]:
        if removed == "warn_glyph" and status == "warn":
            glyph_html = ""
        else:
            glyph_html = f'<span class="glyph status-{status}">{glyph}</span>'
        rows.append(f'<tr><td><code>{rule}</code></td>'
                    f'<td class="status-{status}">{glyph_html}{status}</td></tr>')
    rows = "\n".join(rows)

    stability = "" if removed == "stability_section" else f"""
<h2>Stability</h2>
<div class="card">
  <p><span class="count">{f["streak_line"]}</span> on the constraint suite.</p>
  <p>{f["promotion_line"]}</p>
  {'' if removed == 'recommendation' else f'<p class="rec">{f["recommendation"]}</p>'}
</div>"""
    # Recommendation lives inside Stability; when Stability itself is removed the
    # recommendation question is not asked of that variant (v03 asks headings).

    meta = f'checked {f["checked_date"]}' + (f' \u00b7 {run_label}' if run_label else "")

    return f"""<!-- seeded probe page (ticket 047) — generated by gen_seeded.py; do not edit -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{f["project"]} \u2014 Design Check</title>
<style>{STYLE}</style>
</head>
<body>
<header>
  <h1>{f["project"]} \u2014 Design Check <span class="meta">{meta}</span></h1>
</header>
<p class="verdict">{verdict_glyph}{f["verdict"]}</p>
<h2>Needs attention</h2>
<div class="card"><ul>
{asks}
</ul></div>
<h2>Checks</h2>
<div class="card"><table>
{rows}
</table></div>
<h2>Coverage</h2>
<div class="card">
  <p><span class="count">{f["coverage_pct"]}</span> \u2014 {f["coverage_line"]}.</p>
</div>
{stability}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--outdir", default=".scratch/vision-probes")
    args = ap.parse_args()
    out = Path(args.outdir)
    pages = out / "pages"
    pages.mkdir(parents=True, exist_ok=True)

    # Base page (S1 + S3 target). Self-check: every S3 string must be verbatim.
    base_html = render()
    missing = [s["text"] for s in S3_STRINGS if s["text"] not in base_html]
    if missing:
        print(f"ERROR: seeded strings missing from base page: {missing}", file=sys.stderr)
        return 2
    (pages / "base.html").write_text(base_html, encoding="utf-8")

    truth = {
        "facts": FACTS,
        "s3_strings": S3_STRINGS,
        "s2_variants": [],
    }

    # Element-to-question ground truth per S2 variant. Controls get the question
    # of the removal they pair with (previous variant in the list).
    for i, (vid, removed) in enumerate(S2_VARIANTS):
        question_key = removed if removed else S2_VARIANTS[i - 1][1]
        html = render(removed=removed, run_suffix=f" \u00b7 {vid}" if removed != "run_label" else "")
        (pages / f"{vid}.html").write_text(html, encoding="utf-8")
        truth["s2_variants"].append({
            "id": vid,
            "removed": removed,
            "element": question_key,
            "element_present": removed is None,
            "question": S2_QUESTIONS[question_key],
        })

    (out / "ground-truth.json").write_text(
        json.dumps(truth, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"generated base + {len(S2_VARIANTS)} variants -> {pages}")
    print(out / "ground-truth.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
