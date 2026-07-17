# Conformance Gating: How Ecosystems Gate Acceptance of Adapters/Plugins

Research date: 2026-07-17
Question: How do ecosystems gate acceptance of new adapters/plugins/implementations via conformance testing?

## Summary

Four mature ecosystems use four distinct gating models, forming a spectrum from hard certification to soft transparency. Kubernetes (CNCF) gates via a **self-run, centrally-reviewed certification** — vendors run an identical open-source test suite and submit machine-readable results as a PR; certification is annual and trademark-enforced. Java/Jakarta TCKs gate via a **required test kit that ships with the spec** — an implementation isn't "compliant" until it passes the TCK, with tests explicitly classified as required/optional/stochastic/untested per spec rule. OpenTelemetry uses **no gate at all** — a hand-maintained compliance matrix per language SDK, where compliance is defined by RFC 2119 language (all MUSTs satisfied) but self-reported. Tree-sitter grammars gate via **corpus tests as convention** — golden-file tests (input → expected syntax tree) that serve as both API documentation and regression suite, with no central certification body.

The common pattern: (1) a spec expressed as enumerable rules, (2) a test suite that maps 1:1 to rules (or a matrix that does), (3) an explicit taxonomy for what's required vs. optional vs. unverifiable, and (4) a submission/review mechanism whose strictness scales with the trademark/brand value being protected.

## Details

### 1. Kubernetes Certified Conformance (CNCF) — hard gate, self-run, centrally reviewed

**What's required before a distribution counts as "Certified Kubernetes":**
- Pass 100% of the e2e tests tagged `[Conformance]` in the kubernetes e2e suite. A valid certification run may not skip any conformance test (`--mode=certified-conformance` is mandatory; `E2E_FOCUS=[Conformance]` with no skips).
- Submit a PR to `cncf/k8s-conformance` containing exactly: `README.md` (reproduction instructions), `e2e.log` (test log), `junit_01.xml` (machine-readable results), and `PRODUCT.yaml` (vendor metadata: legal entity, product name/version, type = distribution | hosted platform | installer, contacts).
- The submitting vendor must have a signed participation form on file with CNCF (free for community/non-profit distributions, but a named contact is required in case the product falls out of compliance).
- Only the current release version and two prior versions qualify; **recertification is required annually** to keep the mark.

**How tests are structured:** conformance tests are a tagged subset of the upstream e2e suite, owned by the community — SIG Architecture controls what "Certified Kubernetes" means, Testing SIG owns test mechanics, and the Conformance WG owns program process/policy. Requirements evolve per Kubernetes version.

**Who runs them:** the **vendor** runs the identical open-source tooling (Sonobuoy or Hydrophone) against their own cluster; **CNCF reviews** the submitted results (a 15-point mechanical checklist: all required tests present in junit_01.xml, zero failures in e2e.log, correct file structure, one product per PR, one commit, valid PRODUCT.yaml, etc.). Confirmability is a design goal: any end user can re-run the same suite to verify a vendor's claim.

**Reward/enforcement:** trademark license — only certified products may use the Certified Kubernetes mark and version-styled logo.

### 2. Java / Jakarta TCK (Technology Compatibility Kit) — hard gate, required artifact of the spec

**What's required before an implementation counts as compatible:**
- A TCK is one of the **three mandatory deliverables of any JSR** (spec document, reference implementation, TCK). An implementation is "certified compatible" only after passing the TCK, which verifies conformance to both the spec and the reference implementation's behavior.
- Implementations are required to cover the parts of the spec they implement — e.g., in the Reactive Streams TCK, a library implementing only `Subscriber`s need not run `Publisher` verifications, but must run the verifications for what it does ship.

**How tests are structured (Reactive Streams TCK as a concrete, well-documented example):**
- Test classes to be **extended by the implementer**, who provides their implementation via factory methods (`createPublisher`, `createSubscriber`, `createElement`, ...). The TCK harness drives the tests.
- Naming convention `TYPE_spec###_DESC` maps each test to a numbered spec rule, with an explicit verifiability taxonomy:
  - `required_` — covers MUST / MUST NOT rules (hard requirement)
  - `optional_` — covers MAY / SHOULD rules, or tests needing extra configuration
  - `stochastic_` — rule is infeasible to verify deterministically; can yield false positives
  - `untested_` — rule cannot be automated (shows as SKIPPED; PRs to fix welcome)
