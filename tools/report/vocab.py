"""Vocabulary map: internal term -> surface phrase (contract:vocabulary-map).

Completeness is enforced at generation: translating an unknown term raises
GenerationError (an untranslated term is a generation-time error, never a
silent passthrough — pattern plain-surface-progressive-disclosure).
"""

from pathlib import Path

import yaml

DEFAULT_MAP = Path(__file__).parent / "vocabulary.yaml"


class GenerationError(Exception):
    pass


class Vocabulary:
    def __init__(self, path=None):
        data = yaml.safe_load(Path(path or DEFAULT_MAP).read_text(encoding="utf-8"))
        self.tokens = data["tokens"]
        self.status_roles = data["status_roles"]
        self.confidence_glyphs = data["confidence_glyphs"]

    def surface(self, term):
        """Translate an internal term for the surface layer. Unknown = error."""
        if term not in self.tokens:
            raise GenerationError(
                f"vocabulary map has no surface phrase for internal term '{term}' — "
                f"add it to the token table before it can appear on a surface"
            )
        return self.tokens[term]

    def status_glyph(self, status):
        role = self.status_roles.get(status)
        if role is None:
            raise GenerationError(f"vocabulary map has no status role for '{status}'")
        return role["glyph"]
