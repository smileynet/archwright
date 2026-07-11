#!/usr/bin/env node
/**
 * archwright-check-compile: Generate check blocks from high-level intent declarations.
 *
 * Usage:
 *   archwright-check-compile <intent.yaml> --project-root <path>
 *
 * Input: YAML with check_intent declarations
 * Output: YAML check block ready to paste into a spec
 *
 * Intent patterns supported:
 *   single_writer:  "Only X writes field Y"
 *   no_import:      "A must not import from B"
 *   no_mutation:    "A must not call mutation methods"
 *   no_reference:   "A must not reference B"
 *   must_use:       "A must contain concept X"
 *   no_literal:     "No plaintext X anywhere in scope"
 */

import { readdirSync, statSync, existsSync } from "node:fs";
import { join, relative } from "node:path";

// --- Intent → Check compilation ---

const MUTATION_VERBS = ["save", "store", "persist", "write", "set_meta", "push", "delete", "remove"];

function compile(intent) {
  switch (intent.pattern) {
    case "single_writer":
      return {
        method: "grep",
        target: intent.scope || "src/",
        pattern: `${intent.field}\\\\s*=`,
        expect: "absent",
        exclude: intent.authority,
        description: `Only ${intent.authority} may write ${intent.field}`
      };

    case "no_import":
      return {
        method: "grep",
        target: intent.source,
        pattern: `from.*${intent.forbidden_module}`,
        expect: "absent",
        description: `${intent.source} must not import from ${intent.forbidden_module}`
      };

    case "no_mutation":
      return {
        method: "grep",
        target: intent.actor,
        pattern: `\\\\.(${MUTATION_VERBS.join("|")})\\\\(`,
        expect: "absent",
        description: `${intent.actor} must not call mutation methods`
      };

    case "no_reference":
      return {
        method: "grep",
        target: intent.source,
        pattern: intent.forbidden_names.join("|"),
        expect: "absent",
        description: `${intent.source} must not reference ${intent.forbidden_names.join(", ")}`
      };

    case "must_use":
      return {
        method: "grep",
        target: intent.source,
        pattern: intent.concept,
        expect: "present",
        description: `${intent.source} must reference ${intent.concept}`
      };

    case "no_literal":
      return {
        method: "grep",
        target: intent.scope || "src/",
        pattern: intent.forbidden_patterns.join("|"),
        expect: "absent",
        exclude: intent.exclude || "test",
        description: `No plaintext ${intent.subject} in ${intent.scope || "src/"}`
      };

    default:
      return { error: `Unknown intent pattern: ${intent.pattern}` };
  }
}

// --- Target resolution ---

function resolveTarget(target, projectRoot) {
  const resolved = join(projectRoot, target);
  if (!existsSync(resolved)) {
    return { warning: `Target path not found: ${resolved}. Check project structure.` };
  }
  return null;
}

// --- CLI ---

const args = process.argv.slice(2);
if (args.length < 1) {
  console.error("Usage: archwright-check-compile <intent.yaml> [--project-root <path>]");
  console.error("\nExample intent.yaml:");
  console.error(`  intents:
    - pattern: single_writer
      field: ball_holder
      authority: ball_state_service
      scope: client/src/

    - pattern: no_import
      source: src/control-plane.ts
      forbidden_module: oci-cli

    - pattern: no_mutation
      actor: client/src/setup/

    - pattern: must_use
      source: src/adapters/oci-cli.ts
      concept: ORACLE_APP_ALLOW`);
  process.exit(2);
}

// For now, demonstrate compilation with inline examples
const examples = [
  { pattern: "single_writer", field: "ball_holder", authority: "ball_state_service", scope: "client/src/" },
  { pattern: "no_import", source: "src/control-plane.ts", forbidden_module: "oci-cli" },
  { pattern: "no_mutation", actor: "client/src/setup/" },
  { pattern: "no_reference", source: "client/src/execution/play_manager3d.gd", forbidden_names: ["PlayerFielderController", "AIFielderController"] },
  { pattern: "must_use", source: "src/adapters/oci-cli.ts", concept: "ORACLE_APP_ALLOW" },
  { pattern: "no_literal", subject: "passwords", scope: "src/", forbidden_patterns: ["password.*=.*['\"]", "ADMIN_PASSWORD"], exclude: "test" }
];

console.log("# Generated check blocks from intent patterns\n");
for (const intent of examples) {
  const check = compile(intent);
  console.log(`# Intent: ${intent.pattern}`);
  console.log(`# ${check.description || check.error}`);
  console.log("check:");
  for (const [key, value] of Object.entries(check)) {
    if (key === "description") continue;
    if (key === "error") { console.log(`  # ERROR: ${value}`); continue; }
    console.log(`  ${key}: "${value}"`);
  }
  console.log();
}
