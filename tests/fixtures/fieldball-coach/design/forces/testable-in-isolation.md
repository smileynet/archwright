---
kind: force
id: testable-in-isolation
polarity: desire
evidence_level: L3
source: "AGENTS.md convention + gdUnit test history"
---

# Testable In Isolation

## Statement

Any component can be tested headless with mock collaborators — no hidden globals, no scene-tree prerequisites.

## Who Feels It

The developer writing tests; CI running them. Hidden dependencies turn every unit test into an integration test.

## Evidence

gdUnit tests became order-dependent when autoloaded services leaked state between tests; explicit injection fixed it.
