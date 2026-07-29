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


def _smcat_src(actor, transitions):
    """smcat source for one actor — retained for fixture suite compatibility.

    Transitions come from behavior specs via model_view (ticket 046); arrow
    labels are vocabulary surface phrases (D002 applies to arrows too)."""
    lines = []
    for st in actor["states"] if not isinstance(actor.get("states"), dict) else []:
        sid = st["id"] if isinstance(st, dict) else st
        label = (st.get("label") if isinstance(st, dict) else None) or sid
        lines.append('%s [label="%s"]' % (sid.replace("-", "_"), label))
    if isinstance(actor.get("states"), dict):
        for sname in actor["states"]:
            lines.append('%s [label="%s"]' % (sname.replace("-", "_"), sname))
    src = ",\n".join(lines) + ";"
    for tr in transitions:
        src += '\n%s => %s : %s;' % (
            tr["from"].replace("-", "_"), tr["to"].replace("-", "_"), tr["label"])
    return src


def _mermaid_src(actor, transitions, actor_id, state_rollups=None):
    """Mermaid stateDiagram-v2 source for one actor with click-to-detail links."""
    lines = ["stateDiagram-v2"]
    state_ids = []
    rollups = state_rollups or {}
    # Determine if any state has a non-zero rollup; if none do, all are "pending"
    any_rollup = any(sum(r.values()) > 0 for r in rollups.values()) if rollups else False
    states = actor.get("states") if isinstance(actor.get("states"), dict) else actor.get("states", [])
    if isinstance(states, dict):
        for sname, sdef in states.items():
            sid = sname.replace("-", "_")
            label = sname.replace("_", " ")
            # Append verification badge (ticket 063)
            r = rollups.get(sname, {})
            if r.get("fail"):
                label += " ✗"
            elif r.get("pass") and not r.get("pending"):
                label += " ✓"
            elif r.get("pending") or not any_rollup:
                label += " ○"
            lines.append("    %s: %s" % (sid, label))
            state_ids.append((sid, sname))
    else:
        for st in states:
            raw_id = st["id"] if isinstance(st, dict) else st
            sid = raw_id.replace("-", "_")
            label = (st.get("label") if isinstance(st, dict) else None) or raw_id.replace("_", " ")
            r = rollups.get(raw_id, {})
            if r.get("fail"):
                label += " ✗"
            elif r.get("pass") and not r.get("pending"):
                label += " ✓"
            elif r.get("pending") or not any_rollup:
                label += " ○"
            lines.append("    %s: %s" % (sid, label))
            state_ids.append((sid, raw_id))
    for tr in transitions:
        lines.append("    %s --> %s: %s" % (
            tr["from"].replace("-", "_"), tr["to"].replace("-", "_"), tr["label"]))
    # Click directives: link each state to its behavior-detail anchor (ticket 062)
    for sid, raw_id in state_ids:
        anchor = "detail-%s-%s" % (actor_id, raw_id.replace("_", "-"))
        lines.append('    click %s href "#%s"' % (sid, anchor))
    return "\n".join(lines)


def _diagram_section(model, model_view):
    """Generate diagram content: Mermaid source for client-side rendering.

    Primary path: emit <pre class="mermaid"> with stateDiagram-v2 source.
    Mermaid.js (inlined in template) renders it to SVG on page load.
    Fallback (JS disabled): the Mermaid source is readable as-is."""
    if model is None:
        return None, None
    actors = [a for a in model.get("actors") or [] if a.get("states")]
    if not actors:
        return None, None
    all_transitions = model_view.get("transitions") or []
    # Pick the actor with the most transitions (most informative front door).
    # Ties broken by state count, then actor order (ticket 076).
    actor_transition_counts = {}
    for t in all_transitions:
        actor_transition_counts[t["actor"]] = actor_transition_counts.get(t["actor"], 0) + 1
    actor = max(actors,
                key=lambda a: (actor_transition_counts.get(a["id"], 0),
                               len(a["states"]) if isinstance(a["states"], dict) else len(a.get("states", []))),
                default=actors[0]) if actors else actors[0]
    actor_id = actor["id"]
    transitions = [t for t in all_transitions if t["actor"] == actor_id]
    # Build per-state rollups for verification badges (ticket 063)
    state_rollups = {}
    for st in model_view.get("states") or []:
        if st["actor"] == actor_id:
            state_rollups[st["id"]] = st.get("rollup", {})
    mermaid_src = _mermaid_src(actor, transitions, actor_id, state_rollups)
    return mermaid_src, actor


