"""archwright Python trace emitter (stack adapter, Extension Protocol / ADR 0008).

Records state transitions during test/harness execution and writes the JSON
shape consumed by ``archwright-check.py --trace``:

    [
      {"event": "INITIAL", "state": {"<var>": <value>, ...}, "clock": 0},
      {"event": "JOIN",    "state": {...},                   "clock": 1},
      ...
    ]

Shape notes (contract shared with the TypeScript adapter, verified against
check_trace):
- The trace is a BARE JSON ARRAY (not an envelope object).
- The first entry MUST be event "INITIAL" with the initial variable snapshot.
- ``state`` is the FULL context-variable snapshot after the event (guards are
  evaluated against the PREVIOUS entry's snapshot; invariants against this one).
- Variable names use the spec's snake_case ``context.variables`` keys.

Implementation notes (research pass, ticket 049):
- Snapshots are taken AT RECORD TIME via a JSON round-trip — storing live
  references and serializing at teardown records the final state in every
  entry (the mutable-argument pitfall the stdlib documents for
  mock.call_args); the round-trip also fails fast at the offending event if a
  value is not JSON-serializable, instead of at write time.
- Writes are atomic: temp file in the target directory + ``os.replace`` —
  a mid-dump kill never leaves truncated JSON for the trace consumer.

Stdlib only (json/os/tempfile). Python >= 3.6. Pytest usage:

    rec = TraceRecorder({"current_players": 0, "max_players": 3})
    # ... after each successful domain action:
    rec.record("JOIN", current_players=1)
    # ... at test end / fixture teardown:
    rec.write("design/traces/session-lifecycle.trace.json")
"""

import json
import os
import tempfile


def _snapshot(mapping):
    """Detached, JSON-safe copy — fails fast on non-serializable values."""
    return json.loads(json.dumps(mapping))


class TraceRecorder:
    """Accumulates {event, state, clock} entries; full snapshot per entry."""

    def __init__(self, initial_vars):
        self._snapshot = _snapshot(dict(initial_vars))
        self._trace = [{"event": "INITIAL", "state": dict(self._snapshot), "clock": 0}]

    def record(self, event, **changed):
        """Record an event with the context vars that CHANGED (merged onto the
        running snapshot). Record consequences, not intentions — pass values
        read back from the real system after the operation."""
        self._snapshot.update(_snapshot(changed))
        self._trace.append(
            {"event": event, "state": dict(self._snapshot), "clock": len(self._trace)}
        )

    def entries(self):
        """The entries recorded so far (INITIAL included)."""
        return list(self._trace)

    def to_json(self):
        """Serialize to the validator's JSON shape."""
        return json.dumps(self._trace, indent=2, ensure_ascii=False)

    def write(self, path):
        """Write the trace file atomically, creating parent directories."""
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".trace.tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(self.to_json() + "\n")
            os.replace(tmp, path)
        except BaseException:
            os.unlink(tmp)
            raise
