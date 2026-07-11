/**
 * archwright-trace: Minimal trace event schema for behavior spec validation.
 * 
 * Traces record state transitions observed during test execution.
 * A validator walks the trace against a behavior spec's FSM and reports
 * any event that violates the spec's declared transitions or invariants.
 * 
 * Design principles:
 * - Minimal: only state + event + context updates (TLA+ paper finding)
 * - Language-agnostic: JSON format, any test framework can emit
 * - Partial: not every spec variable needs a value in every event
 */

export interface TraceEvent {
  /** Current state BEFORE this event */
  readonly state: string;
  /** Event that occurred */
  readonly event: string;
  /** State AFTER this event (the transition target) */
  readonly next_state: string;
  /** Context variable updates (only changed values, not full snapshot) */
  readonly context?: Record<string, unknown>;
  /** Timestamp (optional, for ordering verification) */
  readonly ts?: number;
}

export interface Trace {
  /** Which behavior spec this trace validates against */
  readonly spec_id: string;
  /** The initial state declared by the spec */
  readonly initial_state: string;
  /** Ordered sequence of observed events */
  readonly events: readonly TraceEvent[];
  /** Test/scenario that produced this trace */
  readonly source?: string;
}

export interface TraceViolation {
  /** Index in the events array where the violation occurred */
  readonly event_index: number;
  /** The event that violated the spec */
  readonly event: TraceEvent;
  /** What the spec says should be possible from this state */
  readonly allowed_events: string[];
  /** Type of violation */
  readonly kind: "invalid_transition" | "invalid_target" | "invariant_violated" | "unknown_state";
  /** Human-readable explanation */
  readonly message: string;
}

export interface TraceValidationResult {
  readonly spec_id: string;
  readonly status: "pass" | "fail";
  readonly violations: readonly TraceViolation[];
  readonly events_checked: number;
  readonly trace_source?: string;
}
