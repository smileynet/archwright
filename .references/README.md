# .references/: external binaries and reference material (gitignored)

Only this README is committed. Everything else here is local.

## Rehydrate

On a fresh checkout, from the repo root:

```sh
mise run rehydrate-alloy   # Alloy 6.2.0 dist jar -> .references/alloy6.jar (pinned URL + SHA-256: tools/alloy-runtime.json)
```

Without mise: `python3 tools/install-alloy.py`. Behavior checks SKIP (a coverage gap, not a pass) until the jar exists.

## Entries

| Entry | What it is | Source |
|---|---|---|
| `alloy6.jar` | Alloy 6 analyzer (≥ 6.2.0, for the `exec` CLI) | downloaded by `tools/install-alloy.py`; not a git clone |
