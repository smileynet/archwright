"""Vocabulary map: internal term -> surface phrase (contract:vocabulary-map).

Completeness is enforced at generation: translating an unknown term raises
GenerationError (an untranslated term is a generation-time error, never a
silent passthrough — pattern plain-surface-progressive-disclosure).

Override semantics: a target project may provide design/vocabulary.yaml with
additional tokens (typically "event <NAME>" entries for domain events). These
merge INTO the base map — project tokens win on conflict. Non-event terms
without a mapping still raise GenerationError (structural vocabulary is
non-negotiable); event terms without a mapping fall through to humanization
and are collected as warnings.
"""

from pathlib import Path

import yaml

DEFAULT_MAP = Path(__file__).parent / "vocabulary.yaml"


class GenerationError(Exception):
    pass


class Vocabulary:
    def __init__(self, path=None, override=None):
        """Load vocabulary. Base is always the default map (or explicit path).
        Override merges additional tokens on top of base."""
        base_path = path or DEFAULT_MAP
        data = yaml.safe_load(Path(base_path).read_text(encoding="utf-8"))
        self.tokens = data["tokens"]
        self.status_roles = data["status_roles"]
        self.confidence_glyphs = data["confidence_glyphs"]
        self._missing_events = []

        if override:
            override_path = Path(override)
            if override_path.exists():
                override_data = yaml.safe_load(override_path.read_text(encoding="utf-8"))
                if isinstance(override_data, dict) and isinstance(override_data.get("tokens"), dict):
                    self.tokens.update(override_data["tokens"])

    def surface(self, term):
        """Translate an internal term for the surface layer.

        Unknown event terms (prefixed 'event ') fall through to humanization
        and are collected as warnings. All other unknown terms raise."""
        if term in self.tokens:
            return self.tokens[term]
        if term.startswith("event "):
            # Humanize: strip prefix, underscores to spaces, title case
            raw = term[len("event "):]
            humanized = raw.replace("_", " ").lower()
            self._missing_events.append(term)
            return humanized
        raise GenerationError(
            f"vocabulary map has no surface phrase for internal term '{term}' — "
            f"add it to the token table before it can appear on a surface"
        )

    @property
    def missing_events(self):
        """Event terms that fell back to humanization (no override provided)."""
        return sorted(set(self._missing_events))

    def status_glyph(self, status):
        role = self.status_roles.get(status)
        if role is None:
            raise GenerationError(f"vocabulary map has no status role for '{status}'")
        return role["glyph"]
