---
id: "095"
title: "Adopt Agent Plugins standard — add plugin.json and SKILL_MANIFEST.yaml to existing skills"
status: open
blocked_by: []
---

# Adopt Agent Plugins Standard

## Context

crew-research is formalizing a skill import protocol (crew-research ticket 98) that adds
version checking, staleness detection, and auto-deploy to the existing known-tools pattern.
archwright already has `skills/` + `tools/deploy-skills.sh` — this ticket adds the two
manifest files to make it fully compliant with both Agent Plugins 1.0 (portable discovery)
and the crew-research lifecycle contract (version/freshness/compat).

## References to clone and review

```bash
# Agent Plugins spec
gh repo clone agentplugins/agent-plugins-spec ~/code/refs/agent-plugins-spec

# Agent Plugins example
gh repo clone agentplugins/agent-plugins-example ~/code/refs/agent-plugins-example

# crew-research protocol design
# ~/code/crew-research/.tickets/98-skill-import-protocol.md
# ~/code/crew-research/.scratch/research/agent-plugins-spec.md
# ~/code/crew-research/.references/agent-plugins-spec/
```

**Key docs:**
- Agent Plugins spec: https://agent-plugins.org/
- Agent Skills format: https://agentskills.io/specification
- Agent Plugins GitHub: https://github.com/agentplugins/agent-plugins-spec

## What to build

### 1. Add `plugin.json` at repo root

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "archwright",
  "version": "1.0.0",
  "description": "Force-resolution design methodology — verified architecture pipeline",
  "repository": "https://github.com/smileynet/archwright",
  "license": "MIT",
  "keywords": ["architecture", "design", "forces", "patterns", "specs"]
}
```

### 2. Add `SKILL_MANIFEST.yaml`

```yaml
name: archwright
version: "1.0.0"
compatibility:
  crew_research: "~> 0.9"
binary: null  # archwright has no binary — it's skills + tools
skills:
  - name: archwright-survey
    path: skills/archwright-survey
  - name: archwright-forces
    path: skills/archwright-forces
  # ... all 16 archwright-* skills
deploy:
  method: symlink
  auto: true
  script: "tools/deploy-skills.sh"
```

### 3. Validate naming compliance

Agent Plugins requires: lowercase, 1-64 chars, `[a-z0-9.-]`, no `--` or `..`.
Current skill names (`archwright-survey`, `archwright-forces`, etc.) should already
comply — verify all 16.

### 4. Validate path containment

Ensure all `references/` paths resolve within skill directories. The deploy script
copies domains/stacks/glossary INTO `archwright-survey/references/` — verify these
don't escape the plugin root boundary.

## Acceptance criteria

- [ ] `plugin.json` present and passes Agent Plugins JSON Schema
- [ ] `SKILL_MANIFEST.yaml` present listing all 16 skills
- [ ] All skill directory names pass Agent Plugins naming rules
- [ ] No path containment violations (references resolve within plugin root)
- [ ] Existing `deploy-skills.sh` still works unchanged
- [ ] crew-research `doctor.sh` detects the manifest (once crew ticket 98 ships)

## What's already done

- `skills/` directory with 16 skills ✅
- `tools/deploy-skills.sh` with multi-tool support ✅
- Symlink deployment to ~/.kiro/skills/ ✅
- Ownership manifest for steering (.archwright-deployed) ✅
- known-tools.yaml registration in crew-research ✅
