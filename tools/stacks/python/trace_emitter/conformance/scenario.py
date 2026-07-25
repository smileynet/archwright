"""Conformance scenario for the Python trace emitter (Extension Protocol rule 3:
spike output IS the conformance scenario; rule 4: MUST include a violating
scenario that produces FAIL).

Simulates a session-like guarded counter (mirrors the guarded-counter fixture
and the TypeScript adapter's scenario) and emits two traces via the real
recorder:

    passing.trace.json   -- respects the JOIN guard (never exceeds max)
    violating.trace.json -- a buggy implementation admits a 4th player
                            (capacity-never-exceeded must FAIL at that entry)

Run: python3 scenario.py <outdir>
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from trace_recorder import TraceRecorder  # noqa: E402

out_dir = sys.argv[1] if len(sys.argv) > 1 else "."


def correct_run():
    """Correct implementation: guard respected."""
    rec = TraceRecorder({"current_players": 0, "max_players": 3})
    players = 0
    max_players = 3

    def join():
        nonlocal players
        if players < max_players:
            players += 1
            rec.record("JOIN", current_players=players)
            return True
        return False  # guard rejected — nothing recorded, nothing happened

    join()  # 1
    join()  # 2
    join()  # 3
    join()  # rejected at capacity — correctly not recorded
    rec.record("START")
    rec.record("COMPLETE")
    rec.write(os.path.join(out_dir, "passing.trace.json"))


def buggy_run():
    """Buggy implementation: guard missing — admits a 4th player."""
    rec = TraceRecorder({"current_players": 0, "max_players": 3})
    players = 0

    def join_unguarded():
        nonlocal players
        players += 1  # BUG: no capacity check
        rec.record("JOIN", current_players=players)

    join_unguarded()  # 1
    join_unguarded()  # 2
    join_unguarded()  # 3
    join_unguarded()  # 4 — capacity exceeded; validator must FAIL here
    rec.record("START")
    rec.write(os.path.join(out_dir, "violating.trace.json"))


correct_run()
buggy_run()
print("traces written")
