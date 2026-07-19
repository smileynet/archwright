"""Dispenser — motor servant for contract:dispense-command.

Complete state: the partial state's defect is gone. This module's whole
world is: receive dispense(slot), run the motor, report completion. It
never touches money-state and never talks to other peripherals
(dependency:dispenser-isolation).
"""


class Dispenser:
    def __init__(self, session=None):
        self.motor_running = False
        self.session = session

    def dispense(self, slot):
        self.motor_running = True
        ok = self.run_motor(slot)
        self.motor_running = False
        if self.session is not None:
            self.session.dispense_done(slot, ok)

    def run_motor(self, slot):
        return True  # spins the shelf coil for `slot`
