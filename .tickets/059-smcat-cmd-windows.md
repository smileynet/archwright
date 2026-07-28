---
id: "059"
title: "report render: smcat.CMD not executable via subprocess.run on Windows"
status: open
blocked_by: []
---

# report render: smcat.CMD not executable via subprocess.run on Windows

## Context

`render_html.py` calls `subprocess.run(["smcat", "-T", "svg", "-"], ...)`
to render state machine diagrams. On Windows, mise installs smcat as
`smcat.CMD` (a batch file wrapper around the Node module), not `smcat.exe`.

Python's `subprocess.run` with a list argument on Windows cannot execute
`.CMD` files without `shell=True` — it throws `FileNotFoundError` ([WinError 2]).
The code catches this as `OSError` and falls back to a plain `<ul>` list,
so the report generates but without the SVG diagram.

`shutil.which("smcat")` correctly finds `smcat.CMD`, confirming the tool is
installed — the issue is purely subprocess execution of batch wrappers.

Reproduced: 2026-07-27 on Windows 11, mise-managed smcat 15.0.6.

## What to build

Fix `render_html.py`'s smcat subprocess call to work on Windows. Options:

1. **Use `shutil.which("smcat")`** to get the full path (including `.CMD`
   extension), then call with `shell=True` only on Windows — or use the
   full path which Windows CreateProcess can resolve
2. **Detect `.cmd`/`.bat` extension** from which() result and add `shell=True`
   for that case
3. **Call via `node`**: since smcat is a Node module, invoke it as
   `node <path_to_smcat_cli.js>` which avoids the batch wrapper entirely

## Acceptance criteria

- [ ] `render_html.py` produces SVG output when smcat is installed as a .CMD wrapper
- [ ] Report HTML contains the labeled-arrow diagram, not just a state list
- [ ] Suite "smcat source carries labeled arrows; label reaches HTML when smcat present" passes on Windows
- [ ] Non-Windows behavior unchanged (subprocess.run(["smcat", ...]) still works)
