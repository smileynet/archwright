# Research: Structuring Multi-Stage AI Agent Workflows

Date: 2026-07-18 · Researcher: subagent (agent-pipeline-orchestration)

## Summary

The literature converges on three findings. (1) **Split a pipeline only when the task exceeds one context window or crosses a trust/stakeholder boundary** — coordination overhead is real (Anthropic measured ~15x token cost for multi-agent vs. chat; 36.94% of multi-agent failures in one taxonomy are coordination failures), so a single agent with good tools is the default until it demonstrably breaks. (2) **HITL gates should be placed by action consequence, not by agent confidence** — LLM confidence is systematically miscalibrated (claimed 90% ≈ ~75% real accuracy; a 3-agent chain at claimed 90%/step is ~42% reliable end-to-end), so the mature pattern is a 4-tier action-risk classification where only irreversible/external actions hard-block, and gates are enforced in the workflow definition, never negotiated by the agent at runtime. (3) **Pipelines compose through typed shared state, schema-validated handoffs, and durable "living spec" artifacts** — the composition contract is a DAG of subtasks with validation gates at every seam, and async (checkpoint-and-resume) approval is the production default because synchronous blocking collides with infrastructure timeouts.

Notably, archwright's existing design (ADR 0007 HITL-only gates, ★★-blocks, span digests, validation gates between phases, baseline-suppressed checks) already matches the strongest published patterns closely; the main external ideas not yet reflected are the explicit action-risk tiering vocabulary, idempotency keys + state-hash verification on resume, and confirmation-fatigue as a security argument for fewer gates.

## Details

### 1. Decomposition criteria — when to split one pipeline into multiple

