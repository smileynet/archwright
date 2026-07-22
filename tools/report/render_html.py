"""Render the web surface (single self-contained HTML file).

Surface copy comes from the vocabulary map only; internal terms render solely
through the disclosure partial (constraint:vocabulary-map-surface)."""

import html
import json
import string
import subprocess
from pathlib import Path

TEMPLATES = Path(__file__).parent / "templates"


def _tpl(name):
    return string.Template(Path(TEMPLATES / name).read_text(encoding="utf-8"))


def _esc(s):
    return html.escape(str(s if s is not None else ""))


def _disclosure(summary, item):
    ev = "\n".join((item.get("evidence") or [])[:8])
    return _tpl("disclosure.html").substitute(
        summary=_esc(summary), spec_id=_esc(item.get("spec_id")),
        confidence_glyph=_esc(item.get("confidence", "—")),
        suggested_route=_esc(item.get("suggested_route", "")),
        fingerprint=_esc((item.get("fingerprints") or [""])[0]),
        from_force=_esc(item.get("from_force")), from_pattern=_esc(item.get("from_pattern")),
        evidence=_esc(ev))


def _ask_card(ask, vocab, violation_by_ref):
    v = violation_by_ref.get(ask["source"]["ref"]) or {}
    parts = ['<div class="card ask" data-ask-id="%s" data-ask-type="%s">'
             % (_esc(ask["ask_id"]), _esc(ask["ask_type"]))]
    glyph = "?" if ask["ask_type"] == "decision" else ("💡" if ask["ask_type"] == "suggestion" else vocab.status_glyph("fail"))
    parts.append('<p><span class="glyph status-fail">%s</span><strong>%s</strong> [%s]</p>'
                 % (glyph, _esc(ask["title"]), _esc(ask["confidence_phrase"])))
    cp = ask.get("contrast_pair")
    if cp:
        parts.append("<p>The design says: %s<br>The code does: %s</p>"
                     % (_esc(cp.get("expected")), _esc(cp.get("actual"))))
    if ask["ask_type"] == "decision":
        parts.append("<p>Pick one:</p>")
        for opt in ask.get("options") or []:
            rec = ' <span class="rec">← recommended</span>' if opt["recommended"] else ""
            parts.append(('<label><input type="radio" name="opt-%s" value="%s" '
                          'onchange="chooseOption(this)">%s%s</label><br>')
                         % (_esc(ask["ask_id"]), _esc(opt["id"]), _esc(opt["label"]), rec))
        parts.append(('<label>Something else: <input type="text" data-freeform="%s" '
                      'onchange="freeform(this)"></label>') % _esc(ask["ask_id"]))
    elif ask["ask_type"] == "approval":
        parts.append('<p>Recommended: <span class="rec">%s</span> '
                     '<button onclick="approveFix(this)">Approve Fix</button> '
                     '<button onclick="reroute(this)">Review / Amend Rule</button></p>'
                     % _esc(ask["recommendation"]["action"]))
    else:
        parts.append('<p>%s <button onclick="dismissAsk(this)">Not now</button></p>'
                     % _esc(ask["recommendation"]["action"]))
    if ask["source"]["kind"] == "violation" and v:
        parts.append(_disclosure("why we recommend this · history · why this rule exists", v))
    parts.append("</div>")
    return "\n".join(parts)


