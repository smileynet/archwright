---
id: "025"
title: "woz-export consumer: skill interpretation + category mapping"
status: done
blocked_by: ["020"]
---

# woz-export consumer (T7b)

Consume wizard_of_oz's neutral-JSON session export (exporter = T7a, tracked in wizard_of_oz repo): decisions → force evidence, sim log → model-seed states/events, wireframes → screen flow, draft behavior spec w/ `from_woz:` provenance. Category mapping (woz enum → core-5 + game extensions) lives here (consumer side, Q5). Conservation check applies (Q6): every output cites source entries; unconsumed decisions listed.

UNBLOCKED 2026-07-19: wizard_of_oz shipped the exporter (T7a). JSON contract is versioned from both sides — read the shipped export format from the wizard_of_oz repo before implementing the consumer.

Context: ADR 0011; spec T7b; grill Q5/Q6.
