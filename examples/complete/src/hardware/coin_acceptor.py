"""Coin acceptor shim — the hardware boundary entity (contract:coin-events).

A peripheral, not an authority: it reports coin events upward through a
callback wired in main, and pays out refunds when commanded. It knows
nothing about sessions (constraint:hardware-no-session-import) — the
dependency arrow points one way.
"""


class CoinAcceptor:
    def __init__(self, on_coin):
        self._on_coin = on_coin  # wired to the session authority in main

    def coin_pulse(self, amount_cents):
        # Hardware interrupt → typed event (contract:coin-events).
        self._on_coin(amount_cents)

    def pay_out(self, amount_cents):
        return amount_cents  # drives the hopper; refund leg of the coin protocol
