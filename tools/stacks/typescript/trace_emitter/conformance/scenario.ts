/**
 * Conformance scenario for the TypeScript trace emitter (rule 3: spike output IS
 * the conformance scenario; rule 4: MUST include a violating scenario → FAIL).
 *
 * Simulates a session-like guarded counter (mirrors the guarded-counter fixture
 * and TileRush session-lifecycle) and emits two traces via the real recorder:
 *
 *   passing.trace.json   — respects the JOIN guard (never exceeds max)
 *   violating.trace.json — a buggy implementation admits a 4th player
 *                          (capacity-never-exceeded must FAIL at that entry)
 *
 * Run: node --experimental-strip-types scenario.ts <outdir>
 */

import { createTraceRecorder } from "../traceRecorder.ts";

const outDir = process.argv[2] ?? ".";

// --- Correct implementation: guard respected ---
function correctRun(): string {
  const rec = createTraceRecorder({ current_players: 0, max_players: 3 });
  let players = 0;
  const max = 3;
  const join = () => {
    if (players < max) {
      players += 1;
      rec.record("JOIN", { current_players: players });
      return true;
    }
    return false; // guard rejected — nothing recorded, nothing happened
  };
  join(); // 1
  join(); // 2
  join(); // 3
  join(); // rejected at capacity — correctly not recorded
  rec.record("START");
  rec.record("COMPLETE");
  rec.write(`${outDir}/passing.trace.json`);
  return "ok";
}

// --- Buggy implementation: guard missing — admits a 4th player ---
function buggyRun(): string {
  const rec = createTraceRecorder({ current_players: 0, max_players: 3 });
  let players = 0;
  const joinUnguarded = () => {
    players += 1; // BUG: no capacity check
    rec.record("JOIN", { current_players: players });
  };
  joinUnguarded(); // 1
  joinUnguarded(); // 2
  joinUnguarded(); // 3
  joinUnguarded(); // 4 — capacity exceeded; validator must FAIL here
  rec.record("START");
  rec.write(`${outDir}/violating.trace.json`);
  return "ok";
}

correctRun();
buggyRun();
console.log("traces written");
