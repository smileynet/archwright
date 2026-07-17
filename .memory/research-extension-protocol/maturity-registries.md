# Research: Capability/Maturity Registries and Tiered Support Policies

Date: 2026-07-17
Researcher: maturity-registries (orchestrated session)

## Summary

Four mature open-source ecosystems (Rust targets, Kubernetes feature gates, MDN browser-compat-data, tidyverse/ExecuTorch API lifecycles) converge on the same registry design: **a small number of named tiers (3–4), each defined by verifiable graduation criteria, with explicit demotion paths and a machine-readable registry that separates support data from status data.** The strongest common patterns: (1) tiers are cumulative — each tier inherits all requirements of the tier below; (2) promotion requires demonstrated track record at the current tier, not just meeting the criteria on paper; (3) demotion is a first-class, documented process with communication requirements proportional to the tier; (4) the registry stores *evidence* (versions, dates, flags, notes), not just labels. The anti-pattern literature warns against building the registry/plugin machinery before there are ≥2 concrete entries that need it (YAGNI / premature abstraction).

## Details

### 1. Rust Target Tier Policy — [L4:verified]

Source: https://doc.rust-lang.org/rustc/target-tier-policy.html (fetched full text)

**Tier definitions (guarantee-based, cumulative):**

| Tier | Guarantee | Key requirements |
|------|-----------|------------------|
| Tier 3 | "Exists in codebase, may or may not build" — no guarantees | Named maintainer(s) on record; consistent naming; no legal/license issues; docs on how to build; **must not impose burden on other developers** (no PR-blocking comments); must not break tier 1/2 targets |
| Tier 2 | "Guaranteed to build" — CI checks build, rejects breaking patches | All tier-3 requirements + value to people beyond maintainers; ≥2 designated maintainers; docs for cross-compile + test; documented baseline expectations; core/std fully implemented; builds reliably in CI without excessive CI cost |
| Tier 1 | "Guaranteed to work" — CI builds AND passes tests; official binaries | All tier-2 requirements + substantial widespread community interest; multiple production users across multiple orgs; ≥3 maintainers; full testsuite passes in CI; maintainers provide CI infrastructure if needed |

"Host tools" is an orthogonal capability axis at tiers 1–2 with its own supplementary requirements — a useful pattern: **tier × capability matrix rather than one linear scale**.

**Graduation criteria / promotion rules:**
- Each tier builds on all requirements from the previous tier unless overridden by a stronger requirement.
- A target must have received approval at the lower tier AND "spent a reasonable amount of time" there before proposing promotion — even if it meets higher-tier requirements immediately. Minimum: multiple stable releases between promotions.
- Proposals must **quote the requirements verbatim and respond to each one** — a structured self-assessment artifact.
- Approval authority scales with tier: tier 3 = one compiler-team member; tier 2 = compiler team (MCP) + infra team for CI; tier 1 = full RFC jointly approved by compiler + infra teams.
- RFC 2119 language (must/should/may) is used throughout; policy explicitly states human judgment applies — "targets must fulfill the spirit of the requirements."

