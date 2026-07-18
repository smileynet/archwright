/**
 * archwright-trace: Trace shape for behavior spec validation.
 *
 * CONSUMER-AUTHORITATIVE: this file documents exactly what
 * `archwright-check.py --trace <spec.yaml> <trace.json>` consumes
 * (function `check_trace`, verified 2026-07-18). If the validator and this
 * file ever disagree, the validator wins — fix this file.
 *
 * A trace is a BARE JSON ARRAY of entries (no envelope object):
 *
 *   [
 *     { "event": "INITIAL", "state": { "current_players": 0, "max_players": 3 }, "clock": 0 },
 *     { "event": "JOIN",    "state": { "current_players": 1, "max_players": 3 }, "clock": 1 },
 *     ...
 *   ]
 *
 * Protocol:
 * - The FIRST entry must have event "INITIAL" with the initial variable snapshot.
 * - `state` is the FULL context-variable snapshot AFTER the event (not a delta).
 *   Guards are evaluated against the PREVIOUS entry's snapshot; invariants
 *   against the current one. Variable names use the spec's snake_case
 *   `context.variables` keys. Include any extra variables that the spec's
 *   invariant predicates reference (e.g. a `status` string), even if they are
 *   not declared in `context.variables`.
 * - `clock` is a monotonically increasing ordinal (the emitter uses the entry
 *   index). The validator reads it for violation reporting, defaulting to the
 *   array index when absent.
 * - Events not observed are simply not recorded: an operation the system
 *   REJECTED (guard held) must NOT appear in the trace.
 *
 * Design principles:
 * - Minimal: full-snapshot entries, no transition metadata (TLA+ paper finding)
 * - Language-agnostic: JSON format, any test framework can emit
 * - Reference emitter: tools/stacks/typescript/trace_emitter/traceRecorder.ts
 *
 * History: an earlier revision of this file described an envelope shape
 * ({ spec_id, initial_state, events: [{ state, event, next_state, context }] })
 * that the validator never consumed. Removed 2026-07-18 after the shape drift
 * was caught while building the TypeScript trace emitter.
 *
 * OUTPUT MODES (ticket 016): the shapes below (TraceValidationResult) are the
 * DEFAULT stdout output. With `--json`, the validator instead emits the CK-03
 * document (tools/check-output-schema.yaml, scope.mode "trace") so
 * archwright-passup routes trace violations uniformly with static ones:
 * the violation becomes a violations[] entry (confidence from the violated
 * invariant, severity derived, escalate on ★★, contrast_pair, provenance);
 * invariants_skipped/guards_skipped map into skips[]; coverage counts
 * invariants. Exit codes are identical in both modes (0 pass / 1 fail /
 * 2 error). Use the default shape for replay detail, --json for routing.
 */

/** One observed transition. */
export interface TraceEntry {
  /** Event name, matching the spec's transition events. First entry: "INITIAL". */
  readonly event: string;
  /** FULL context-variable snapshot after this event. */
  readonly state: Record<string, unknown>;
  /** Monotonic ordinal for ordering/reporting (defaults to array index). */
  readonly clock?: number;
}

/** The trace file content: a bare array. */
export type Trace = readonly TraceEntry[];

/**
 * Violation payload emitted by the validator on FAIL in DEFAULT mode (single
 * JSON object on stdout with status "fail"; with --json the CK-03 document is
 * emitted instead). Field presence varies by violation type.
 */
export interface TraceViolation {
  /** "protocol" | "transition" | "guard" — invariant violations carry `invariant` instead. */
  readonly type?: "protocol" | "transition" | "guard";
  /** Violated invariant id (invariant violations). */
  readonly invariant?: string;
  /** Index in the trace array where the violation occurred. */
  readonly position: number;
  readonly clock: number;
  readonly event?: string;
  readonly state?: Record<string, unknown>;
  readonly prev_state?: Record<string, unknown>;
  readonly current_spec_state?: string;
  readonly valid_events?: string[];
  readonly expected?: string;
  readonly message: string;
}

export interface TraceValidationResult {
  readonly status: "pass" | "fail" | "error";
  readonly assurance: "trace";
  readonly spec_id?: string;
  readonly violation?: TraceViolation;
  readonly provenance?: { readonly from_force?: string; readonly from_pattern?: string };
  readonly steps_checked?: number;
  readonly final_state?: string;
  /** Invariants fully evaluated at every step (excludes skipped ones). */
  readonly invariants_checked?: string[];
  /**
   * Invariants NOT evaluated because their predicate is untranslatable
   * (ticket 015 — SKIP-with-reason, never silent-pass). Always present on
   * pass results AND fail results (a failing trace must not hide coverage
   * gaps accumulated before the failure point); empty when everything
   * translated. A pass with skips still exits 0, but the skipped list is a
   * coverage statement, not a pass.
   */
  readonly invariants_skipped?: ReadonlyArray<{ readonly id: string; readonly reason: string }>;
  /**
   * Guards that were untranslatable: the transition was accepted with a note
   * rather than silently treated as guard-satisfied. Present only when
   * non-empty.
   */
  readonly guards_skipped?: ReadonlyArray<{
    readonly position: number;
    readonly event: string;
    readonly predicate: string;
    readonly reason: string;
  }>;
  readonly message?: string;
}
