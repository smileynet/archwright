"""archwright_common: shared spec-parsing helpers for the archwright tools.

Any tool reading behavior specs MUST use these instead of raw dict access —
PyYAML (YAML 1.1) parses the key `on:` as boolean True, which made
archwright-compile-alloy generate transition-less (vacuously-checkable)
models for months while the trace validator carried the workaround inline.
One parser, one workaround (lessons.md 2026-07-17).
"""


def state_events(state_def):
    """Return the event→transition mapping of a behavior-spec state.

    Handles both spellings: `"on":` (quoted, YAML 1.2-safe) and bare `on:`
    (parsed by PyYAML as the boolean True).
    """
    return state_def.get("on") or state_def.get(True) or {}
