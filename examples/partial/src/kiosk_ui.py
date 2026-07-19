"""Kiosk UI — renders session state, raises customer intents.

KNOWN DEBT (baselined in ../.archwright-baseline.json): the bench-test
maintenance hookup below wires the UI straight to the dispenser module,
violating constraint:ui-no-hardware-import. Accepted as a baseline entry
when checks were first turned on — it reports as a WARNING with
`baselined: true`, not a failure, and the baseline ratchet
(`--update-baseline`) removes the entry the day the hookup is gone (the
complete state shows exactly that).
"""

import dispenser  # known debt: maintenance-mode direct hookup, baselined


class KioskUi:
    def __init__(self, session):
        self.session = session

    def render(self):
        return f"credit: {self.session.balance}c"  # read-only: the session owns money

    def on_vend_pressed(self):
        self.session.vend()

    def on_cancel_pressed(self):
        return self.session.cancel()

    def maintenance_test(self, slot):
        # Bench-test path from before the session protocol existed.
        dispenser.Dispenser(self.session).dispense(slot)
