# Deploy Target Conventions (B10 evidence)

**Date:** 2026-07-17 · **Method:** local binary/dir inspection (L1) + official docs via 3 research subagents (L4) — full findings in `.scratch/research/{claude-code,codex,agy}-conventions.md` (ephemeral; key facts preserved here).

## Verified conventions

| Tool | Skills (global) | Skills (project) | Steering / always-on rules | Source |
|------|-----------------|------------------|----------------------------|--------|
| kiro | `~/.kiro/skills/` | `<p>/.kiro/skills/` | `~/.kiro/steering/*.md` | L1: live install |
| claude code | `~/.claude/skills/<name>/SKILL.md` | `<p>/.claude/skills/` (discovered up to repo root; nested monorepo skills supported) | `~/.claude/rules/*.md` (project: `.claude/rules/**/*.md`); CLAUDE.md hierarchy for instructions | L4: code.claude.com docs; L1: `~/.claude/{agents,rules}` present locally |
| codex CLI | `~/.agents/skills/` — **NOT** `~/.codex/skills` | `<p>/.agents/skills/` (and every dir up to repo root) | none — global `~/.codex/AGENTS.md` (override: `AGENTS.override.md`); custom prompts deprecated in favor of skills | L4: developers.openai.com/codex; L1: `~/.codex/` has config.toml only, no skills dir |
| agy | none — plugins only (`agy plugin install <github-url>` → `~/.gemini/antigravity-cli/plugins/`) | `<p>/.agents/skills/` (agent-skills standard, `npx skills add`) | none verified — plugin-bundled "rules" (on-disk format unverified) | L4: web research; L1: no `~/.agy` or `~/.config/agy` on this machine |

## Load-bearing facts

1. **All four tools consume the open agent-skills standard** (SKILL.md, name+description frontmatter, progressive disclosure — agentskills.io). Claude Code docs state compliance explicitly; codex builds on it natively; agy uses the same format. Our skills deploy unmodified everywhere. Extra frontmatter fields are the interop risk (open question — untested on codex).
2. **Codex's user-level skills live at `~/.agents/skills`**, not under `~/.codex/`. Community repos referencing `.codex/skills/` are unofficial/legacy — do not target it.
3. **Steering is kiro/claude-native only.** codex/agy have no always-on rules dir; their mechanism is AGENTS.md (codex) or plugin rules (agy). Deploy SKIPs with reason + prints wiring guidance; it never edits a user's AGENTS.md (Extension Protocol rule 1: gaps are pending-with-reason, never silent — and mutating a user-owned file crosses the tools-write-tool-owned-files principle, ADR 0009).
4. **agy has no global copy target at all** — global capability is plugin-install only. `--tool agy` without `--project` exits 2 with the per-project instruction.

## Verified behavior (2026-07-17, all 6 modes)

- kiro global: unchanged output, steering symlink guard intact
- claude `--project`: skills → `.claude/skills/` (13), steering → `.claude/rules/` (2)
- codex `--project`: skills → `.agents/skills/` (13), steering SKIP line with guidance
- agy global: exit 2 + per-project instruction; agy `--project`: skills → `.agents/skills/`, steering SKIP
- unknown tool: exit 2

## Open questions (carried, non-blocking)

- Codex tolerance of non-standard SKILL.md frontmatter fields (test on first real codex deploy)
- agy plugin "rules" on-disk format (needed only if we ever bundle steering as an agy plugin)
- Whether agy reads repo AGENTS.md natively