def _diagram_svg(model, out_dir):
    """Pre-rendered inline SVG via smcat when available; plain list fallback."""
    if model is None:
        return None
    actors = [a for a in model.get("actors") or [] if a.get("states")]
    if not actors:
        return None
    actor = actors[0]
    lines = []
    for st in actor["states"]:
        sid = st["id"] if isinstance(st, dict) else st
        label = (st.get("label") if isinstance(st, dict) else None) or sid
        lines.append('%s [label="%s"]' % (sid.replace("-", "_"), label))
    src = ",\n".join(lines) + ";"
    try:
        r = subprocess.run(["smcat", "-T", "svg", "-"], input=src,
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip().startswith("<"):
            return r.stdout
    except (OSError, subprocess.TimeoutExpired):
        pass
    items = "".join("<li>%s</li>" % _esc((s.get("label") if isinstance(s, dict) else None) or
                                          (s["id"] if isinstance(s, dict) else s))
                    for s in actor["states"])
    return "<ul>%s</ul>" % items


def render_html(bundle, model, vocab, out_dir):
    doc = bundle["canonical"]
    asks_block, model_view = bundle["asks"], bundle["model_view"]
    post = bundle["posture"]
    violation_by_ref = {v["spec_id"]: v for v in doc.get("violations") or []}

    counts = asks_block["counts"]
    if post == "all-clear":
        verdict = '<span class="glyph status-pass">%s</span>%s' % (
            vocab.status_glyph("pass"), _esc(vocab.surface("all-clear")))
    elif post in ("tool-error", "empty-project"):
        verdict = _esc(vocab.surface(post))
    else:
        verdict = _esc("%d %s · %d %s" % (
            counts["decision"], vocab.surface("decision") + ("s" if counts["decision"] != 1 else ""),
            counts["approval"] - counts["auto_approved"],
            vocab.surface("approval") + ("s" if counts["approval"] != 1 else "")))
    verdict += ' <span class="meta">auto-approve: %s</span>' % _esc(asks_block["auto_approve"])

    sections = []
    blocking = [a for a in asks_block["asks"] if not a["auto_approved"]]
    decisions = [a for a in blocking if a["ask_type"] == "decision"]
    approvals = [a for a in blocking if a["ask_type"] == "approval"]
    suggestions = [a for a in blocking if a["ask_type"] == "suggestion"]
    if counts["auto_approved"]:
        sections.append('<p class="meta">%d fixes auto-approved (see log)</p>' % counts["auto_approved"])
    for title, group in (("DECISIONS", decisions), ("APPROVALS", approvals)):
        if group:
            sections.append("<h2>%s (%d)</h2>" % (title, len(group)))
            sections.extend(_ask_card(a, vocab, violation_by_ref) for a in group)
    asks_section = "\n".join(sections)

    svg = _diagram_svg(model, out_dir)
    diagram_section = ""
    if svg:
        badge = ("every step verified " + vocab.status_glyph("pass")) if post == "all-clear" \
            else "steps needing attention are marked " + vocab.status_glyph("fail")
        diagram_section = ('<h2>HOW %s WORKS</h2><div class="diagram">%s</div>'
                           '<p class="meta">%s · click any step for details</p>'
                           % (_esc(bundle["project"].upper()), svg, _esc(badge)))
    elif model_view.get("note"):
        diagram_section = '<p class="meta">%s</p>' % _esc(model_view["note"])

    unverified = []
    pendings = [s for s in doc.get("skips") or [] if "pending" in (s.get("reason") or "")]
    skips = [s for s in doc.get("skips") or [] if "pending" not in (s.get("reason") or "")]
    baselined = [v for v in doc.get("violations") or [] if v.get("baselined")]
    if pendings or skips or baselined:
        unverified.append("<h2>WHAT ISN'T VERIFIED</h2>")
        for s in skips:
            unverified.append('<p><span class="glyph status-skip">%s</span>%s — %s</p>'
                              % (vocab.status_glyph("skip"), _esc(vocab.surface("skip")), _esc(s.get("reason"))))
        if pendings:
            unverified.append('<p><span class="glyph status-pending">%s</span>%d rules: %s</p>'
                              % (vocab.status_glyph("pending"), len(pendings), _esc(vocab.surface("pending"))))
            unverified.append('<ul class="meta">%s</ul>' % ''.join(
                '<li>%s</li>' % _esc(s.get("spec_id") or s.get("reason") or "unnamed rule")
                for s in pendings))
        for v in baselined:
            unverified.append('<p><span class="glyph status-warn">%s</span>%s — %s</p>'
                              % (vocab.status_glyph("warn"), _esc(vocab.surface("baselined")), _esc(v.get("message"))))
    elif post == "all-clear":
        unverified.append("<h2>WHAT ISN'T VERIFIED</h2><p>Nothing — every rule was checked this run.</p>")
    unverified_section = "\n".join(unverified)

    stability_section = ""
    if suggestions:
        stability_section = "<h2>STABILITY</h2>" + "\n".join(
            _ask_card(a, vocab, violation_by_ref) for a in suggestions)

    page_js = Path(TEMPLATES / "page.js").read_text(encoding="utf-8")
    run = (doc.get("code_state") or {})
    page_wiring = """
var page = ArchwrightReport.newPage(%s);
function _rec(el, response) {
  var card = el.closest('.ask');
  ArchwrightReport.pageRecord(page, card.dataset.askId, response);
  var n = Object.keys(page.responses).length;
  document.getElementById('response-count').textContent = n + ' response' + (n>1?'s':'') + ' recorded';
  document.getElementById('response-bar').style.display = 'block';
}
function approveFix(el) { _rec(el, { kind: 'approve-fix' }); }
function reroute(el) { _rec(el, { kind: 'reroute-to-decision', note: null }); }
function chooseOption(el) { _rec(el, { kind: 'choose-option', option_id: el.value }); }
function freeform(el) { _rec(el, { kind: 'freeform', text: el.value }); }
function dismissAsk(el) { _rec(el, { kind: 'dismiss' }); }
function saveResponses() {
  var blob = new Blob([ArchwrightReport.exportResponses(page)], { type: 'application/json' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'responses.json';
  a.click();
}
""" % json.dumps({"commit": run.get("commit"), "dirty": run.get("dirty")})

    return _tpl("report.html").substitute(
        project=_esc(bundle["project"]), checked_at=_esc(bundle["generated_at"]),
        run_label=_esc((run.get("commit") or "no-git")[:7] + (" · uncommitted changes present" if run.get("dirty") else "")),
        verdict_line=verdict, asks_section=asks_section, diagram_section=diagram_section,
        unverified_section=unverified_section, stability_section=stability_section,
        page_js=page_js, page_wiring=page_wiring)
