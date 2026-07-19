# ADR 0002: Full Architecture Scope

**Status:** Accepted
**Date:** 2026-07-06

## Context

The original working doc positioned state machines as the compilation target. But real architecture decisions (from fieldball-coach: "no autoloads", "executor never resolves", "single writer for ball state") aren't state machines — they're constraints on code structure, dependency rules, and data contracts.

## Decision

Specs cover full architecture: behavior (statecharts), contracts (typed data shapes), constraints (global rules), dependencies (allowed/forbidden relationships), boundaries (service groupings), and protocols (communication patterns). The statechart is the central anchor but not the only artifact.

## Why

Architecture decisions ARE invariants — "PlayManager3D never calls PlayResolver" is a constraint just as checkable as "no dead-end states." Limiting to statecharts would leave the majority of real decisions unverifiable. The same provenance/confidence model applies regardless of spec kind.

## Consequences

- Spec schema has a `kind` field with multiple types (behavior, contract, constraint, dependency)
- Different checking mechanisms per kind (Alloy for behavior, grep/AST for constraints)
- The `check` field in constraint/dependency specs is self-describing (spec carries its own verification)
- Behavior specs are the most formally rigorous; other kinds are lighter but still checkable
