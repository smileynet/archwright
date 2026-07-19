"""Dispenser — motor servant for contract:dispense-command.

PARTIAL-STATE DEFECT (deliberate, for the lifecycle example): dispense()
settles the customer's money itself "to save a round trip". This single
line violates TWO specs — the single-writer constraint (money-state
assigned outside the authority) and the isolation dependency rule (the
dispenser knows about money at all).

Run the check to see both violations with their provenance chains:

    python3 tools/archwright-check.py --static examples/partial/design/specs
"""


class Dispenser:
    def __init__(self, session=None):
        self.motor_running = False
        self.session = session

    def dispense(self, slot):
        self.motor_running = True
        self.run_motor(slot)
        self.motor_running = False
        self.session.balance = 0  # BAD: settling money is the gate's job
        if self.session is not None:
            self.session.dispense_done(slot, True)

    def run_motor(self, slot):
        pass  # spins the shelf coil for `slot`
