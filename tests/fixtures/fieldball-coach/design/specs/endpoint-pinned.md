---
kind: constraint
id: endpoint-pinned
from_patterns:
  - "pattern:explicit-dependencies"
confidence: "★"
protects_experience: "predictable-practice-runs"
user_story: "When a practice run replays, it talks to the pinned TLS backend — never an ambient or legacy endpoint."
check:
  method: grep
  target: "client/src/services/NetConfig.cs"
  pattern: "\"https://api\\.fieldball-coach\\.example\""
  expect: present
links: []
---

# Endpoint Pinned

## Rule

`NetConfig.cs` pins the TLS API base URL. Exactly this literal must be present.

## Conformance Role (fixture suite)

Golden corpus for positional comment handling in `//`-comment languages: the
pattern contains `//` (inside `https://`), and the matching line also carries a
trailing `//` comment. If comment handling ever regresses to *truncating* lines
at the first comment token, `https://` self-truncates, the literal never
matches, and this `expect: present` check flips red (the field false-PASS bug,
2026-07-17). The commented-out `http://` line in the same file must NOT count
as a match for absence-style checks.

## Violations Look Like

```csharp
// BAD — ambient endpoint, not pinned:
var api = Environment.GetEnvironmentVariable("API_BASE");
```

## Correct Usage

```csharp
// GOOD — pinned TLS endpoint:
public const string ApiBase = "https://api.fieldball-coach.example";
```
