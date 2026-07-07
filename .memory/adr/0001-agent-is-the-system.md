# ADR 0001: The Agent IS the System

**Status:** Accepted
**Date:** 2026-07-06

## Context

Archwright could be delivered as a CLI binary, a library, an IDE plugin, or a methodology. The choice affects everything: language, packaging, user interaction model, and what "using archwright" means.

## Decision

Archwright is a methodology embodied as agent skills. The AI agent IS the system — it holds the design methodology (force identification, resolution, verification, correction routing). Tools are mechanical servants for deterministic operations only (schema validation, Alloy execution, grep-based conformance checks).

## Why

The intelligence in archwright is the methodology — knowing when to surface tensions, how to decompose experience desires into checkable proxies, how to re-express a violation in the parent's vocabulary. None of this is deterministic. A binary can't hold it. Only a skill-equipped agent can.

Tools handle only what's mechanical: "is this YAML valid?", "does this model have a counterexample?", "does this grep match?" These are deterministic and benefit from dedicated scripts. Everything else is the agent applying judgment.

## Consequences

- No monolithic binary to build or maintain
- Skills are the primary deliverable (methodology as instructions)
- Tools are small, purpose-built scripts on PATH
- The "interface" is conversation + file artifacts, not a GUI
- New users adopt archwright by loading the skills, not installing software
