---
kind: constraint
id: no-server-dependency
from_patterns:
  - "pattern:static-report-response-file"
confidence: "★"
protects_experience: "exp-loop-closes"
user_story: "The report opens from a file anywhere — CI artifact, laptop, air-gapped review — and answering asks needs no server."
check:
  method: grep
  target: "tools/report/templates/"
  pattern: "fetch\\(|XMLHttpRequest|WebSocket|EventSource|navigator\\.sendBeacon|<script[^>]+src=[\"']https?:|<link[^>]+href=[\"']https?:"
  include: ["*.html", "*.js", "*.j2", "*.tmpl"]
  expect: absent
links:
  - target: "contract:response-file"
    type: constrains
---

# No Server Dependency

## Rule

The report page makes no network requests and loads no remote resources: no
fetch/XHR/WebSocket/beacon calls, no external script or stylesheet URLs, no
webfonts. Everything the page needs is inline in the single file; the response
file is written via a local save, never transmitted.

## Rationale

`static-report-response-file` + the `zero-infrastructure-artifact` force
(design-system#D005, P5): the report travels as a CI artifact and must be
readable and answerable with zero setup. One remote dependency breaks file://
opening, air-gapped review, and long-term artifact integrity. "Nothing is sent
anywhere — the file is the handoff" (wf-overview#D006).

## Violations Look Like

```html
<!-- BAD — remote resource + network call: -->
<script src="https://cdn.example.com/chart.js"></script>
<script>fetch("/api/responses", { method: "POST", body: data })</script>
```

## Correct Usage

```html
<!-- GOOD — inline everything; responses save to a local file: -->
<script>/* inlined at generation time */ downloadResponseFile(state)</script>
```
