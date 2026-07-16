
# Subagent Reliability

Subagent calls are unreliable. Expect failures and design around them.

## Failure Modes (observed)

| Mode | Symptom | Frequency |
|------|---------|-----------|
| Empty response | Stage completes but returns no content | Common (~50%) |
| Timeout | ConnectorError / Connection timed out | Occasional |
| Partial response | Starts output then cuts off | Rare |
| Silent success | Returns but missed key content (no way to detect) | Unknown |

## Rules

### 1. Never silently absorb a failure

When a subagent returns empty or errors:
- **Report it immediately** to the user: "Subagent [name] returned empty. [N] of [M] stages failed."
- **State what was lost:** "Force extraction for play-data-schema, editor-ux, scene-composition was not completed."
- **Recommend remediation:** retry, read directly, or skip with documented gap.

Do NOT quietly fall back to reading everything in the main context without reporting the failure and its implications.

### 2. Design for partial failure

- **Keep stages small.** One grill session per stage, not six. A failure loses one session's work, not half the project.
- **Make stages idempotent.** If retried, the same stage produces the same output.
- **Track which stages succeeded.** Before proceeding, enumerate: "5/11 succeeded, 6/11 need retry or direct read."

### 3. Retry before fallback

When stages fail:
1. **First retry:** Re-dispatch failed stages only (not the whole batch). Smaller prompt may help.
2. **Second retry:** Split large stages further (e.g., 12 questions → 2 batches of 6).
3. **Fallback:** Only after 2 retries, read directly in main context. Report: "Reading [area] directly — subagent failed twice."

### 4. Validate subagent output

A non-empty response is not necessarily complete. Check:
- Does the output cover all files listed in the prompt?
- Does it have the expected structure (sections per session, forces listed)?
- Is the volume proportional to the input? (11 questions → expect 11+ forces, not 3)

If output looks thin relative to input, flag it: "Stage [name] returned content but coverage looks incomplete — [N] questions in, only [M] forces out."

### 5. Report coverage gaps in deliverables

The final artifact must declare its own completeness:
```markdown
## Coverage
- ✅ Fully extracted: [list of areas]
- ⚠️ Partial (subagent thin, supplemented by direct read): [list]
- ❌ Not extracted (subagent failed, not retried): [list]
```

## Anti-Patterns

- **Cowboy fallback:** Subagent fails → silently read everything in main context → present output as if systematic extraction occurred. The user can't distinguish rigorous from improvised.
- **Quiet partial coverage:** Only 5/11 areas extracted → proceed as if all 11 covered → force inventory has gaps the user doesn't know about.
- **Retry storm:** Retrying the same oversized prompt 5 times. If it failed twice with the same shape, the shape is wrong — split or simplify.
- **Context exhaustion:** Reading 100+ files directly after subagent failure → burns context budget → quality degrades in subsequent work without the user knowing why.

## Sizing Guidance

| Corpus size | Strategy |
|-------------|----------|
| 1-5 files, < 500 lines total | Read directly. NEVER subagent. |
| 6-15 files | One subagent per logical group (1 grill session = 1 stage) |
| 16-50 files | Multiple stages, 5-8 files each |
| 50+ files | Multiple stages + structured output format + validation |
| Data already in context | Do directly. NEVER re-dispatch. |

## Task Shape (what to subagent vs do directly)

| Task type | Subagent? | Why |
|-----------|-----------|-----|
| Read files → extract structured data | ✅ Yes | Small prompt ("read X, extract Y") + tool-mediated work |
| Transform provided text → new structure | ❌ No | Large inline prompt overflows subagent context |
| Cross-area dedup/merge | ❌ No | Requires seeing all areas together; do directly |
| Validate/check existing output | ⚠️ Maybe | Only if the data is in FILES, not inline |
| Multi-step reasoning | ❌ No | Better to work sequentially in main context |
| Research (web search + synthesis) | ⚠️ Unreliable | ~40% success rate; have a fallback plan |

**Root cause (validated):** Subagent failures correlate with **prompt size**, not task complexity. File-reading tasks succeed because the dispatch prompt is small (< 1K tokens) and work happens via tool calls. Synthesis tasks fail because the data is inlined in the prompt (5-10K+ tokens), which can overflow the subagent model's effective working space.

**The rule:** Never put large data inline in a subagent prompt. If the subagent needs data, write it to a file and have the subagent read it.

## Batching Strategy

Plan subagent dispatches in batches sized by the tool's concurrency limit. Each batch completes before the next starts.

```
Batch 1: [stage-A, stage-B, stage-C, stage-D]  → wait for all
Batch 2: [stage-E, stage-F, stage-G]           → wait for all
Validate: check success count before proceeding
```

**Rules:**
- Never exceed the tool's concurrency limit per batch
- Validate each batch's results before dispatching the next
- If a batch has 2+ failures, STOP — don't dispatch the next batch
- Order batches by dependency: independent stages first, dependent stages after

## Write-Then-Read Pattern

When a subagent needs to process data that's already in your main context:

1. Write the data to a temp file: `.scratch/subagent-input/{stage-name}.md`
2. Dispatch the subagent with: "Read `.scratch/subagent-input/{stage-name}.md` and [task]"
3. The subagent's prompt stays small; the data loads via tool call

This converts a "synthesis with inline data" (fails ~90%) into a "file reading" task (succeeds ~93%).

## Preserving Subagent Output

When a subagent phase produces raw extraction that a later phase will consume:
- Save raw results to `.scratch/subagent-raw/` (ephemeral but session-durable)
- Later phases read the saved output rather than re-dispatching
- This avoids: double extraction cost and re-read failures

## Detecting Degraded Reliability

If 2+ stages in a batch return empty:
1. STOP dispatching subagents
2. Report: "N/M stages returned empty. Switching to direct reading."
3. For remaining files < 500 lines total: read directly
4. For larger corpora: use the write-then-read pattern with smaller batches (2 stages at a time)

## Tool-Specific Limits

For per-tool concurrency limits and validated failure patterns (kiro-cli, codex, agy, crush), read [references/tool-limitations.md](references/tool-limitations.md).
