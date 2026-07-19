"""PaymentSession — the payment-gate authority (behavior:purchase-session).

Sole writer of `.balance` (constraint:single-balance-writer). The guarded
VEND transition below IS the payment gate from pattern:payment-gate.
"""

IDLE, ACCEPTING, DISPENSING = "idle", "accepting", "dispensing"


class PaymentSession:
    def __init__(self, dispenser, price_cents):
        self.state = IDLE
        self.balance = 0
        self.selected_slot = None
        self.price = price_cents
        self._dispenser = dispenser

    def coin_inserted(self, amount):
        # contract:coin-events — the acceptor reports, the session applies.
        if self.state in (IDLE, ACCEPTING):
            self.balance = self.balance + amount
            self.state = ACCEPTING

    def select(self, slot):
        if self.state == ACCEPTING:
            self.selected_slot = slot

    def vend(self):
        # THE payment gate: dispensing is reachable only through this guard.
        if self.state == ACCEPTING and self.selected_slot is not None \
                and self.balance >= self.price:
            self.state = DISPENSING
            self._dispenser.dispense(self.selected_slot)

    def cancel(self):
        if self.state == ACCEPTING:
            refund = self.balance
            self.balance = 0
            self.state = IDLE
            return refund
        return 0

    def dispense_done(self, slot, success):
        # contract:dispense-command ack leg. On jam, the exchange reverts.
        change = self.balance - self.price if success else self.balance
        self.balance = 0
        self.selected_slot = None
        self.state = IDLE
        return change