- The TCK explicitly acknowledges it **cannot fully verify** an implementation — some spec rules aren't automatable — but claims to validate the most important ones.
- Capability declarations let restricted implementations participate honestly: e.g., `maxElementsFromPublisher()` tells the TCK a Publisher can only emit N elements, and tests requiring more are skipped rather than failed. Whitebox vs. blackbox verification tiers trade implementation effort for verification depth (whitebox strongly recommended).

**Who runs them:** the implementer, in their own test suite (TCK shipped as a Maven test-scope dependency). For formal Java/Jakarta certification, results feed into the spec process; for community specs like Reactive Streams, passing the TCK is the community-recognized bar for calling yourself an implementation.

### 3. OpenTelemetry — no gate; transparency via a spec compliance matrix

**What's required before an SDK counts as compliant:**
- Definition only, no certification: "An implementation is compliant if it satisfies all the MUST, MUST NOT, REQUIRED requirements defined in the specification" (RFC 2119 language). Failing any single MUST = non-compliant.
- In practice, language SDKs are official OpenTelemetry projects with their own maintainer teams; third-party implementations live in a registry as "unofficial."

**How the matrix is structured:**
- `spec-compliance-matrix.md` in the specification repo: one row per spec feature (grouped by signal: Traces, Metrics, Logs, Baggage, Resource, Context Propagation, Environment Variables, Exporters...), one column per language (Go, Java, JS, Python, Ruby, Erlang, PHP, Rust, C++, .NET, Swift, Kotlin).
- Cell values: `+` supported, `-` not supported, `N/A` not applicable to that language, **blank = status unknown** — the matrix is honest about its own gaps.
- An `Optional` column marks which features are optional (`X`), required (blank), or "at least one of a family required" (`*`, e.g., you must implement at least one OTLP transport format).
- Feature rows link back to the exact spec section they represent — the matrix is the traceability layer between spec text and implementations.

**Who maintains it:** SDK maintainers and contributors update the matrix by hand via PRs to the spec repo. There is no test harness enforcing it and no central body verifying claims — status is self-reported and versioned with the spec (substantive spec changes go through the OTEP process).

### 4. Tree-sitter grammar corpus tests — convention gate, golden-file style

**What's required before a grammar counts as supported:**
- No central certification. The ecosystem convention (enforced socially and by downstream consumers like Neovim, Helix, Emacs, GitHub) is a comprehensive `test/corpus/` directory: "For each rule that you add to the grammar, you should first create a test that describes how the syntax trees should look when parsing that rule."
- Recommendation is exhaustive coverage: every visible node type should appear in a corpus test, ideally all permutations of each construct.

