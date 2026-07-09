# Context Assembly

What the agent reads for each archwright task. A deterministic function, not "read everything relevant."

Inspired by the Spec Growth Engine's Spine + Context(N) formula.

## The Formula

```
Context(task) =
  Project AGENTS.md (root invariants, conventions)
  + Target pattern (the pattern being worked on)
  + Target spec (the spec being created/modified)
  + Dependency contracts (one hop — specs this spec links TO, contract section only)
  + Affected code paths (files the spec's check.target references)
  + Domain overlay (if applicable — game predicates, scales)
```

## What Is EXCLUDED (deliberately)

- Sibling patterns/specs (not relevant to this node)
- Dependency internals (their design, their code — only their contract)
- Transitive dependencies (dependencies of dependencies)
- Unrelated code (anything not in check.target)
- Other projects' patterns/specs

## Per Task Type

| Task | Context includes |
|------|-----------------|
| **Identify forces** | AGENTS.md + existing patterns (scan for related) + target domain docs + conversation history |
| **Resolve tension** | Target pattern + prior art (research results) + related patterns (above/below links) |
| **Derive spec** | Target pattern + spec template + dependency contracts + domain predicates |
| **Check spec** | Target spec + check.target files + dependency contracts (for link validation) |
| **Route correction** | Violated spec + from_pattern + from_force + contrast pair + pattern's resolution section |

## Why This Matters

SGE showed (Grabowski 2026) that context explosion degrades agent output — quality drops with context length. Models retrieve worst from the middle of long contexts (Liu et al. 2024). Performance can collapse from 29% to 3% as context grows from 32K to 256K tokens (LongCodeBench).

The fix: give the agent LESS, BETTER-CHOSEN context. The formula above ensures the agent sees exactly what it needs and nothing else.

## The Default Repair

If the context is insufficient for a task (agent can't find what it needs):
- **DO:** Fix the spec graph — add a missing link, add a missing contract, declare a dependency
- **DO NOT:** Widen the context by reading more files

The spec graph is the source of truth for what depends on what. If the graph doesn't contain the connection, either the connection doesn't exist (agent shouldn't need it) or the graph is incomplete (fix the graph, not the context rule).
