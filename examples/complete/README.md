# Snackbox — complete state

**Lifecycle state:** quiescence. Same design as `../partial/` — the code has
caught up with it. Every check passes; the evidence ledger is accumulating.

## What changed since partial/

| Partial | Complete |
|---------|----------|
| `dispenser.py` settles the balance (2 FAILs) | dispenser reports `dispense_done`; the session settles |
| `kiosk_ui.py` bench-test `import dispenser` (baselined) | import gone; `--update-baseline` ratcheted the entry away (no baseline file remains) |
| `src/hardware/` missing (`hardware-no-session-import` pending) | `coin_acceptor.py` exists — the pending check activated and passes |
| no evidence ledger | `design/.archwright-evidence.json` — see below |

## Run the checks

```bash
python3 tools/archwright-check.py --static examples/complete/design/specs
# 5 passed, 0 failed, 0 pending — exit 0
python3 tools/archwright-check.py examples/complete/design/specs/purchase-session.yaml
# both ★★ invariants hold (Alloy, bounded)
```

## What to notice at this state

1. **Quiescence, not silence.** All checks pass, but they keep running — the
   design stays live. Drift in any file re-opens the conversation with full
   provenance (try re-adding the dispenser's balance line from `../partial/`).
2. **The evidence ledger accumulates.** `design/.archwright-evidence.json`
   holds a real `promotion-candidate`: the ★-confidence
   `no-dispense-outside-session` check passed 5 consecutive runs
   (`config.promotion_streak` default), so the tool proposes considering a
   confidence promotion. **Ratification is human** — the ledger never edits
   a spec's confidence, and ★★ moves always block for HITL (ADR 0009).
3. **The committed ledger is a snapshot** (produced in a scratch copy —
   `code_state` is null-with-reason there). Because the file exists, any
   check run you make against this state appends to it: that's the feature.
   `git checkout` resets your experiments.
4. **The baseline is gone, not emptied.** Debt was paid; the ratchet removed
   the entry; the file itself was deleted when its last entry went. Compare
   `../partial/.archwright-baseline.json`.
