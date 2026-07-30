---
id: "080"
title: "ELK diagram: async layout race condition"
status: done
priority: high
blocked_by: []
---

## Problem

When layout requests are fired in rapid succession (e.g. model changes during an in-flight ELK computation), a stale result can arrive after a newer one and overwrite it, causing the diagram to snap to an outdated layout.

## What to fix

Track each layout request with a monotonic ID. When a result returns, compare its ID to the latest dispatched ID — discard if stale.