**Demotion rules:**
- Tier availability is explicitly NOT a hard stability guarantee ("The availability or tier of a target in stable Rust is not a hard stability guarantee").
- Tier 2 demotion: proposal CCed to target maintainers, communicated widely before dropping from a stable release; teams may temporarily disable targets in nightly to unblock features, with maintainers expected to catch up or face demotion (precedent: u128/i128 introduction).
- Tier 1 demotion: requires full RFC with compiler + infra approval; "highly unlikely to be directly removed without first being demoted to tier 2 or tier 3" — **demotion is stepwise, not cliff-edge**.
- Tier 3 removal: PR CCing maintainers if requirements lapse, maintainers lose interest, or target shows no activity.
- Communication lead time scales with severity, timing of discovery, and whether the target shipped in a stable release.
- Real precedent: 32-bit Apple targets demoted Tier 1 → Tier 3 (2020) when Apple dropped OS support ([L4] https://blog.rust-lang.org/2020/01/03/reducing-support-for-32-bit-apple-targets/).

### 2. Kubernetes Feature Gates (Alpha → Beta → GA) — [L4:verified]

Source: https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/ (fetched full text); KEP 5241 (https://www.kubernetes.dev/resources/keps/5241/)

**Stage definitions:**

| Stage | Default | Guarantees |
|-------|---------|-----------|
| Alpha | Disabled | Might be buggy; support may be dropped at any time without notice; API may change incompatibly without notice; short-lived test clusters only |
| Beta | Usually enabled (but beta *API groups* disabled by default since 1.24) | Well tested; feature won't be dropped, but details/schema may change incompatibly with migration instructions; non-business-critical use recommended |
| GA (stable) | Always on, cannot disable | Gate becomes a locked no-op for a few releases (compat), then removed; appears in released software for many subsequent versions |

**Graduation criteria:**
- Alpha → Beta: defined per-feature in the KEP (Kubernetes Enhancement Proposal); must include functional, security, monitoring, and testing requirements. Beta means "enabled by default with an opt-out flag."
- Beta → GA (per KEP 5241): the **only valid GA criterion is "all issues and gaps identified as feedback during beta are resolved"** — GA is not a new bar, it's closure of beta feedback. This prevents scope creep at graduation time.
- Each KEP must declare its graduation criteria up front — the promotion plan is written when the feature is proposed, not when promotion is requested.

**Registry structure (the feature-gate table itself):**
- Machine-readable rows: `Feature | Default | Stage | Since | Until` — a full **stage history** per feature, not just current state. E.g. `WatchList` shows Alpha 1.27–1.31, Beta on 1.32, Beta *off* 1.33 (a demotion-in-place!), Beta on again 1.34.
- Deprecated is a first-class stage in the same table (e.g. `KMSv1`: Deprecated-on 1.28, Deprecated-off 1.29 — staged wind-down).
- Removed gates move to a separate "feature gates removed" reference page — history is preserved, active registry stays clean.

**Demotion rules:**
- Demotion happens by flipping the default back to false while staying at the same stage (observed: `WatchList` beta default true→false→true; `MaxUnavailableStatefulSet` beta default flipped within patch releases 1.35.0→1.35.4) — **default and stage are independent knobs**.
- Deprecation is a stage, with its own default-flipping sequence before removal.
- Formal deprecation policy governs timelines (https://kubernetes.io/docs/reference/using-api/deprecation-policy/).

### 3. MDN browser-compat-data (BCD) Structure — [L4:verified]

Source: https://github.com/mdn/browser-compat-data/blob/main/schemas/compat-data-schema.md (fetched full text)

**Structure highlights (registry-as-data patterns):**
- Hierarchical feature identifiers (`css.properties.text-align.start`) with unlimited nesting; a node is a *feature* iff it has a `__compat` block. File layout is irrelevant to the export — identity comes from the path, not the file.
- Each `__compat` has two mandatory parts: `support` (per-platform evidence) and `status` (stability flags), plus optional description/mdn_url/spec_url.
- **Support statements are evidence-rich**: `version_added` (string version, `false`, `"preview"`, or ranged `≤37` for "confirmed by this version, may be earlier"), `version_removed`, `prefix`/`alternative_name`, `flags` (required feature flags with type/name/value), `partial_implementation` (must carry an explanatory note), `notes`, `impl_url` (link to tracking bug).
- A support statement can be an **array** — multiple overlapping support eras (prefixed era, renamed era, standard era), sorted most-relevant-first.
- `"mirror"` keyword: derivative browsers inherit upstream data automatically — deduplication for entries that track another entry.
- **Status flags**: `standard_track` (bool — part of an active spec), `deprecated` (bool — no longer recommended), `experimental` (bool — **now deprecated as a field** because it "does not have a precise definition"; MDN recommends "more well-defined stability calculations, such as Baseline, instead"). Lesson: a vague boolean maturity flag decays; prefer derived/computable status.
- `spec_url` is **mandatory when standard_track is true** and must deep-link (fragment identifier) — claims of standardization require a citable anchor.
- Ranged versions (`≤`) are an honest-uncertainty mechanism: allowed only for releases ≥2 years old, discouraged, meant to be replaced by exact data.

### 4. API Maturity Lifecycles (tidyverse, ExecuTorch, Adobe, Kubernetes API versioning) — [L4:established]

Sources: tidyverse lifecycle vignette (https://cran.r-project.org/web/packages/lifecycle/vignettes/stages.html); ExecuTorch API Life Cycle (https://docs.pytorch.org/executorch/0.6/api-life-cycle.html); Adobe deprecation policy (https://developer.adobe.com/express/add-ons/docs/guides/learn/platform-concepts/deprecation-policy)

- **tidyverse** uses 4 stages: experimental → stable, plus two exit paths: **deprecated** (will be removed; scheduled) and **superseded** (a better alternative exists but this stays maintained — a softer demotion that avoids breaking users). The older lifecycle package had 7 stages (experimental, maturing, stable, questioning, soft-deprecated, deprecated, defunct) — it was *simplified* to 4; more stages ≠ better.
- **ExecuTorch**: Experimental APIs "may change or be removed at any time," but with an explicit expectation of eventual promotion to Stable "unless sufficient negative signals have been collected" — experimental is a promotion pipeline, not a dumping ground.
- **Adobe**: Experimental APIs are explicitly **outside** the deprecation lifecycle — no deprecation phase, no warnings, no scheduled removal. Clean separation: lifecycle guarantees begin at stable.
- **Kubernetes API versioning** (v1alpha1/v1beta1/v1): alpha = no backward-compat requirement, removable without notice, non-production only; beta = enabled infrastructure but schema may still change with migration paths; GA = long-horizon stability. Deprecation policy mandates minimum support windows per stage after deprecation announcement.
- Common thread: **the tier label is a contract about change velocity and removal notice**, not a quality judgment.

### 5. Anti-Patterns: Premature Abstraction / Plugin Architecture — [L5:established]

Sources: YAGNI/over-abstraction articles (gazar.dev, hemaks.org, medium.com/weave-lab, ironsoftware.com); Magento plugin-architecture critique (yegorshytikov.medium.com)

- **Rule of two**: "Don't create a base class, interface hierarchy, or plugin system until you have concrete evidence it's needed. Two concrete implementations are usually better than one premature abstraction." (gazar.dev) — for a maturity registry, this means: don't build the registry schema until at least two real entries with different maturity levels exist.
- **Over-abstraction cost**: unnecessary abstractions decrease code quality, raise cyclomatic complexity, and bloat the codebase with adapters/glue (weave-lab Go antipatterns article).
- **Generic-mechanism hazard**: Magento's plugin (AOP) architecture is criticized as "a very generic mechanism for solving some very specific concerns," likened to GOTO for OOP — hooks everywhere make behavior untraceable. Applied to registries: avoid generic "capability provider" interception points; prefer explicit, enumerated capability entries.
- **Counter-caution**: YAGNI can be over-applied — one article warns it gets misused to "avoid deeper engineering conversations altogether. Conversations about boundaries, ownership, data, and failure modes get postponed." (medium.com/@souravray). Deferring the *implementation* is right; deferring the *boundary/ownership conversation* is not.
- Synthesis for archwright: define the tier vocabulary and graduation/demotion rules early (cheap, conversational), but keep the registry as plain data (YAML/Markdown tables like BCD/K8s feature gates) rather than a plugin system, until ≥2 domains actually diverge in what they need.

### Cross-cutting design principles extracted

1. **3–4 tiers max**, defined by the *guarantee* offered, not internal quality (Rust: "may build / builds / works"; K8s: "may vanish / won't vanish but may change / locked").
2. **Cumulative requirements** — each tier = lower tier + delta. Makes audits mechanical.
3. **Promotion needs soak time** at the current tier plus a structured self-assessment quoting criteria verbatim (Rust) or criteria declared at proposal time (K8s KEP).
4. **GA criteria should be nothing more than "beta feedback resolved"** (KEP 5241) — prevents moving goalposts.
5. **Demotion is stepwise, communicated, and evidence-triggered**; default-off is a lighter lever than stage demotion (K8s); "superseded" is a lighter lever than "deprecated" (tidyverse).
6. **Registry rows carry stage history** (Since/Until per stage), not just current state.
7. **Evidence over labels**: version numbers, flags required, partial-implementation notes, tracking-bug links (BCD). Vague booleans (`experimental`) rot and get deprecated.
8. **Approval authority scales with tier** (one reviewer → team → joint RFC).
9. **Orthogonal capability axes** (Rust host tools; BCD per-browser) attach to a tier rather than multiplying tiers.
10. **Don't build registry machinery before two real entries need it** (YAGNI), but do settle the tier vocabulary and ownership boundaries up front.

## Sources

- [L4:verified] Rust Target Tier Policy — https://doc.rust-lang.org/rustc/target-tier-policy.html (full text fetched)
- [L4:verified] Rust Platform Support — https://doc.rust-lang.org/nightly/rustc/platform-support.html
- [L4:reported] Rust blog: Reducing support for 32-bit Apple targets (demotion precedent) — https://blog.rust-lang.org/2020/01/03/reducing-support-for-32-bit-apple-targets/
- [L4:verified] Kubernetes Feature Gates reference (v1.36, incl. feature stages definitions and Since/Until tables) — https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/ (full text fetched)
- [L4:reported] KEP 5241: Beta Feature Gate Promotion Requirements — https://www.kubernetes.dev/resources/keps/5241/
- [L4:reported] Kubernetes Deprecation Policy — https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- [L4:reported] Gateway API versioning (Experimental/Standard channels variant) — https://gateway-api.sigs.k8s.io/docs/concepts/versioning/
- [L4:verified] MDN browser-compat-data JSON schema — https://github.com/mdn/browser-compat-data/blob/main/schemas/compat-data-schema.md (full text fetched)
- [L4:reported] tidyverse lifecycle stages vignette — https://lifecycle.r-lib.org/articles/stages.html (via CRAN mirror snippet)
- [L4:reported] ExecuTorch API Life Cycle and Deprecation Policy — https://docs.pytorch.org/executorch/0.6/api-life-cycle.html
- [L4:reported] Adobe Express Add-ons Deprecation Policy — https://developer.adobe.com/express/add-ons/docs/guides/learn/platform-concepts/deprecation-policy
- [L5:reported] YAGNI / premature abstraction — https://gazar.dev/clean-code/yagni-principle-typescript
- [L5:reported] Dangers of Over-Abstraction — https://hemaks.org/posts/the-dangers-of-over-abstraction-when-yagni-principle-wins/
- [L5:reported] Abstraction Antipatterns in Go — https://medium.com/weave-lab/abstraction-antipatterns-in-go-a85d6703c0e3
- [L5:reported] Magento plugin (AOP) architecture critique — https://yegorshytikov.medium.com/magento-2-plug-ins-aod-architecture-are-harmful-dc23c4edb534
- [L5:reported] YAGNI over-application warning — https://medium.com/@souravray/yagni-you-arent-gonna-nail-it-until-you-do-a47d5fa303dd

## Open Questions

1. **Who owns demotion detection?** Rust relies on CI + maintainer responsiveness; K8s relies on release-team process. For archwright's domain overlays / confidence tiers, what's the automated signal that a ★★ claim no longer holds (equivalent to a target failing CI)?
2. **Soak-time quantification** — Rust says "multiple stable releases" between promotions; K8s ties stages to release cycles. What is the analogous clock for archwright artifacts (checks passed over N commits? N sessions?)?
3. **Superseded vs deprecated** — should archwright's registry adopt tidyverse's "superseded" (kept working, better alternative exists) as distinct from demotion? It fits patterns replaced by re-resolution.
4. **Default vs stage as independent knobs** — K8s can flip a beta feature's default off without demoting it. Is there an archwright analogue (e.g., a ★★ predicate temporarily not enforced without demoting to ★)?
5. **Baseline-style derived status** — MDN deprecated the `experimental` boolean in favor of computed stability (Baseline). Could archwright compute confidence from check history rather than storing a hand-set flag?
6. **How many entries before formalizing?** The YAGNI rule-of-two suggests waiting for 2 divergent domain overlays before generalizing the registry schema — current domain overlays (game/web/general) may already satisfy this.