**The default is NOT to split.** Multiple sources (Augment Code guide; single-agent research it cites; Anthropic's "building effective agents" building blocks) state that a single agent with a general-purpose toolbox is competitive with multi-agent systems for anything that fits one context window, and is faster, cheaper, and far easier to debug.

**Split when one of these holds:**
- **Context-window exceedance** — the task spans enough files/services/steps that a single agent loses coherence as history accumulates ("does the task exceed what one context window can hold without degrading output quality?" is the reduction test).
- **Privileged-information boundaries** — different sub-agents must see different data (security, tenant isolation, need-to-know).
- **Distinct principals/stakeholders** — each agent represents a different authority (e.g., an implementor vs. an independent verifier; verifier independence specifically counters "agreement bias" / verifier false passes).
- **Parallelizable independent subtasks** — literature review + competitor analysis + financial summary type fan-outs; a single agent serializes what could run concurrently.
- **Different cadences or lifecycles** — a sub-workflow that runs hourly/overnight or must survive process restarts wants its own durable pipeline with checkpointing.

**Cost side of the ledger:** ~15x token cost (Anthropic, multi-agent research system); coordination failures are the single largest failure class (36.94% in the MAST taxonomy across AutoGen/CrewAI/LangGraph); mesh communication scales O(N²). Rule of thumb from the Augment guide: start with explicit task decomposition + shared state + verification gates on ONE workflow that already breaks single-agent execution, before expanding agent count.

**Decomposition shape:** produce a DAG of subtasks where nodes are subtasks and edges encode which outputs feed which inputs (HTN-planning lineage). Production systems layer roles onto the DAG:
- **Coordinator / Manager** — decomposes, re-plans adaptively when quality degrades (static role definitions are a known limitation of mainstream frameworks).
- **Workers / Implementors** — execute in scoped contexts, ideally isolated (git worktrees; one-writer-per-module eliminates parallel write conflicts by construction).
- **Verifier / Evaluator** — a blocking pre-merge check against the spec, separate from the generating agent.
- **Waves** — tasks at the same DAG depth run in parallel; next wave starts only when the prior completes (Intent's model).

**Topology selection** (Augment/AdaptOrch): hub-and-spoke for auditable, spec-driven work (high observability, hub is SPOF); hierarchical for large scale (partitions context so no agent needs the full picture); sequential for strictly ordered dependencies (easiest debugging — failures stage-localize); mesh only for small fixed agent counts (2–4) doing adversarial/debate work. AdaptOrch found adaptive topology selection beat any single fixed topology by ~22.9% on SWE-bench Verified — i.e., topology should be a per-task decision, not a global one.

### 2. HITL gate placement patterns

**Three mechanical HITL patterns** (DZone framework comparison, June 2026):
1. **Durable graph interrupt** (LangGraph/deepagents `interrupt()`) — full state serialized at the exact node; process can exit and resume hours later; supports approve/EDIT/reject. The only pattern that survives process restarts today.
2. **Message-loop injection** (AutoGen UserProxy) — human is a peer participant in the conversation; no true suspension; state lost on process exit. Fits real-time co-pilot use.
3. **Blocking gate / run-termination** (Pydantic AI deferred tools, OpenAI Agents SDK `needs_approval`, CrewAI `human_input`) — run ends cleanly with a pending-approval object; caller owns persistence and resume.

Choosing among them turns on three questions: intervention granularity (tool call vs. step vs. task output), reviewer latency (real-time vs. hours), and whether the run must survive a restart. Switching patterns later means rearchitecting the execution model, not swapping a parameter — decide early.

**WHERE to gate — consequence, not confidence** (Digital Applied escalation-design guide):
- LLM verbal confidence is a bad gate signal: RLHF models are systematically miscalibrated (claimed 90% ≈ 75% real; compounds to ~42% over 3 chained agents). If you use confidence, discount it and pair with trajectory-level calibration signals.
- **Four action-risk tiers**: Tier 1 read-only → fully autonomous, never gate (gating manufactures confirmation fatigue); Tier 2 reversible → autonomous with full logging; Tier 3 external/third-party → staging queue or async review; Tier 4 irreversible (deploys, money movement, data deletion, privilege changes, external comms) → mandatory human approval regardless of confidence.
- **Six in-flight triggers** beyond static tiers: confidence-floor breach (async), risk-tier match (sync for T4), user frustration/sentiment (sync), SLA-breach proximity (sync + priority), irreversibility flag (mandatory sync), anomaly/injection suspicion (sync block + security review). Async for anything queue-tolerant; sync only where proceeding is unrecoverable.
- **Enforcement locus rule**: approval requirements live in the workflow DEFINITION, never negotiated by the agent at runtime — otherwise prompt injection can talk the agent out of asking. Gates fire on what the action IS, not what the model inferred.
- **Confirmation fatigue is a security vulnerability, not just UX**: over-gating trains reviewers to rubber-stamp, which turns the Tier-4 approval that matters into a reflexive clickthrough — the strongest argument for risk-tiering and for keeping Tier 1–2 ungated.
- A well-calibrated agent's own check-in rate should RISE with task difficulty (Anthropic observed Claude's self-check-in rate roughly doubling on complex tasks) — design the handoff layer to reward self-escalation rather than suppress it.

**HOW to gate in production — async-first with durability:**
- Synchronous blocking fails on real infrastructure: gateway timeouts (~29s API Gateway), OAuth token expiry mid-wait (30 min–2 h), stale pagination cursors/snapshots.
- Correct pattern: serialize state to a checkpoint, enqueue the approval with a TTL (practitioner defaults: 7 days ordinary, 24 h sensitive, 30 min before kill-switch escalation in one open protocol), resume from checkpoint on decision.
- Two safeguards make async correct: (a) generate an **idempotency key before interrupting** and persist it in state so a resumed action executes exactly once; (b) **hash the proposed action at interrupt time and re-verify at execution time** — if the world drifted while approval was pending, refuse to execute the stale decision.
- **The handoff context package** determines gate quality: plain-language action description, agent's reasoning, impact estimate, reversibility flag, alternatives considered, session ID, approval deadline; render diffs not raw payloads; offer "reject with edits," not just binary yes/no. Condensed decision-ready summaries (~1–2K tokens), never full traces (context-rot argument).
- Governance overlay: CSA/NIST four autonomy tiers (supervised → constrained → monitored → full autonomy) scale oversight cadence with granted autonomy; EU AI Act Art. 14 (high-risk obligations effective Aug 2026) legally mandates intervene/stop/override paths; OWASP names "Excessive Agency" as the risk class — every gate is also a security boundary against injection-driven privilege escalation.

### 3. Inter-pipeline contracts — how pipelines compose

**Composition primitive set** (Augment guide): every multi-agent system reduces to four primitives — decomposition (task graph), routing (structural: which agent; conditional: which branch, e.g., LangGraph conditional edges — routing itself is cheap, <50 ms vs. 2–15 s per LLM call), state (typed shared schema), recovery (detect/retry/re-plan/escalate).

**Five state-sharing patterns with tradeoffs:**
| Pattern | Token cost | Coherence mechanism |
|---|---|---|
| Blackboard/shared memory | High (~2x RAG) | Broadcast + self-selection (13–57% task-success gains over RAG in cited studies) |
| Graph-based message passing | Low (pull-only) | Declared dependency edges; downstream pulls only what it needs |
| Living specifications | Minimal (external file) | Durable artifact survives context replacement; source of truth across sessions |
| Hierarchical summarization | Medium | Structured condensed handoffs |
| Event-driven delta delivery | Low | Only new-since-last-invocation info |

**Contract mechanisms at seams:**
- **Schema validation gates between agents** — output must match the expected structure before passing downstream; this is the primary defense against error cascading (upstream hallucinated values consumed as valid inputs and amplified per hop).
- **File-based communication contracts** (Anthropic guidance) — one agent writes a file, another reads and responds; progress files + git history as handoff mechanism for fresh-context resumption.
- **Boolean exit gates with explicit success criteria in shared state** — a phase cannot declare completion until e.g. `tests_passed == true` is written by the harness, not self-assessed by the generating agent. Enforcement lives at the system/harness level.
- **Typed graph state** (LangGraph `StateGraph`) — fields like `full_plan` (carries the decomposed plan) and `next` (drives routing) make composition inspectable; typed schemas prevent runtime state-manipulation errors.
- **Turn/iteration budgets** (`RemainingSteps`) — agents inspect remaining budget and gracefully summarize-and-hand-off rather than hard-crash; paired with inter-phase exit gates this prevents infinite loops.
- **Local graph repair before global replan** (GraSP): Rebind, InsertPrereq, Substitute (preserving downstream interfaces), Rewire, Bypass — escalate to global replanning only when local repair fails. Notable: "Substitute while preserving downstream interfaces" is exactly an interface-contract notion between pipeline stages.
- **Verifier independence** — reviewing agent ≠ testing agent ≠ generating agent, because verifiers exhibit agreement bias with prior outputs.

**Failure-mode → contract mapping** (condensed from Augment):
error cascading → schema gates at handoffs; infinite loops → turn caps + boolean exit gates; context drift → living spec as correctness anchor; verifier false passes → independent dual verification; parallel write conflicts → isolated worktrees / one-writer-per-module; vague handoff conditions → explicit success criteria in a state file.

### Relevance to archwright (analyst note, not from sources)

Archwright already implements most of the strong patterns: ADR 0007 (gates only where human input is needed = the anti-confirmation-fatigue position), validation gates between phases (= schema gates at seams), span digests (= condensed handoff context packages), ★★ hard-block floor (≈ Tier 4 irreversible), design/ artifacts as living specs, and the research-before-escalate gate (ADR 0010) matches "arrive with decision-ready context." External ideas potentially worth adopting: (a) the explicit reversibility/blast-radius vocabulary for classifying ★★ escalations (tier the hard floor by consequence, which ADR 0010's "irreversible, security-material-and-novel" already gestures at); (b) idempotency + action-hash-on-resume if archwright ever gains long-lived async approvals; (c) the finding that self-escalation rate rising with difficulty is a health signal — could inform evidence-ledger interpretation.

## Sources

- [L4:established] DZone — "How Agent Frameworks Solve Human-in-the-Loop" (Ninaad Rao, Jun 2026) — three HITL patterns (durable graph interrupt / message-loop injection / blocking gate), framework comparison table with code. https://dzone.com/articles/agent-frameworks-human-loop
- [L5:reported] Digital Applied — "Human-in-the-Loop Escalation Design for AI Agents" (Jun 2026) — calibration math, 4-tier action risk, 6-trigger matrix, async-first infrastructure argument, confirmation fatigue as security risk, context-package spec. (Vendor blog; itself flags several figures as secondary — e.g., the 88% pilot-failure rate and 90%→75% calibration gap should be traced to primaries before quoting.) https://www.digitalapplied.com/blog/human-in-the-loop-escalation-design-ai-agents-2026
- [L5:established] Augment Code — "Multi-Agent Orchestration: A Practical Architecture Without the Buzzwords" (May 2026) — four primitives, topology comparison, five state patterns, failure→recovery table; cites Anthropic engineering posts, MAST failure taxonomy (arXiv), AdaptOrch benchmark, GraSP paper. https://www.augmentcode.com/guides/multi-agent-orchestration-architecture-guide
- [L4:reported] arXiv 2512.08769 — "A Practical Guide for Designing, Developing, and Deploying Production-Grade Agentic AI Workflows" (abstract only read). https://arxiv.org/abs/2512.08769
- [L5:reported] jetthoughts — "Mastering LangGraph" — LangGraph as state-machine port for agent orchestration; node caching, deferred nodes (map-reduce), pre/post hooks, consensus (snippet only). https://jetthoughts.com/blog/langgraph-workflows-state-machines-ai-agents/
- [L5:reported] groovyweb — five orchestration patterns taxonomy: sequential, parallel, hierarchical, state-graph, swarm (snippet only). https://www.groovyweb.co/blog/multi-agent-orchestration-patterns-supervisor-router-pipeline-swarm-2026
- [L4:reported] Cloudflare Agents docs — HITL at three layers: MCP-server request, durable Workflow hold, connector-call approval (snippet only). https://developers.cloudflare.com/agents/concepts/agentic-patterns/human-in-the-loop/
- Referenced-via-Augment primaries (not independently read): Anthropic "How we built our multi-agent research system" (15x token figure); Anthropic "Effective harnesses for long-running agents" (context resets, progress files); MAST failure taxonomy arXiv (36.94% coordination failures); GraSP graph-repair primitives; AdaptOrch benchmark.

## Open Questions

1. **Primary-source verification needed**: the 90%→75% confidence miscalibration figure and the 88% pilot-failure rate both circulate through secondary sources; the Digital Applied piece itself flags them. Trace to primaries (TianPan.co calibration analysis; the "88% framework" origin) before load-bearing use.
2. **Adaptive vs. static decomposition**: AdaptOrch shows per-task topology selection beats fixed topologies, but all archwright-style pipelines (and most production systems) use static phase sequences. When does a fixed pipeline with flow-through gates beat adaptive re-planning, and is the answer just auditability?
3. **Edit-at-the-gate**: only LangGraph/deepagents support human EDIT of a pending action (vs approve/reject). Is "reject with edits" worth the state-model complexity for design-pipeline gates where the human's edit IS the decision (cf. archwright resolve)?
4. **Cross-pipeline (not intra-pipeline) contracts**: the literature covers agent-to-agent handoffs within one orchestrated run well, but says little about contracts between separately-owned pipelines that compose at the artifact level (pipeline A's output repo consumed by pipeline B weeks later). Living-spec + schema-validation generalizes, but versioning/compat rules for such seams appear under-documented.
5. **Calibration of self-escalation**: Anthropic's observation (check-in rate doubling with difficulty) suggests a measurable health metric for agent pipelines — is anyone publishing thresholds or dashboards for "agent asks too little/too much"?
6. **HITL gate placement for design pipelines specifically**: all sources address action-execution gates (tool calls, deploys). Gates for judgment artifacts (a design decision, a pattern document) have different reversibility semantics — a wrong pattern is reversible in code but expensive in propagated downstream work. No source addresses this directly.
