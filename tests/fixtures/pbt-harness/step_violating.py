"""Buggy step function: no guard on INCREMENT, exceeds capacity."""

_count = 0
_max_count = 3


def step(event, context):
    global _count, _max_count
    if event == "INITIAL":
        _count = 0
        _max_count = 3
        return {"count": _count, "max_count": _max_count}
    elif event == "INCREMENT":
        _count += 1  # BUG: no guard — will exceed max_count
        return {"count": _count, "max_count": _max_count}
    elif event == "RESET":
        _count = 0
        return {"count": _count, "max_count": _max_count}
    return {"count": _count, "max_count": _max_count}
