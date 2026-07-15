#!/usr/bin/env bash
# archwright-trace-validate: Validate a JSON trace against a behavior spec.
#
# Usage:
#   archwright-trace-validate <spec.yaml> <trace.json>
#
# Converts spec to JSON via yq, then validates with Node.
# Exit: 0 = pass, 1 = violations, 2 = usage error

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: archwright-trace-validate <spec.yaml> <trace.json>" >&2
  exit 2
fi

SPEC_PATH="$1"
TRACE_PATH="$2"

# Convert YAML spec to JSON
SPEC_JSON=$(yq -o=json '.' "$SPEC_PATH")

# Run inline Node validator
node --input-type=module -e "
const spec = JSON.parse(process.argv[1]);
const trace = JSON.parse(process.argv[2]);

if (spec.kind !== 'behavior') {
  console.error('Spec is kind ' + spec.kind + ', expected behavior');
  process.exit(2);
}

const violations = [];

if (trace.initial_state !== spec.initial) {
  violations.push({
    event_index: -1,
    event: { state: trace.initial_state, event: '(initial)', next_state: trace.initial_state },
    allowed_events: [],
    kind: 'unknown_state',
    message: 'Trace initial_state \"' + trace.initial_state + '\" != spec initial \"' + spec.initial + '\"'
  });
}

for (let i = 0; i < trace.events.length; i++) {
  const ev = trace.events[i];
  const stateSpec = spec.states?.[ev.state];

  if (!stateSpec) {
    violations.push({
      event_index: i, event: ev,
      allowed_events: Object.keys(spec.states || {}),
      kind: 'unknown_state',
      message: 'State \"' + ev.state + '\" not in spec'
    });
    continue;
  }

  const transitions = stateSpec.on?.[ev.event];
  if (!transitions) {
    violations.push({
      event_index: i, event: ev,
      allowed_events: Object.keys(stateSpec.on || {}),
      kind: 'invalid_transition',
      message: 'Event \"' + ev.event + '\" not allowed in state \"' + ev.state + '\". Allowed: ' + Object.keys(stateSpec.on || {}).join(', ')
    });
    continue;
  }

  const transArray = Array.isArray(transitions) ? transitions : [transitions];
  const allowedTargets = transArray.map(t => t.target);
  if (!allowedTargets.includes(ev.next_state)) {
    violations.push({
      event_index: i, event: ev,
      allowed_events: allowedTargets,
      kind: 'invalid_target',
      message: 'Event \"' + ev.event + '\" in \"' + ev.state + '\" -> \"' + ev.next_state + '\" but spec allows: ' + allowedTargets.join(', ')
    });
  }
}

const result = {
  spec_id: spec.id,
  status: violations.length === 0 ? 'pass' : 'fail',
  violations: violations,
  events_checked: trace.events.length,
  trace_source: trace.source
};

console.log(JSON.stringify(result, null, 2));
process.exit(violations.length === 0 ? 0 : 1);
" "$SPEC_JSON" "$(cat "$TRACE_PATH")"
