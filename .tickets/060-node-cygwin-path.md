---
id: "060"
title: "suite: page reducer test uses Cygwin pwd path incompatible with Node require()"
status: open
blocked_by: []
---

# suite: page reducer test uses Cygwin pwd path incompatible with Node require()

## Context

The page reducer trace test in `run-fixture-tests.sh` computes:

```bash
RT_ABS="$(cd "$TOOLS" && pwd)"
```

On Windows with Cygwin/MSYS bash, `pwd` returns a POSIX path like
`/c/Users/uosmi/code/archwright/tools`. The test then passes this into
a `node -e` script:

```js
const R = require('$RT_ABS/report/templates/page.js');
```

Node.js (native Windows build) cannot resolve Cygwin POSIX paths —
`require('/c/Users/...')` throws `MODULE_NOT_FOUND`. Node needs a
Windows-native path like `C:/Users/uosmi/code/archwright/tools/...`.

Reproduced: 2026-07-27 on Windows 11, Cygwin bash 5.3.9, Node 22.23.1
(mise-managed).

## What to build

Fix the path computation so Node receives a Windows-native path. Options:

1. **Use `cygpath -w`** (or `cygpath -m` for forward slashes):
   `RT_ABS="$(cygpath -m "$(cd "$TOOLS" && pwd)")"` — converts to
   `C:/Users/...` which Node understands
2. **Use `pwd -W`** (MSYS-specific): returns Windows path directly —
   less portable but simpler
3. **Use Node's own resolution**: pass the path as a relative require
   (`./tools/report/templates/page.js`) from the correct cwd instead
   of computing an absolute path

Also applies to `RG_TMP` if it's used in the same node -e block (it is:
`require('fs').writeFileSync('$RG_TMP/trace.json', ...)`). The TMPDIR fix
gives RG_TMP a Windows-native prefix, but RT_ABS needs the same treatment.

## Acceptance criteria

- [ ] page reducer `node -e` script can require() the page.js module on Windows
- [ ] Trace file written by node is accessible to the subsequent python3 trace check
- [ ] Suite "page reducer trace validates vs ask-lifecycle" passes on Windows
- [ ] Fix is no-op on Linux/macOS (forward slashes work everywhere)
