# Growth Rules

When artifacts change, other artifacts MUST update in the same commit. These rules prevent silent drift between patterns, specs, and code.

Inspired by the Spec Growth Engine (Grabowski, 2026) — adapted for archwright's force-resolution model.

## The Rules

| # | Fires when | Required co-updates |
|---|-----------|-------------------|
| 1. **Force change** | A pattern gains/loses/modifies a force | Update tension statement. Check if resolution still holds. If not → re-resolve (may cascade to specs). |
| 2. **Resolution change** | A pattern's resolution is revised | Update `resolves_into` links. Update or create affected specs. Run archwright-check on affected specs. |
| 3. **Spec contract change** | A spec's externally-visible surface changes (new states, events, invariants) | Find all specs that link TO this spec. Verify their assumptions still hold. Flag consumers for re-check. |
| 4. **Spec internal change** | A spec's design changes but contract stays same | No cascade required. Update only the spec's internal fields. Do NOT touch consuming specs. |
| 5. **New dependency** | A spec starts depending on another spec | Add `links` entry. Verify target spec has a contract. Reference only the contract, never internals. |
| 6. **Implementation change** | Code changes that affect a spec's domain | Run `archwright-check` on affected specs. If violation found → update spec (same commit) or fix code. Spec and code must never diverge. |
| 7. **Confidence promotion** | Evidence accumulated, requesting ★ → ★★ | Run deeper checking (larger scope/steps, or Lean proof attempt). Record evidence in pattern. Update confidence field if promoted. |

## The Invariant

**Spec and code are always aligned, or the commit does not land.**

This is not a discipline request — it's enforceable via `archwright-check` as a merge gate (CI integration).

## Cascade Depth

- Rule 1 (force change) can cascade: force → pattern → specs → consumers. Maximum depth = 3 hops.
- Rule 3 (contract change) cascades to direct consumers only (one hop).
- Rule 4 (internal change) does NOT cascade. This is why the contract/design split matters.
- Rule 6 (implementation change) cascades upward: code → spec → pattern (if resolution invalidated).

## Applying the Rules

When the agent makes any change, it classifies the change against this table and performs ALL required co-updates before presenting the work as complete. If a co-update triggers another rule (cascade), follow the chain.

The verification protocol (`archwright-check`) catches violations of these rules — but the rules exist so the agent doesn't NEED the check to catch them. Fix before commit, not after.
