"""Derive the model_view and asks blocks from the canonical check document
plus the design model YAML (contracts: model-view-block, asks-block).

Read-only projection: consumes ONLY the CK-03 document and design/ YAML files
(dependency rule report-reads-canonical-only — never checker internals).
"""

import hashlib
from pathlib import Path

import yaml

from vocab import GenerationError

ASK_DECISION, ASK_APPROVAL, ASK_SUGGESTION = "decision", "approval", "suggestion"


def _bool_key(d, key):
    # YAML 1.1: unquoted `on:` parses as True (shared-helper rule).
    return d.get(key) if key in d else d.get(True) or {}


def load_model(models_dir):
    """Load the first actor-model YAML found; None when no model exists."""
    models_dir = Path(models_dir)
    if not models_dir.is_dir():
        return None
    for path in sorted(models_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "actors" in data:
            data["_path"] = str(path)
            return data
    return None


def _actor_for_projection(model, proj):
    source = proj.get("from", "")
    for a in model.get("actors") or []:
        if a["id"] in source or a["id"] in str(proj.get("pattern", "")):
            return a["id"]
    return None


def _spec_join(model, doc):
    """Join spec results to actors via the model's spec_projections."""
    by_spec = {}
    for v in doc.get("violations") or []:
        by_spec.setdefault(v["spec_id"], []).append(("fail", v))
    for s in doc.get("skips") or []:
        status = "pending" if "pending" in (s.get("reason") or "") else "skip"
        by_spec.setdefault(s.get("spec_id"), []).append((status, s))
    joined = {}  # actor_id -> [(spec_ref, status, item)]
    for proj in model.get("spec_projections") or []:
        spec_ref = proj["spec"]
        spec_id = spec_ref.split(":", 1)[1]
        actor = _actor_for_projection(model, proj)
        results = by_spec.get(spec_id)
        if results:
            for status, item in results:
                joined.setdefault(actor, []).append((spec_ref, status, item))
        else:
            joined.setdefault(actor, []).append((spec_ref, "pass", None))
    return joined


def _behavior_transitions(model, vocab):
    """Join transitions from behavior specs into the model view (ticket 046).

    Behavior specs (design/specs/<id>.yaml, kind: behavior) carry the statechart;
    the model's spec_projections link them to actors. Returns
    [{from, to, event, label, actor, spec}] with state ids normalized to the
    model's hyphenated form. Reads spec YAML as a design/ file input — never
    checker internals (dependency:report-reads-canonical-only).
    """
    specs_dir = Path(model["_path"]).parent.parent / "specs" if model.get("_path") else None
    if specs_dir is None or not specs_dir.is_dir():
        return []
    state_ids = {}  # actor_id -> {normalized: model_form}
    for a in model.get("actors") or []:
        state_ids[a["id"]] = {
            (st["id"] if isinstance(st, dict) else st).replace("_", "-"):
            (st["id"] if isinstance(st, dict) else st)
            for st in a.get("states") or []}

    transitions = []
    for proj in model.get("spec_projections") or []:
        spec_ref = proj["spec"]
        if not spec_ref.startswith("behavior:"):
            continue
        actor = _actor_for_projection(model, proj)
        if actor is None:
            continue
        spec_path = specs_dir / (spec_ref.split(":", 1)[1] + ".yaml")
        if not spec_path.exists():
            continue
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if not isinstance(spec, dict) or spec.get("kind") != "behavior":
            continue
        ids = state_ids.get(actor, {})
        model_form = lambda s: ids.get(str(s).replace("_", "-"), str(s))
        for state_name, state_def in (spec.get("states") or {}).items():
            if not isinstance(state_def, dict):
                continue
            for event, tr in (_bool_key(state_def, "on") or {}).items():
                target = tr.get("target") if isinstance(tr, dict) else tr
                if not target:
                    continue
                transitions.append({
                    "from": model_form(state_name), "to": model_form(target),
                    "event": str(event),
                    "label": vocab.surface("event " + str(event)),
                    "actor": actor, "spec": spec_ref,
                })
    return transitions


def build_model_view(model, doc, vocab):
    """model_view block: elements with plain labels + per-element rollups.

    v1 join granularity: specs join at ACTOR level — every state/transition of
    an actor inherits its actor's rule rollup (per-element spec joins need
    invariant->state mapping, deferred; noted in the block)."""
    if model is None:
        return {"front_door": "promise-grouped-list", "states": [], "transitions": [],
                "source_model": None,
                "note": "no behavior map available for this project yet"}

    actors = [a for a in (model.get("actors") or []) if a.get("states")]
    front_door = "behavior-diagram" if len(actors) == 1 else "composition-view"
    joined = _spec_join(model, doc)
    transitions = _behavior_transitions(model, vocab)

    states = []
    for actor in actors:
        rules = []
        rollup = {"pass": 0, "fail": 0, "warn": 0, "skip": 0, "pending": 0}
        for spec_ref, status, item in joined.get(actor["id"], []):
            surface = None
            if status == "fail" and item is not None:
                surface = (item.get("contrast_pair") or {}).get("expected") or item.get("message")
            rules.append({"spec": spec_ref, "status": status, "statement": surface})
            rollup[status if status in rollup else "warn"] += 1
        for st in actor["states"]:
            states.append({
                "id": st["id"] if isinstance(st, dict) else st,
                "actor": actor["id"],
                "label": (st.get("label") if isinstance(st, dict) else None) or str(st),
                "rollup": rollup,
                "rules": rules,
                "protects": [e["id"] for e in model.get("experiences") or []],
            })
    return {"front_door": front_door, "states": states, "transitions": transitions,
            "source_model": model.get("_path"),
            "note": "rules are grouped by the part of the app they check"}


def _ask_id(source_kind, key):
    if source_kind == "violation":
        return key  # aw/v1 fingerprint reused verbatim (contract:asks-block)
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{source_kind}:{digest}"


def build_asks(doc, vocab, auto_approve="off"):
    """asks block per contract:asks-block. Classification (wf-overview table):
    escalate=true violation -> decision; other violations -> approval
    (recommendation: suggested_route); persistent skips (not pending) ->
    suggestion; baselined violations are disclosure content, not asks."""
    asks = []
    for v in doc.get("violations") or []:
        if v.get("baselined"):
            continue
        fp = (v.get("fingerprints") or [f"{v['spec_id']}:{v['invariant']}"])[0]
        ask_type = ASK_DECISION if v.get("escalate") else ASK_APPROVAL
        route = v.get("suggested_route", "fix-implementation")
        auto = (ask_type == ASK_APPROVAL and (
            auto_approve == "all" or
            (auto_approve == "code-fixes" and route == "fix-implementation")))
        asks.append({
            "ask_id": _ask_id("violation", fp),
            "ask_type": ask_type,
            "title": v.get("message", ""),
            "contrast_pair": v.get("contrast_pair"),
            "options": ([{"id": "keep-rule", "label": "Keep the rule — " + vocab.surface(route), "recommended": True},
                         {"id": "amend-rule", "label": "Amend the rule", "recommended": False},
                         {"id": "accept-debt", "label": "Accept as a known issue for now", "recommended": False}]
                        if ask_type == ASK_DECISION else None),
            "recommendation": {"action": vocab.surface(route),
                               "rationale": f"{vocab.surface('confidence ' + v['confidence'])}; contrast pair localizes the fault"},
            "confidence_phrase": vocab.surface("confidence " + v["confidence"]),
            "source": {"kind": "violation", "ref": v["spec_id"]},
            "auto_approved": bool(auto),
            "diagram_ref": None,  # filled by pin pass below
        })
    for s in doc.get("skips") or []:
        if "pending" in (s.get("reason") or ""):
            continue  # pending = disclosure content ("check not built yet")
        asks.append({
            "ask_id": _ask_id("skip", f"{s.get('spec_id')}"),
            "ask_type": ASK_SUGGESTION,
            "title": f"{s.get('spec_id')}: {vocab.surface('skip')} — {s.get('reason', '')}",
            "contrast_pair": None, "options": None,
            "recommendation": {"action": "build the checker or accept the gap",
                               "rationale": s.get("reason", "")},
            "confidence_phrase": vocab.surface("confidence —"),
            "source": {"kind": "persistent-skip", "ref": s.get("spec_id")},
            "auto_approved": False, "diagram_ref": None,
        })
    counts = {t: sum(1 for a in asks if a["ask_type"] == t)
              for t in (ASK_DECISION, ASK_APPROVAL, ASK_SUGGESTION)}
    counts["auto_approved"] = sum(1 for a in asks if a["auto_approved"])
    return {"counts": counts, "auto_approve": auto_approve, "asks": asks}


def pin_violations(asks_block, model_view, model):
    """constraint:violations-pin-to-diagram — violation asks get a diagram_ref
    when a diagram front door exists (v1: the violated spec's actor's first state)."""
    if model_view["front_door"] == "promise-grouped-list" or model is None:
        return
    spec_actor = {}
    for proj in model.get("spec_projections") or []:
        spec_actor[proj["spec"].split(":", 1)[1]] = proj.get("from", "")
    actor_first_state = {}
    for el in model_view["states"]:
        actor_first_state.setdefault(el["actor"], el["id"])
    for ask in asks_block["asks"]:
        if ask["source"]["kind"] != "violation":
            continue
        source = spec_actor.get(ask["source"]["ref"], "")
        for actor_id, state_id in actor_first_state.items():
            if actor_id and actor_id in source:
                ask["diagram_ref"] = state_id
                break
        if ask["diagram_ref"] is None and actor_first_state:
            ask["diagram_ref"] = next(iter(actor_first_state.values()))


def posture(doc, asks_block):
    if doc.get("status") == "error":
        return "tool-error"
    if (doc.get("scope") or {}).get("specs_checked", 0) == 0:
        return "empty-project"
    blocking = [a for a in asks_block["asks"]
                if a["ask_type"] in (ASK_DECISION, ASK_APPROVAL) and not a["auto_approved"]]
    return "needs-attention" if blocking else "all-clear"
