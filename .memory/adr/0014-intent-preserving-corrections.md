# 0014 — Intent-Preserving Corrections to Ratified Artifacts

**Status:** accepted (operator ruling 2026-07-27, option D of four weighed)
**Context:** The hard floor blocks any amendment "contradicting a ratified
resolution." Field evidence (discord-poc, 2026-07-23/24): a ratified
acceptance criterion — byte-identical output checksums for a dataset
generator — turned out physically unachievable (Iceberg metadata embeds
commit timestamps/UUIDs by spec). The fix preserved the ratified intent
(provable reproducibility) while changing only the mechanism (two-tier:
data-file byte hashes + order-independent logical row hash). It blocked a
build path ~24h purely on formality, and its presence in the escalation list
diluted attention from seven genuinely open judgments. A dollar/effort
threshold (option B) was rejected: stakes are agent-judged and dollars poorly
proxy architectural significance — the same field run produced a ~$10
amendment (F2 envelope) that also silently moved a measurement window, i.e.
an intent CHANGE hiding inside small stakes.

**Decision:** The ratified thing is the decision's INTENT, not the letter of
its text. An **intent-preserving achievability correction** — where the
ratified text is physically unachievable or factually wrong, and the fix
preserves the ratified intent — is not a contradiction of ratification and
may be agent-applied without blocking, with mandatory mechanics:

1. A one-line **intent statement** in the amendment note ("intent: X —
   preserved; mechanism changed from Y to Z because <evidence>").
2. `resolution_source` (or equivalent provenance field) cites this ADR plus
   the evidence for unachievability.
3. The correction is **listed in the span digest** presented to the human.

Everything else on the hard floor is unchanged and blocks unconditionally:
intent-changing amendments (envelopes, scope, sequencing, semantics),
irreversible actions, security-material-and-novel decisions, ★★ assignment
beyond what resolve ratified, demotion proposals.

**Test an agent must pass before applying:** (a) can you state the ratified
intent in one sentence without reference to the broken mechanism? (b) is the
unachievability a citable fact rather than an inconvenience? (c) would the
original ratifier recognize the fix as "what we meant"? Any doubt on any leg
→ escalate as before. A motivated stretch of "intent-preserving" is itself a
hard-floor violation.

**Why not the provisional-flag variant (D+C):** operator chose pure D;
unswept status flags rot, and the digest listing already provides the review
surface.
