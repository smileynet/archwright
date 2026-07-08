# Validation Spike Results: V2 and V5

## V2: Does scope 3 catch 90% of bugs?

### Result: PARTIALLY DISPROVED — trace length matters more than scope for game models.

**Test:** 4 known bugs in a game-domain Alloy model, checked at different scopes and step counts.

| Bug | Scope 2, 6 steps | Scope 3, 6 steps | Scope 2, 10 steps | Scope 3, 10 steps |
|-----|:---:|:---:|:---:|:---:|
| Dead-end (trap) | ✅ | ✅ | ✅ | ✅ |
| Free power | ✅ | ✅ | ✅ | ✅ |
| Gold overflow | ❌ | ❌ | ✅ | ✅ |
| Resurrection | ❌ | ❌ | ✅ | ✅ |
| **Found** | **2/4 (50%)** | **2/4 (50%)** | **4/4 (100%)** | **4/4 (100%)** |

**Key finding:** The small scope hypothesis conflates *scope* (atom count) with *trace length* (steps). For game-domain models with temporal behavior:
- **Scope barely matters** — even scope 2 finds everything with enough steps
- **Trace length is the bottleneck** — bugs 3 and 4 need 7+ steps to manifest (accumulate damage, then trigger)
- 6 steps catches 50%. 10 steps catches 100%.

Jackson's hypothesis is about *structural* complexity (how many objects). Game systems have *temporal* complexity (sequences of events). The hypothesis may hold for relational models but is **misleading for behavioral/temporal models**.

**Impact on archwright:** Default checking should prioritize sufficient **step count** over scope. For game behavior specs: use `steps = max(10, states × 3)` as default. The "scope 3 catches 90%" claim should not be repeated.

### Supporting evidence: Penguin Clash paper (Rezin et al., 2017)
A real multiplayer game (Penguin Clash) modeled in NuSMV:
- Full model: ~10^72 states — **completely intractable**
- Reduced model: ~10^9 states — took **2.5 hours** to verify
- Even reduced, required significant manual model reduction
- Properties verified: reachability (EF), safety (AG), collision (AG EF)

This contradicts our "94ms counterexample" narrative — that only works for toy-sized models. Real games hit state explosion. Our 5-state models are NOT representative of production game complexity.

---

## V5: Does a unified game failure ontology already exist?

### Result: PARTIALLY CONFIRMED — individual terms exist, no unified checkable ontology, but PRIOR ART EXISTS for softlock detection specifically.

**Critical finding:** Mawhorter & Smith (FDG 2021) "Softlock Detection for Super Metroid with Computation Tree Logic" — this paper DOES exactly what archwright proposes for one failure mode:
- Formalizes softlock as CTL: `AG(EF(goal))` — from every reachable state, the goal remains reachable
- Builds a tile-based game abstraction as a Kripke structure
- Uses off-the-shelf model checking (pyModelChecking)
- Finds softlocks, generates counterexample traces, visualizes them
- Detects NON-OBVIOUS softlocks caused by interaction between distant level changes
- Performance: 3645 states checked in ~7 seconds (unoptimized Python)
- Explicitly discusses LIMITATIONS: state explosion with many items, full game world out of reach

**What this means for archwright:**
1. We are NOT the first to apply CTL model checking to game design failure detection. Prior art exists (2021).
2. The softlock detection formula `AG(EF(goal))` is published and validated.
3. State explosion is a REAL problem even the authors acknowledge — not just theoretical.
4. Their approach is level-design focused (spatial); archwright's is system-design focused (behavioral). Different scope but same technique.
5. Their counterexample visualization (trace with arrows showing how the player gets stuck) is analogous to our contrast pairs.

**Other prior art found:**
- Rezin et al. (2017) "Model Checking in multiplayer games development" — NuSMV + game Kripke structure + NFA model. Same fundamental approach. Hit state explosion.
- K-Machinations (Springer 2024) — testing and repairing Machinations diagrams (formal game economy models). Different angle (flow/resource) but formal verification applied to games.

**What's STILL a gap (confirmed):**
- No unified ontology connecting softlock + death spiral + degenerate strategy + others into one checkable framework
- Mawhorter focuses on ONE property (softlock = `AG(EF(goal))`). Archwright proposes a LIBRARY of properties.
- No published work provides the PROVENANCE model (trace violations back to design forces)
- No published work connects formal verification to Alexander's force-resolution methodology

**Impact on archwright:**
- Cite Mawhorter & Smith 2021 as direct prior art
- Adopt their `AG(EF(goal))` formulation for the softlock predicate
- Be honest about state explosion: archwright works for ABSTRACTED models, not full game simulations
- The gap we fill is: unified library + provenance + force-resolution methodology. Not "formal methods applied to games" (that exists).

---

## Summary: What Changes

| Claim | Status | Correction |
|-------|--------|-----------|
| "Scope 3 catches 90%" | **Wrong for games** | Trace length matters more. Use steps = states × 3. |
| "94ms checking" | **Only for toy models** | Real games hit state explosion. Be explicit about abstraction requirements. |
| "No prior art for formal game failure detection" | **Wrong** | Mawhorter 2021, Rezin 2017 exist. Cite them. |
| "Archwright fills the gap" | **Partially correct** | The gap is the UNIFIED library + provenance + methodology, not "formal methods for games." |
| "Contrast pairs are novel" | **Less novel than claimed** | Mawhorter's counterexample traces serve a similar role (showing the path to failure). |
