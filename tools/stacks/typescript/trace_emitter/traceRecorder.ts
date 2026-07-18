/**
 * archwright TypeScript trace emitter (stack adapter, Extension Protocol / ADR 0008).
 *
 * Records state transitions during test execution and writes the JSON shape
 * consumed by `archwright-check.py --trace`:
 *
 *   [
 *     { "event": "INITIAL", "state": { "<var>": <value>, ... }, "clock": 0 },
 *     { "event": "JOIN",    "state": { ... },                   "clock": 1 },
 *     ...
 *   ]
 *
 * Shape notes (verified against check_trace, 2026-07-18):
 * - The trace is a BARE JSON ARRAY (not an envelope object).
 * - The first entry MUST be event "INITIAL" with the initial variable snapshot.
 * - `state` is the FULL context-variable snapshot after the event (guards are
 *   evaluated against the PREVIOUS entry's snapshot; invariants against this one).
 * - Variable names use the spec's snake_case `context.variables` keys.
 * - `tools/trace-schema.ts` documents a richer per-event shape (state/next_state);
 *   the validator does not consume it — this emitter targets the validator.
 *
 * Framework-agnostic: no vitest imports. Vitest usage:
 *
 *   const rec = createTraceRecorder({ current_players: 0, max_players: 3 });
 *   // ... in tests, after each domain action:
 *   rec.record("JOIN", { current_players: 1 });
 *   // ... afterAll:
 *   rec.write("design/traces/session-lifecycle.trace.json");
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

export interface TraceEntry {
  readonly event: string;
  readonly state: Record<string, unknown>;
  readonly clock: number;
}

export interface TraceRecorder {
  /** Record an event with the context vars that CHANGED (merged onto the running snapshot). */
  record(event: string, changed?: Record<string, unknown>): void;
  /** The entries recorded so far (INITIAL included). */
  entries(): readonly TraceEntry[];
  /** Serialize to the validator's JSON shape. */
  toJSON(): string;
  /** Write the trace file, creating parent directories. */
  write(path: string): void;
}

export function createTraceRecorder(
  initialVars: Record<string, unknown>,
): TraceRecorder {
  let snapshot: Record<string, unknown> = { ...initialVars };
  const trace: TraceEntry[] = [
    { event: "INITIAL", state: { ...snapshot }, clock: 0 },
  ];

  return {
    record(event, changed = {}) {
      snapshot = { ...snapshot, ...changed };
      trace.push({ event, state: { ...snapshot }, clock: trace.length });
    },
    entries() {
      return trace;
    },
    toJSON() {
      return JSON.stringify(trace, null, 2);
    },
    write(path) {
      mkdirSync(dirname(path), { recursive: true });
      writeFileSync(path, JSON.stringify(trace, null, 2) + "\n", "utf-8");
    },
  };
}
