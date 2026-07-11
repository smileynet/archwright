#!/usr/bin/env node
/**
 * archwright-trace-validate: Validate a JSON trace against a behavior spec.
 *
 * Usage:
 *   archwright-trace-validate <spec.yaml> <trace.json>
 *   cat trace.json | archwright-trace-validate <spec.yaml> -
 *
 * Reads the behavior spec's states and transitions, then walks the trace
 * event-by-event checking that each transition is allowed by the spec.
 *
 * Exit codes: 0 = pass, 1 = violations found, 2 = usage error
 */

import { readFileSync } from "node:fs";
import { parse as parseYaml } from "yaml";

// --- Types (inline to avoid build step) ---

interface TraceEvent {
  state: string;
  event: string;
  next_state: string;
  context?: Record<string, unknown>;
}

interface Trace {
  spec_id: string;
  initial_state: string;
  events: TraceEvent[];
  source?: string;
}

interface TraceViolation {
  event_index: number;
  event: TraceEvent;
  allowed_events: string[];
  kind: string;
  message: string;
}

interface SpecTransition {
  target: string;
  guard?: { predicate: string };
}

interface SpecState {
  type?: string;
  on?: Record<string, SpecTransition | SpecTransition[]>;
}

interface BehaviorSpec {
  kind: string;
  id: string;
  initial: string;
  states: Record<string, SpecState>;
  invariants?: Array<{ id: string; predicate: string }>;
}

// --- Validator ---

function validate(spec: BehaviorSpec, trace: Trace): TraceViolation[] {
  const violations: TraceViolation[] = [];

  // Check initial state matches
  if (trace.initial_state !== spec.initial) {
    violations.push({
      event_index: -1,
      event: { state: trace.initial_state, event: "(initial)", next_state: trace.initial_state },
      allowed_events: [],
      kind: "unknown_state",
      message: `Trace declares initial_state '${trace.initial_state}' but spec declares '${spec.initial}'`
    });
  }

  for (let i = 0; i < trace.events.length; i++) {
    const ev = trace.events[i];

    // Check source state exists in spec
    if (!spec.states[ev.state]) {
      violations.push({
        event_index: i,
        event: ev,
        allowed_events: Object.keys(spec.states),
        kind: "unknown_state",
        message: `State '${ev.state}' not declared in spec. Known states: ${Object.keys(spec.states).join(", ")}`
      });
      continue;
    }

    const stateSpec = spec.states[ev.state];
    const allowedEvents = Object.keys(stateSpec.on ?? {});

    // Check event is allowed from this state
    if (!stateSpec.on || !stateSpec.on[ev.event]) {
      violations.push({
        event_index: i,
        event: ev,
        allowed_events: allowedEvents,
        kind: "invalid_transition",
        message: `Event '${ev.event}' not allowed in state '${ev.state}'. Allowed: ${allowedEvents.join(", ") || "(none)"}`
      });
      continue;
    }

    // Check target state matches spec
    const transitions = stateSpec.on[ev.event];
    const transArray = Array.isArray(transitions) ? transitions : [transitions];
    const allowedTargets = transArray.map(t => t.target);

    if (!allowedTargets.includes(ev.next_state)) {
      violations.push({
        event_index: i,
        event: ev,
        allowed_events: allowedTargets,
        kind: "invalid_target",
        message: `Event '${ev.event}' in state '${ev.state}' transitions to '${ev.next_state}' but spec allows: ${allowedTargets.join(", ")}`
      });
    }
  }

  return violations;
}

// --- CLI ---

function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error("Usage: archwright-trace-validate <spec.yaml> <trace.json | ->");
    process.exit(2);
  }

  const specPath = args[0];
  const tracePath = args[1];

  // Load spec
  const specRaw = readFileSync(specPath, "utf8");
  const spec = parseYaml(specRaw) as BehaviorSpec;

  if (spec.kind !== "behavior") {
    console.error(`Spec '${specPath}' is kind '${spec.kind}', expected 'behavior'`);
    process.exit(2);
  }

  // Load trace
  const traceRaw = tracePath === "-"
    ? readFileSync(0, "utf8")
    : readFileSync(tracePath, "utf8");
  const trace = JSON.parse(traceRaw) as Trace;

  // Validate
  const violations = validate(spec, trace);

  // Output
  const result = {
    spec_id: spec.id,
    status: violations.length === 0 ? "pass" : "fail",
    violations,
    events_checked: trace.events.length,
    trace_source: trace.source
  };

  console.log(JSON.stringify(result, null, 2));
  process.exit(violations.length === 0 ? 0 : 1);
}

main();
