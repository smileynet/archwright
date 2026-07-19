"""Kiosk UI — renders session state, raises customer intents.

Complete state: the bench-test hardware hookup is gone (the baseline entry
that covered it was removed by `--update-baseline` — the ratchet). The UI
reads session state and raises intents; the session decides everything.
"""


class KioskUi:
    def __init__(self, session):
        self.session = session

    def render(self):
        return f"credit: {self.session.balance}c"  # read-only: the session owns money

    def on_vend_pressed(self):
        self.session.vend()

    def on_cancel_pressed(self):
        return self.session.cancel()
