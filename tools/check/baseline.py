"""Baseline suppression (CK-07) — load and discovery."""

import json
from pathlib import Path

from check.common import FINGERPRINT_ALGO, _find_up


BASELINE_FILENAME = ".archwright-baseline.json"


def find_baseline(start_dirs, explicit=None):
    """Locate .archwright-baseline.json: explicit flag wins; otherwise walk up
    from each start dir. Returns a Path or None. No baseline = no suppression
    (never silently create one — baseline entries are a human decision)."""
    if explicit:
        return Path(explicit)
    return _find_up(start_dirs, BASELINE_FILENAME)


def load_baseline(path):
    """Parse the baseline file. Returns (data, matchable-fingerprint-set).
    Entries with an unknown algo are retained in data but excluded from
    matching (stale, never guessed). Raises ValueError on malformed JSON."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"cannot read baseline {path}: {e}")
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError(f"baseline {path}: 'entries' must be a list")
    fps = {e["fingerprint"] for e in entries
           if isinstance(e, dict) and "fingerprint" in e
           and e.get("algo", FINGERPRINT_ALGO) == FINGERPRINT_ALGO}
    return data, fps
