# Origin & Lineage

The ancestor is Christopher Alexander, Sara Ishikawa & Murray Silverstein, *A Pattern Language: Towns, Buildings, Construction* (1977) — 253 patterns ordered by scale, region → town → building → room → construction detail.

Four mechanics from that work are the parts we're stealing:

- **Patterns resolve forces.** A pattern is *context → problem → solution*, where the "problem" is a field of competing forces in tension and the "solution" is the configuration that balances them. No real tension ⇒ not a pattern, just a feature.
- **Generative, not templates.** A pattern lets you solve the same problem endlessly without ever solving it the same way twice. It is a rule for *making* form, not a blueprint.
- **A network, not a list.** Patterns link *up* (larger patterns they help complete) and *down* (smaller patterns that complete them). A design is a chosen path through the network; wholeness comes from the linking.
- **A confidence claim.** Alexander rated each pattern with two / one / zero asterisks — his stated confidence that it names a *true invariant* of the problem versus merely one workable arrangement.

## Cautionary tale

This book spawned software design patterns (Gang of Four, 1994; Ward Cunningham's original wiki was a pattern repository) and a games branch (Björk & Holopainen, *Patterns in Game Design*, 2005). Alexander's 1996 OOPSLA keynote essentially warned the software field that it had taken his catalogue and dropped the soul — the forces, and the question of whether the generated thing is actually good to inhabit.

Our system is a deliberate attempt to keep the soul: forces stay first-class and confidence-weighted, all the way down to code.
