# Game Domain — Research Sources

When running `archwright-formalize` Step 4 (prior art research) against a game project, use these domain-specific source categories.

## Source Categories

| Category | Search Pattern | Confidence | Example |
|----------|---------------|-----------|---------|
| **GDC postmortem** | `GDC {concept} postmortem` or `{game} GDC talk` | High (L4 authoritative) | "Hades narrative GDC Kasavin" |
| **Design analysis** | `{game_name} {system} analysis` | Medium (L5-6 informed) | "Disco Elysium skill system analysis" |
| **Academic (FDG/DiGRA)** | `site:fdg-workshop.org OR site:digra.org {concept}` | High (L4 authoritative) | "softlock detection formal methods FDG" |
| **Community deep-dive** | `{game} {system} reddit OR gamedeveloper.com` | Low (L6 community) | "Returnal house sequence design reddit" |
| **Documented failure** | `{system} removed OR deprecated OR backlash game` | High for warnings | "FFXIV cross-class removed", "DD2 fast travel backlash" |
| **Developer blog** | `{studio} blog {system}` | Medium (L5 informed) | "Supergiant narrative design blog" |

## Key Venues

- **GDC Vault** (gdcvault.com) — Conference talks, often free after 1 year
- **Game Developer** (gamedeveloper.com, formerly Gamasutra) — Postmortems, analysis
- **FDG** (fdg-workshop.org) — Foundations of Digital Games (academic)
- **DiGRA** (digra.org) — Digital Games Research Association (academic)
- **Game Studies** (gamestudies.org) — Peer-reviewed journal
- **Mechanics of Magic** (mechanicsofmagic.com) — Systems analysis blog
- **PulseGeek** (pulsegeek.com) — Technical game design articles

## Anti-Pattern Search Templates

Always search for WARNINGS before recommending (G2 gate):

```
"{system} problems game design"
"{game} {feature} criticism OR backlash"
"{pattern} removed OR deprecated game"
"{studio} cut OR scrapped {feature}"
```

## Game-Specific Confidence Mapping

| Source type | Archwright confidence |
|-------------|---------------------|
| GDC talk by lead designer + shipped game demonstrates it | ★★ |
| Multiple shipped games use the same pattern independently | ★★ |
| One shipped game demonstrates it (no second source) | ★ |
| Academic paper proposes it (not validated in shipped game) | ★ |
| Community consensus without official confirmation | — |
| Single reddit post or fan analysis | — (flag "unconfirmed") |

## Domain Predicates (reusable across game projects)

See `predicates.yaml` in this directory for the game-specific predicate library.
