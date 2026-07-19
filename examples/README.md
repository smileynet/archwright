# Examples — one product, three lifecycle states

**Snackbox** is a toy vending kiosk: insert coins, pick a snack, vend or
cancel. One invented product, expressed at three lifecycle states, so the
*diff between the states* shows what archwright does as a project grows.
These directories are live fixtures — the suite asserts each state's expected
check results, so they track "what good looks like today" as the methodology
evolves.

The design story in one line: the customer's **fair exchange** desire (snack
or full refund, never neither) is resolved by a **payment-gate** pattern into
one guarded state machine, two contracts, three constraints, and a dependency
rule — then code arrives, drifts, gets caught, and catches up.

## State 0 — greenfield (no directory: this section is the state)

You have an empty repo, or a pile of code with no `design/`. There is nothing
for a directory to show and nothing for a check to assert — which is exactly
the point: archwright starts with a conversation, not an artifact.

Ask your agent to **"survey this project"**. On a greenfield, survey finds no
forces, no patterns, no specs — it reports the design space as open and
queues the discovery track: a grill session to interrogate what you're
building, a UI session (`archwright-discover-ui`) if screens exist in your
head, a WoZ import (`archwright-woz-import`) if you've played the game out in
a wizard_of_oz session. Decisions land in ledgers; approved decisions enter
the pipeline at `resolve`; the pipeline (forces → … → derive) turns them into
exactly the kind of `design/` tree you see in `planned/`.

**→ `planned/` is where a greenfield lands** after the pipeline's first full
pass, before any code is written.

## The three states

| | `planned/` | `partial/` | `complete/` |
|---|---|---|---|
| **Design** | full `design/` | + 2 specs derived mid-build | same as partial |
| **Code** | none | first modules, one defect | caught up |
| **Static checks** | 3 pending | 2 FAIL, 1 baselined warning, 1 pass, 1 pending | 5 pass |
| **Behavior check (Alloy)** | pass — proven before code | pass — the design didn't regress | pass |
| **Exit code** | 0 | **1** | 0 |
| **Debt files** | — | `.archwright-baseline.json` | ledger accumulating (`design/.archwright-evidence.json`) |

Walk them in order:

1. **[`planned/`](planned/README.md)** — design complete, zero code. The ★★
   invariants are model-checked NOW (the payment gate is *proven* before
   implementation starts); code-facing checks declare `target_status: pending`
   and wait.
2. **[`partial/`](partial/README.md)** — code arrives, and with it the two
   things checks exist for: a real defect (the dispenser settles money —
   one line, two FAILs, full provenance chains) and known debt (a bench-test
   import, baselined to a warning that keeps its ★★ escalate flag).
3. **[`complete/`](complete/README.md)** — quiescence. The defect is fixed,
   the debt paid and ratcheted out of the baseline, the pending check
   activated by the hardware module landing, and the evidence ledger is
   accumulating pass streaks (a real promotion-candidate is in the committed
   snapshot).

## What to try

```bash
# The lifecycle in three exit codes:
python3 tools/archwright-check.py --static examples/planned/design/specs    # 0 — pending
python3 tools/archwright-check.py --static examples/partial/design/specs    # 1 — caught
python3 tools/archwright-check.py --static examples/complete/design/specs   # 0 — quiescent

# The payment gate, proven with no code in sight:
python3 tools/archwright-check.py examples/planned/design/specs/purchase-session.yaml

# What a catch looks like (violations with provenance, fingerprints, contrast pairs):
python3 tools/archwright-check.py --static examples/partial/design/specs --json
```

Note: `complete/` ships a committed evidence-ledger snapshot; check runs
against it append events (that's the feature). `git checkout` resets your
experiments.

## Relation to `tests/fixtures/`

`tests/fixtures/` holds *targeted tool corpora* (one feature exercised
precisely, frozen as golden). `examples/` holds *lifecycle corpora* — small
but complete project states, evolved deliberately whenever schemas or the
methodology change. The fixture suite asserts both.
