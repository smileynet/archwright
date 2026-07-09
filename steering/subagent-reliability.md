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
| 1-5 files | Read directly, no subagent needed |
| 6-15 files | One subagent per logical group (1 grill session = 1 stage) |
| 16-50 files | Multiple stages, 5-8 files each |
| 50+ files | Multiple stages + structured output format + validation |

For the LBP survey (106 grill files across 11 sessions): 11 stages, one per grill session. Not 2-3 mega-stages that batch 5-6 sessions together.