**How tests are structured (golden-file format):**
- Plain text files in `test/corpus/`; each entry is: test name between `===` lines → input source code → `---` divider → expected syntax tree as an S-expression (named nodes only; anonymous tokens omitted; field names optional).
- Header attributes extend the format: `:error` (assert the input must produce a parse error — negative tests), `:skip`, `:fail-fast`, `:language(LANG)` (multi-grammar repos), `:platform(...)`, `:cst`.
- Escape hatches for separator collisions (custom suffixes, longer `---` dividers) keep the format usable for any language.
- `tree-sitter test` runs the whole corpus; `tree-sitter test -u` regenerates expected trees from current parser output (explicit golden-update workflow).
- Corpus tests are described as serving double duty: **regression suite and the parser's API documentation** — readers learn the grammar's node vocabulary by reading tests.
- In-the-wild practice adds a second tier: parsing a large real-world code corpus (e.g., tree-sitter-d validated against Weka's entire D codebase) as a smoke/soak test beyond the curated corpus.

**Who runs them:** the grammar author, locally and in CI. Downstream integrators (editors) apply their own acceptance judgment — corpus quality is a de facto admission signal, not a formal one.

### Cross-cutting patterns

1. **Rule enumeration precedes testing.** Every ecosystem first makes the spec enumerable (numbered rules, tagged tests, feature rows, grammar rules), then attaches verification per rule. The test-to-rule traceability link (`required_spec101_...`, `[Conformance]` tag, matrix row → spec anchor) is the load-bearing artifact.
2. **Explicit verifiability taxonomy.** Mature programs admit what they can't check: TCK's `stochastic_`/`untested_`, OTel's blank cells, K8s's "conformance subset" of e2e. Claiming full verification is avoided.
3. **Required vs. optional is first-class metadata**, not prose: TCK prefixes, OTel's Optional column (including "at least one of family" semantics), K8s's no-skips rule.
4. **Who-runs vs. who-verifies split.** Self-run + central review of machine-readable evidence (K8s: junit XML + logs in a PR) scales better than central execution. The stricter the brand value (trademark), the more mechanical the review checklist.
5. **Capability declaration beats binary pass/fail.** The TCK's `maxElementsFromPublisher()` pattern lets constrained implementations be honestly partially-conformant with tests skipped rather than failed — the gate adapts to declared capabilities.
6. **Golden files + update command** (tree-sitter) is the lightest-weight gate: cheap to author, doubles as documentation, and regeneration (`test -u`) makes intentional behavior changes explicit diffs.
7. **Recertification cadence** matters when the spec evolves: K8s requires annual recert against current/previous version; OTel's matrix rows grow with the spec and cells go stale (visible as blanks).

## Sources

- [L4:verified] CNCF k8s-conformance instructions (submission process, PRODUCT.yaml, 15-point review checklist): https://github.com/cncf/k8s-conformance/blob/master/instructions.md
- [L4:established] CNCF Certified Kubernetes program (confirmability principle, Sonobuoy): https://www.cncf.io/certification/software-conformance
- [L4:established] CNCF k8s-conformance FAQ (participation form, free for community distros): https://github.com/cncf/k8s-conformance/blob/master/faq.md
- [L4:established] Kubernetes blog "Introducing Software Certification for Kubernetes" (SIG Architecture ownership, annual recertification, trademark rule): https://v1-35.docs.kubernetes.io/blog/2017/10/Software-Conformance-Certification/
- [L4:verified] Reactive Streams TCK README v1.0.1 (test taxonomy, naming convention, capability declarations, whitebox/blackbox): https://github.com/reactive-streams/reactive-streams-jvm/blob/v1.0.1/tck/README.md
- [L4:established] Oracle JavaTest intro — TCK definition (certify conformance to spec + reference implementation): https://docs.oracle.com/javame/test-tools/javatest-45/html/intro.htm
- [L4:established] Hibernate Bean Validation TCK intro (TCK as one of three required JSR pieces): https://docs.hibernate.org/beanvalidation/tck/1.1/reference/html/introduction.html
- [L4:verified] OpenTelemetry spec-compliance-matrix (cell semantics, Optional column, per-language columns): https://github.com/open-telemetry/opentelemetry-specification/blob/main/spec-compliance-matrix.md
- [L4:established] OpenTelemetry Specification README (RFC 2119 compliance definition): https://opentelemetry.io/docs/specs/otel/
- [L4:verified] Tree-sitter "Writing Tests" docs (corpus format, attributes, `test -u`, comprehensiveness recommendation): https://tree-sitter.github.io/tree-sitter/creating-parsers/5-writing-tests.html
- [L6:reported] tree-sitter-d README (real-world corpus validation practice): https://github.com/gdamore/tree-sitter-d

## Open Questions

1. **Where should archwright sit on the spectrum?** Domain overlays / adapters could gate like tree-sitter (corpus of golden fixtures per predicate, `run-fixture-tests.sh` is already this shape) or like a TCK (harness that adapter authors extend). Which fits the skill+tool architecture?
2. **Verifiability taxonomy for specs.** The TCK's required/optional/stochastic/untested classification maps suggestively onto archwright's confidence tiers (★★/★/—). Should spec checks explicitly declare their verifiability class (static-checkable / trace-checkable / Alloy-checkable / unverifiable-by-tooling)?
3. **Capability declaration for partial adapters.** Should a domain overlay declare which predicates it supports (à la `maxElementsFromPublisher()`) so the check harness skips rather than fails unsupported checks?
4. **Who reviews self-run results?** K8s's model (vendor runs, machine-readable evidence, mechanical review checklist) suggests conformance evidence should be a structured artifact (JSON per the project's validation contract), not a prose claim. Not investigated: how CNCF handles disputed or falsified submissions.
5. **Matrix staleness.** OTel's blank cells show hand-maintained matrices decay. If archwright grows a support matrix (domains × check kinds), can it be generated from fixture-test results instead of hand-edited?
6. **Not researched:** Jakarta EE's formal TCK certification-request process (compatibility certification requests filed as GitHub issues with test results), and whether OTel has any automated cross-language integration test harness (e.g., OTLP interop tests) complementing the matrix.
