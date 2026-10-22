# Validation Spikes: Testing Unconfirmed Claims

These are claims from training data that haven't been grounded in execution or primary sources. Each needs a concrete test that could *disprove* the claim.

---

## V1. Does CEGAR's consistency map to pass-up?

**Claim:** "The consistency requirement (re-abstraction landing within the original counterexample) IS level-terminating pass-up."

**How to disprove:** Find a case where archwright's pass-up routing gives a DIFFERENT answer than CEGAR's consistency check would. If they diverge, the analogy is broken.

**Spike:**
1. Take the ball-possession counterexample (EXTERNAL_UNLOCK bypass from S2)
2. Manually apply CEGAR's consistency algorithm: does re-abstracting the concrete trace (Shallow→Deep) land within the original abstract counterexample? What does "landing within" mean concretely for our spec layer?
3. Compare: does the provenance annotation (`from_pattern: ball-possession`) give the same routing as the CEGAR algorithm would?
4. Try a HARDER case: two patterns contribute to one behavior spec, violation involves elements from both. Does CEGAR's algorithm identify the same responsible element as reading the `from_pattern` annotation?

**Pass criterion:** The two approaches agree on routing for at least 3 test cases.
**Fail criterion:** They disagree, meaning the analogy is superficial or the annotation model is insufficient.

---

## V2. Is scope 3 really 90%?

**Claim:** "Scope 3 catches ~90% of cumulative invalid assertions."

**How to disprove:** Run Alloy on our models at increasing scopes and count how many NEW counterexamples appear at each scope level. If scope 3 misses significant violations that scope 5+ finds, the number is wrong for our domain.

**Spike:**
1. Take the S7 game model (combat/resource with 5 states + integers)
2. Introduce 5 known bugs (different types: dead-end, unreachable state, guard contradiction, temporal violation, integer overflow)
3. Run at scope 2, 3, 4, 5, 6, 7. Record which bugs are found at which scope.
4. Calculate: what % of bugs are found by scope 3? By scope 5?

**Pass criterion:** ≥80% found by scope 3, ≥95% by scope 5.
**Fail criterion:** Significant bugs (especially game-domain ones with integers) require scope 6+.

---

## V3. Is Apalache practical?

**Claim:** "Apalache (symbolic TLA+ checker) may be more practical than TLC for bounded temporal checking."

**How to disprove:** Try to install and run Apalache on our ball-state-lifecycle model (translated to TLA+). Measure: install difficulty, translation effort, performance, output quality.

**Spike:**
1. Install Apalache (check if it actually works on current Java/OS)
2. Translate ball-state-lifecycle to TLA+ (how hard is this? how many lines?)
3. Run the `at-most-one-holder` invariant check
4. Compare: time, output clarity, and counterexample quality vs. our Alloy run

**Pass criterion:** Installs in <10 min, model translates in <30 min, check completes in <30s, output is interpretable.
**Fail criterion:** Installation hell, translation requires deep TLA+ expertise, or performance is worse than Alloy for our model size.

---

## V4. Is SARIF actually adopted?

**Claim:** "SARIF is adopted by GitHub Code Scanning, VS Code, Semgrep, CodeQL."

**How to disprove:** Try to actually upload a SARIF file to GitHub Code Scanning. Does it work? What's the real developer experience?

**Spike:**
1. Generate a minimal SARIF JSON file from an archwright-check violation (manually construct the JSON)
2. Push to a GitHub repo with code scanning enabled
3. Does GitHub render it? Does VS Code's SARIF viewer open it?
4. Try to consume output from `semgrep --sarif` — does the format match what archwright would produce?

**Pass criterion:** GitHub renders violations, VS Code shows locations, format is straightforward to produce.
**Fail criterion:** SARIF is so complex that producing valid output requires a library, or GitHub rejects common valid SARIF, or the format is overkill for our use case.

---

## V5. Are game failure taxonomy gaps real?

**Claim:** "No published work connects softlock, death spiral, degenerate strategy into a unified ontology. Archwright fills this gap."

**How to disprove:** Find a paper or tool that DOES provide this unified ontology. If it exists, we're reinventing.

**Spike:**
1. Search Google Scholar for: "game design failure ontology", "game balance verification formal", "game design pattern verification"
2. Search for Joris Dormans' "Machinations" framework (known formal game balance tool) — does it have a failure taxonomy?
3. Search for "automated game testing formal methods" — any tool that checks game invariants?
4. Check if the Aytemiz & Smith FDG 2020 taxonomy (found by subagent) actually covers our predicates or is orthogonal

**Pass criterion:** No unified ontology found that covers all of softlock + death spiral + degenerate strategy + the others as checkable predicates.
**Fail criterion:** A framework exists (possibly Machinations, possibly academic) that already formalizes these as checkable properties. If so, we should use/extend it rather than invent from scratch.

---

## V6. Is PBT shrinking actually analogous to contrast pairs?

**Claim:** "PBT shrinking is structurally analogous to contrast-pair generation — both seek the minimal configuration distinguishing pass from fail."

**How to disprove:** Try to actually use a PBT shrinker to produce a contrast pair from an archwright violation. If the output isn't useful as a contrast pair, the analogy is surface-level.

**Spike:**
1. Write a fast-check (TypeScript) or Hypothesis (Python) property test for the ball-state-lifecycle model: `property: no sequence of events leads to two holders simultaneously`
2. Introduce the `direct_grab` violation
3. Let the shrinker find the minimal failing case
4. Compare the shrunk counterexample to our Alloy contrast pair from S6
5. Is the shrunk result *actually informative* for pass-up routing? Does it localize the responsible element?

**Pass criterion:** Shrunk counterexample identifies the same responsible transition (direct_grab) and produces a minimal reproduction that a developer could act on.
**Fail criterion:** The shrunk counterexample is minimal but NOT informative for design-level routing (it tells you THAT something broke but not WHICH DESIGN DECISION to revisit).

---

## Priority

| Spike | Risk if wrong | Effort | Priority |
|-------|--------------|--------|----------|
| V2 (scope 90%) | Low — we already use scope 5 | 30 min | Do first (quick, concrete) |
| V5 (taxonomy gap) | Medium — might be reinventing | 30 min (search) | Do second (search-only) |
| V6 (PBT analogy) | Low — nice-to-have, not load-bearing | 1 hr | Do third (code required) |
| V1 (CEGAR mapping) | Medium — if wrong, pass-up model needs revision | 1 hr | Do fourth (manual analysis) |
| V4 (SARIF adoption) | Low — output format is easily changed | 30 min | Defer (not urgent) |
| V3 (Apalache) | Low — Alloy works fine for now | 1-2 hr | Defer (alternative backend) |

V2 and V5 are the highest-signal tests: they're quick and could actually change what we build. V1 is the most architecturally significant but hardest to test concretely.
