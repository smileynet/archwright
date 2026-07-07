# ADR 0003: "Resolves Into" Not "Compiles To"

**Status:** Accepted
**Date:** 2026-07-06

## Context

The original framing used "compiles" throughout — "a design language that compiles to architecture." But compilation implies a deterministic, mechanical, lossless transformation. Archwright's process is creative (finding resolutions), collaborative (human + agent), and one-to-many (forces don't have a single correct architecture).

## Decision

Use "resolves into" as the primary verb. Design intent resolves into verified architecture. The process is creative resolution followed by formal verification — not mechanical transformation.

Tagline: "A force-resolution design language that resolves into verified architecture."

## Why

"Compile" sets wrong expectations — it implies you can push a button and get architecture out, like `gcc main.c`. In reality, the resolution step requires human judgment (choosing among alternatives) and the verification step proves the result satisfies the stated forces. "Resolves" captures both the creative act and the existence of the resolution as an artifact.

"Compile" is still appropriate for the mechanical sub-steps (spec → Alloy model generation is genuinely compilation). But the overall process is resolution.

## Consequences

- All documentation uses "resolves into" for the overall process
- "Hands-down" (downward direction) and "pass-up" (upward) remain unchanged
- "Compile" is reserved for mechanical sub-steps only (spec → Alloy, spec → XState)
- "Re-resolve" replaces "recompile" for the correction step
