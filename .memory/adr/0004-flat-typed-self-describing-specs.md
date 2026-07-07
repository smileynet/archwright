# ADR 0004: Flat Typed Specs with Self-Describing Checks

**Status:** Accepted
**Date:** 2026-07-06

## Context

Spec files could be organized as: (A) monolithic per-subsystem, (B) directories per subsystem, or (C) flat files with a typed `kind` field and explicit links. Additionally, the checking mechanism could be centralized (one checker knows all rules) or self-describing (each spec carries its own check).

## Decision

Specs are flat, typed, and self-describing. Each spec file has a `kind` field, an `id`, explicit `links` via `kind:id` references, and (for constraint/dependency kinds) a `check` field that describes how to verify it. Tools scan `design/specs/` recursively and don't care about directory structure.

## Why

- **Flat + typed** matches Kubernetes/Terraform patterns (proven at scale)
- **Independent checkability** — each file validates alone, clean git diffs
- **Self-describing checks** — the spec carries its own verification recipe, so adding a new constraint doesn't require modifying a central checker
- **Filesystem-independent links** — `kind:id` refs are greppable and validatable without path conventions
- **User-organized** — directories are optional grouping, not load-bearing structure

## Consequences

- Tools process files by `kind` (dispatch to appropriate checker)
- Link validation is a separate pass (verify all targets exist)
- New spec kinds can be added without changing existing tooling (just add a schema + checker)
- Constraint/dependency specs in markdown+frontmatter (human-readable body + machine-readable check)
- Behavior/contract specs in pure YAML (machine-primary)