def _behavior_detail_sections(model, model_view, vocab):
    """Generate behavior-detail drill-down sections (ticket 055, wf-behavior-detail).

    One anchor section per state: description, arrives-from/leads-to, rules with
    status badges, protected experiences, provenance fold. Uses in-page anchors
    (no routing framework — constraint:no-server-dependency)."""
    if model is None or not model_view.get("states"):
        return ""

    transitions = model_view.get("transitions") or []
    experiences_by_id = {e["id"]: e for e in model.get("experiences") or []}

    # Build state descriptions from raw model (dict-style states carry descriptions)
    descriptions = {}  # (actor_id, state_id) -> description
    for actor in model.get("actors") or []:
        states = actor.get("states")
        if isinstance(states, dict):
            for sname, sdef in states.items():
                if isinstance(sdef, dict) and sdef.get("description"):
                    descriptions[(actor["id"], sname)] = sdef["description"]

    sections = []
    seen_actors = set()
    for st in model_view["states"]:
        actor_id = st["actor"]
        state_id = st["id"]
        anchor = "detail-%s-%s" % (actor_id, state_id.replace("_", "-"))

        # Arrives from / leads to
        arrives = [t for t in transitions if t["to"] == state_id and t["actor"] == actor_id]
        leads = [t for t in transitions if t["from"] == state_id and t["actor"] == actor_id]

        # Description
        desc = descriptions.get((actor_id, state_id)) or descriptions.get((actor_id, state_id.replace("-", "_")))

        # Actor header (once per actor)
        if actor_id not in seen_actors:
            seen_actors.add(actor_id)
            actor_obj = next((a for a in model.get("actors") or [] if a["id"] == actor_id), None)
            actor_desc = actor_obj.get("description", "") if actor_obj else ""
            if actor_desc:
                sections.append('<h3 class="meta">%s</h3>' % _esc(actor_desc))

        # Build section
        parts = []
        parts.append('<div class="card behavior-detail" id="%s">' % _esc(anchor))
        parts.append('<p><a href="#diagram-top">&larr; back to the diagram</a></p>')

        # State name + rollup badge
        rollup = st.get("rollup", {})
        if rollup.get("fail"):
            badge_class = "status-fail"
            badge_text = vocab.status_glyph("fail") + " needs attention"
        elif rollup.get("pass") and not rollup.get("pending"):
            badge_class = "status-pass"
            badge_text = vocab.status_glyph("pass") + " verified"
        else:
            badge_class = "status-pending"
            badge_text = vocab.status_glyph("pending") + " pending"
        parts.append('<p><strong>%s</strong> <span class="glyph %s">%s</span></p>'
                     % (_esc(st["label"]), badge_class, badge_text))

        # What happens here
        if desc or arrives or leads:
            parts.append("<h4>WHAT HAPPENS HERE</h4>")
            if desc:
                parts.append("<p>%s</p>" % _esc(desc))
            if arrives:
                from_labels = ", ".join("%s (%s)" % (_esc(t["from"]), _esc(t["label"])) for t in arrives)
                parts.append('<p class="meta">arrives from: %s</p>' % from_labels)
            if leads:
                to_labels = ", ".join("%s (%s)" % (_esc(t["to"]), _esc(t["label"])) for t in leads)
                parts.append('<p class="meta">leads to: %s</p>' % to_labels)

        # Rules that apply (from model_view join or model invariants)
        rules = st.get("rules") or []
        # Also gather invariants from the raw model for this actor
        actor_obj = next((a for a in model.get("actors") or [] if a["id"] == actor_id), None)
        invariants = (actor_obj.get("invariants") or []) if actor_obj else []
        if rules or invariants:
            parts.append("<h4>THE RULES THAT APPLY HERE</h4>")
            for r in rules:
                status = r.get("status", "pending")
                glyph = vocab.status_glyph(status) if status in ("pass", "fail", "warn", "skip", "pending") else "?"
                glyph_class = "status-%s" % status if status in ("pass", "fail", "warn", "skip", "pending") else ""
                statement = r.get("statement") or r.get("spec", "")
                parts.append('<p><span class="glyph %s">%s</span>%s</p>'
                             % (glyph_class, glyph, _esc(statement)))
            if not rules and invariants:
                for inv in invariants:
                    desc_text = inv.get("description") or inv.get("id", "")
                    parts.append('<p><span class="glyph status-pending">%s</span>%s</p>'
                                 % (vocab.status_glyph("pending"), _esc(desc_text)))

        # What this protects
        protects = st.get("protects") or []
        if protects:
            exp_texts = []
            for eid in protects:
                exp = experiences_by_id.get(eid)
                if exp:
                    exp_texts.append(exp.get("what_user_sees") or eid)
                else:
                    exp_texts.append(eid)
            if exp_texts:
                parts.append("<h4>WHAT THIS PROTECTS</h4>")
                parts.append("<p>%s</p>" % " &middot; ".join(_esc(t) for t in exp_texts))

        # How we arrived at this (folded provenance)
        prov_lines = []
        for r in rules:
            spec_ref = r.get("spec", "")
            if spec_ref:
                prov_lines.append(spec_ref)
        # Include force/experience links as provenance when available
        for eid in protects:
            exp = experiences_by_id.get(eid)
            if exp:
                for prot in exp.get("protected_by") or []:
                    prov_lines.append("%s — %s" % (prot.get("spec", ""), prot.get("how", "")))
                if exp.get("desire"):
                    prov_lines.append("desire: %s" % exp["desire"])
        if prov_lines:
            parts.append('<details class="detail-fold"><summary>HOW WE ARRIVED AT THIS</summary>')
            parts.append('<div class="disclosure-body"><p class="meta">Provenance chain:</p><ul>')
            for line in prov_lines:
                parts.append("<li><code>%s</code></li>" % _esc(line))
            parts.append("</ul></div></details>")

        parts.append("</div>")
        sections.append("\n".join(parts))

    if not sections:
        return ""
    return '<div id="behavior-details">' + "\n".join(sections) + "</div>"


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

    svg = _diagram_section(model, model_view)
    diagram_section = ""
    if svg:
        mermaid_src, diagram_actor = svg
        if mermaid_src:
            badge = ("every step verified " + vocab.status_glyph("pass")) if post == "all-clear" \
                else "steps needing attention are marked " + vocab.status_glyph("fail")
            # Mermaid source needs < and & escaped but NOT > (arrows use -->)
            safe_src = mermaid_src.replace("&", "&amp;").replace("<", "&lt;")
            diagram_section = ('<div id="diagram-top"><h2>HOW %s WORKS</h2>'
                               '<div class="diagram"><pre class="mermaid">\n%s\n</pre></div>'
                               '<p class="meta">%s · click any step for details</p></div>'
                               % (_esc(bundle["project"].upper()), safe_src, _esc(badge)))
        else:
            diagram_section = '<div id="diagram-top"><p class="meta">%s</p></div>' % _esc(model_view.get("note", ""))
    elif model_view.get("note"):
        diagram_section = '<div id="diagram-top"><p class="meta">%s</p></div>' % _esc(model_view["note"])

    behavior_detail_section = _behavior_detail_sections(model, model_view, vocab)

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
    mermaid_vendor = Path(__file__).parent / "vendor" / "mermaid.min.js"
    mermaid_js_content = mermaid_vendor.read_text(encoding="utf-8") if mermaid_vendor.exists() else ""
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

    result = _tpl("report.html").substitute(
        project=_esc(bundle["project"]), checked_at=_esc(bundle["generated_at"]),
        run_label=_esc((run.get("commit") or "no-git")[:7] + (" · uncommitted changes present" if run.get("dirty") else "")),
        verdict_line=verdict, asks_section=asks_section, diagram_section=diagram_section,
        behavior_detail_section=behavior_detail_section,
        unverified_section=unverified_section, stability_section=stability_section,
        mermaid_js="/* __MERMAID_PLACEHOLDER__ */", page_js=page_js, page_wiring=page_wiring)
    # Insert mermaid.js AFTER template substitution to avoid $ escaping conflicts
    # (mermaid.min.js has ~10K $ signs in template literals that break string.Template)
    return result.replace("/* __MERMAID_PLACEHOLDER__ */", mermaid_js_content)
