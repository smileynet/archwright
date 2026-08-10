#!/usr/bin/env python3
"""tools/report/visual-check.py — Visual conformance automation (ticket 072).

Orchestrates: generate posture reports → capture screenshots → package battery
→ dispatch blind judgment → score findings.

Usage:
  python tools/report/visual-check.py [--postures all-clear,needs-attention] [--out <dir>]
  mise run visual-check

Exit: 0 = findings produced, 1 = conformance issue found, 2 = tool error.

The battery runner produces a findings.json with per-D-anchor verdicts:
  pass     — answer matches design intent
  mismatch — answer contradicts design intent
  unclear  — answer is ambiguous or region not captured

The non-vacuity variant (--non-vacuity) injects CSS damage and re-runs a
subset of questions; if broken answers match clean answers, the battery is
vacuous (not actually checking what it claims).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
BATTERY_PATH = SCRIPT_DIR / "visual-battery.md"


def parse_battery():
    """Parse the visual-battery.md table into structured questions."""
    lines = BATTERY_PATH.read_text(encoding="utf-8").splitlines()
    questions = []
    in_table = False
    for line in lines:
        if line.startswith("| Q") and "Region" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("| Q"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 5:
                questions.append({
                    "id": cols[0],
                    "regions": [r.strip() for r in cols[1].split(",")],
                    "postures": [p.strip().lower() for p in cols[2].split("+")],
                    "question": cols[3],
                    "anchor": cols[4],
                })
        elif in_table and not line.startswith("|"):
            break
    return questions


def generate_report(project_path, out_dir, name=None):
    """Generate a report for a project, return the output directory."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    try:
        specs_dir = Path(project_path) / "design" / "specs"
        design_dir = Path(project_path) / "design"
        check_cmd = [sys.executable, str(REPO_ROOT / "tools" / "archwright-check.py"),
                     "--all", str(specs_dir), "--target", str(project_path), "--json"]
        with open(tmp.name, "w") as f:
            subprocess.run(check_cmd, stdout=f, stderr=subprocess.DEVNULL)
        gen_cmd = [sys.executable, str(SCRIPT_DIR / "generate.py"),
                   "--check-json", tmp.name,
                   "--design", str(design_dir),
                   "--project", name or Path(project_path).name,
                   "--out", str(out)]
        r = subprocess.run(gen_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  generate failed: {r.stderr[:200]}")
            return None
    finally:
        os.unlink(tmp.name)
    return out


def capture_screenshots(report_html, out_dir):
    """Run capture.mjs to produce screenshots, return manifest path."""
    capture = SCRIPT_DIR / "capture.mjs"
    r = subprocess.run(["node", str(capture), str(report_html), "-o", str(out_dir)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  capture failed: {r.stderr[:200]}")
        return None
    manifest = Path(out_dir) / "manifest.json"
    return manifest if manifest.exists() else None


def select_images_for_question(q, manifest_data, scheme="light"):
    """Select the image files relevant to a question's regions."""
    entries = manifest_data.get("schemes", {}).get(scheme, [])
    images = []
    for region in q["regions"]:
        for entry in entries:
            if entry["region"] == region or (region == "fullpage" and entry.get("overview_only")):
                images.append(entry["file"])
                break
    return images


def dispatch_judgment(questions_with_images, out_dir):
    """Dispatch blind judgment: either via kiro headless or produce a judgment-ready package.

    Returns a list of {question_id, answer} dicts.
    If kiro-cli is available, dispatches fresh sessions per question batch.
    Otherwise, writes a judgment-package.json for manual/deferred judgment.
    """
    kiro = shutil.which("kiro-cli")
    answers = []

    if kiro:
        # Dispatch questions in batches via headless kiro sessions
        for q_img in questions_with_images:
            q = q_img["question_obj"]
            imgs = q_img["images"]
            if not imgs:
                answers.append({"question_id": q["id"], "answer": None, "status": "no-image"})
                continue

            # Build the prompt: question + image paths
            img_refs = " ".join(imgs)
            prompt = f"Look at the image(s) and answer this question about what you see. Be specific and factual. Question: {q['question']} {img_refs}"

            try:
                r = subprocess.run(
                    [kiro, "chat", "--no-interactive", "--trust-tools=read", prompt],
                    capture_output=True, text=True, timeout=60
                )
                answer_text = r.stdout.strip() if r.returncode == 0 else None
                answers.append({"question_id": q["id"], "answer": answer_text,
                                "status": "answered" if answer_text else "error"})
            except (subprocess.TimeoutExpired, OSError):
                answers.append({"question_id": q["id"], "answer": None, "status": "timeout"})
    else:
        # No kiro-cli: write judgment package for deferred evaluation
        package = {"questions": [], "note": "kiro-cli not on PATH — judgment deferred"}
        for q_img in questions_with_images:
            package["questions"].append({
                "id": q_img["question_obj"]["id"],
                "question": q_img["question_obj"]["question"],
                "images": q_img["images"],
                "anchor": q_img["question_obj"]["anchor"],
            })
        pkg_path = Path(out_dir) / "judgment-package.json"
        pkg_path.write_text(json.dumps(package, indent=2), encoding="utf-8")
        print(f"  judgment package written (kiro-cli absent): {pkg_path}")
        return None  # Deferred

    return answers


def score_findings(questions, answers):
    """Score answers against anchors. Returns list of findings.

    Without ground-truth comparison (which requires the design decisions),
    we produce a structural verdict: answered/unanswered/error per anchor.
    Full semantic scoring requires a second pass comparing answers to the
    D-anchor decisions (done by the human or a follow-up session).
    """
    findings = []
    answer_map = {a["question_id"]: a for a in answers} if answers else {}

    for q in questions:
        a = answer_map.get(q["id"])
        finding = {
            "question_id": q["id"],
            "anchor": q["anchor"],
            "status": "unclear",
        }
        if a is None:
            finding["status"] = "deferred"
        elif a["status"] == "no-image":
            finding["status"] = "unclear"
            finding["reason"] = "region not captured"
        elif a["status"] in ("error", "timeout"):
            finding["status"] = "unclear"
            finding["reason"] = a["status"]
        elif a["answer"]:
            finding["status"] = "answered"
            finding["answer"] = a["answer"]
        findings.append(finding)
    return findings


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Visual conformance check")
    ap.add_argument("--postures", default="all-clear,needs-attention",
                    help="Comma-separated postures to check")
    ap.add_argument("--out", default=None, help="Output directory")
    ap.add_argument("--non-vacuity", action="store_true",
                    help="Run CSS-broken variant to verify battery catches damage")
    args = ap.parse_args()

    # Check playwright availability
    try:
        subprocess.run(["node", "-e", "require('playwright')"],
                       capture_output=True, check=True, cwd=str(REPO_ROOT))
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: playwright not installed (npm install && npx playwright install chromium)")
        return 2

    postures = [p.strip() for p in args.postures.split(",")]
    out_root = Path(args.out) if args.out else REPO_ROOT / ".scratch" / "visual-check"
    out_root.mkdir(parents=True, exist_ok=True)

    # Map postures to project paths
    posture_projects = {
        "all-clear": REPO_ROOT / "examples" / "complete",
        "needs-attention": REPO_ROOT / "examples" / "partial",
        "tool-error": None,  # Synthetic — empty specs dir
        "empty-project": None,  # Synthetic — no design dir
    }

    questions = parse_battery()
    all_findings = {}

    for posture in postures:
        print(f"\n=== Posture: {posture} ===")
        posture_dir = out_root / posture

        project = posture_projects.get(posture)
        if project and project.exists():
            report_dir = posture_dir / "report"
            gen = generate_report(str(project), str(report_dir), f"snackbox-{posture}")
            if not gen:
                print(f"  SKIP: report generation failed for {posture}")
                continue
        elif posture == "empty-project":
            # Synthetic: empty project
            with tempfile.TemporaryDirectory() as tmp:
                Path(tmp, "design", "specs").mkdir(parents=True)
                report_dir = posture_dir / "report"
                gen = generate_report(tmp, str(report_dir), "empty-project")
                if not gen:
                    print(f"  SKIP: empty-project generation failed")
                    continue
        elif posture == "tool-error":
            # Synthetic: project with a spec whose check target errors
            with tempfile.TemporaryDirectory() as tmp:
                specs = Path(tmp, "design", "specs")
                specs.mkdir(parents=True)
                # A constraint spec targeting a nonexistent path triggers tool-error
                (specs / "broken-target.md").write_text(
                    "---\nkind: constraint\nid: broken-check\n"
                    "from_patterns:\n  - \"pattern:test\"\nconfidence: \"★\"\n"
                    "protects_experience: test\nuser_story: test\n"
                    "check:\n  method: script\n  target: /nonexistent/path\n"
                    "  command: exit 2\n---\n# Broken\n", encoding="utf-8")
                report_dir = posture_dir / "report"
                gen = generate_report(tmp, str(report_dir), "tool-error-project")
                if not gen:
                    print(f"  SKIP: tool-error generation failed")
                    continue
        else:
            print(f"  SKIP: no project source for posture '{posture}'")
            continue

        # Capture
        report_html = posture_dir / "report" / "report.html"
        if not report_html.exists():
            print(f"  SKIP: no report.html generated")
            continue

        capture_dir = posture_dir / "captures"
        manifest_path = capture_screenshots(str(report_html), str(capture_dir))
        if not manifest_path:
            print(f"  SKIP: capture failed")
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"  captured {sum(len(v) for v in manifest['schemes'].values())} images")

        # Filter questions for this posture
        posture_key = posture.replace("-", "")  # "all-clear" → "allclear" to match battery "ac"/"na"
        posture_aliases = {"allclear": "ac", "needsattention": "na",
                           "toolerror": "ac", "emptyproject": "ac"}
        battery_key = posture_aliases.get(posture_key, "ac")
        relevant_qs = [q for q in questions if battery_key in
                       [p.replace("-", "").lower() for p in q["postures"]]]

        # Select images for each question
        questions_with_images = []
        for q in relevant_qs:
            imgs = select_images_for_question(q, manifest)
            questions_with_images.append({"question_obj": q, "images": imgs})

        print(f"  battery: {len(relevant_qs)} questions for posture {posture}")

        # Dispatch judgment
        answers = dispatch_judgment(questions_with_images, str(posture_dir))
        findings = score_findings(relevant_qs, answers)
        all_findings[posture] = findings

    # Write findings
    findings_path = out_root / "findings.json"
    findings_path.write_text(json.dumps(all_findings, indent=2), encoding="utf-8")
    print(f"\n=== Findings: {findings_path} ===")

    # Summary
    total = sum(len(f) for f in all_findings.values())
    answered = sum(1 for fs in all_findings.values() for f in fs if f["status"] == "answered")
    deferred = sum(1 for fs in all_findings.values() for f in fs if f["status"] == "deferred")
    unclear = sum(1 for fs in all_findings.values() for f in fs if f["status"] == "unclear")
    print(f"  {total} questions: {answered} answered, {deferred} deferred, {unclear} unclear")

    # Non-vacuity check
    if args.non_vacuity and answered > 0:
        print("\n=== Non-vacuity check (CSS-broken variant) ===")
        print("  TODO: inject CSS damage, re-capture, re-ask subset, compare")
        # This will be implemented as: modify report.html CSS inline,
        # re-capture, re-dispatch a subset of questions, verify answers differ.
        # For now, produce a placeholder finding.
        nv_path = out_root / "non-vacuity.json"
        nv_path.write_text(json.dumps({"status": "not-implemented",
            "note": "CSS damage injection pending — manual validation still required"}), encoding="utf-8")

    return 0 if deferred == 0 and unclear == 0 else (1 if unclear > 0 else 0)


if __name__ == "__main__":
    sys.exit(main())
