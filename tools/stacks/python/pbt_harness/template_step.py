"""Example step function for archwright PBT harness.

The step function bridges the PBT harness to your system under test.
It receives an event name and the current context variables, applies the
event to your system, and returns the new state snapshot.

Replace the body with calls to YOUR system.
"""


def step(event: str, context: dict) -> dict:
    """Apply an event to the system under test, return new state snapshot.

    Args:
        event: The event name from the behavior spec (e.g., "JOIN", "LEAVE")
        context: Current context variable snapshot (dict)

    Returns:
        New state snapshot (dict) — the context variables after the event.
        Keys must match the spec's context.variables.
    """
    # === REPLACE THIS WITH YOUR SYSTEM CALLS ===

    # Example for a session manager:
    #
    # if event == "INITIAL":
    #     session_manager.reset()
    #     return {"current_players": 0, "max_players": 3}
    # elif event == "JOIN":
    #     session_manager.add_player("test_player")
    #     return {"current_players": session_manager.count, "max_players": 3}
    # elif event == "LEAVE":
    #     session_manager.remove_player("test_player")
    #     return {"current_players": session_manager.count, "max_players": 3}

    raise NotImplementedError(f"Step function not implemented for event: {event}")
