/* archwright report page logic — behavior:ask-lifecycle + report-page states.
 *
 * Environment-agnostic reducer: inlined into the generated HTML (no network,
 * no remote resources — constraint:no-server-dependency) and drivable under
 * node so the fixture suite trace-validates the REAL production reducer
 * against behavior:ask-lifecycle (trace shape: tools/trace-schema.ts).
 */
(function (root) {
  "use strict";

  // ---- ask-card state machine (behavior:ask-lifecycle) ----
  function newAsk(askType, autoCfg) {
    var ask = { ask_type: askType, auto_cfg: autoCfg, fsm: "derived", response: null };
    ask.trace = [{ event: "INITIAL", state: snapshot(ask), clock: 0 }];
    return ask;
  }

  function snapshot(ask) {
    return { ask_type: ask.ask_type, auto_cfg: ask.auto_cfg };
  }

  function record(ask, event) {
    ask.trace.push({ event: event, state: snapshot(ask), clock: ask.trace.length });
  }

  function send(ask, event, payload) {
    var t = { // transitions: guard checked BEFORE effects (rejected ops unrecorded)
      CONFIG_ON: function () {
        if (ask.fsm !== "derived") return false;
        ask.auto_cfg = "on_";
        return true;
      },
      AUTO_APPROVE: function () {
        if (ask.fsm !== "derived") return false;
        if (!(ask.ask_type === "approval" && ask.auto_cfg === "on_")) return false;
        ask.fsm = "auto_approved";
        ask.response = { kind: "approve-fix", note: "auto-approved by settings" };
        return true;
      },
      PRESENT: function () {
        if (ask.fsm !== "derived") return false;
        ask.fsm = "presented";
        return true;
      },
      RESPOND: function () {
        if (ask.fsm !== "presented") return false;
        ask.fsm = "answered";
        ask.response = payload || { kind: "approve-fix" };
        return true;
      },
      REROUTE: function () {
        if (ask.fsm !== "presented") return false;
        if (ask.ask_type !== "approval") return false;
        ask.ask_type = "decision"; // assign: reroute makes it a judgment call
        ask.fsm = "rerouted";
        ask.response = { kind: "reroute-to-decision", note: (payload && payload.note) || null };
        return true;
      },
      REPRESENT: function () {
        if (ask.fsm !== "rerouted") return false;
        ask.fsm = "presented";
        return true;
      }
    }[event];
    if (!t || !t()) return false;
    record(ask, event);
    return true;
  }

  // ---- report-page accumulation (pristine -> responding -> exported) ----
  function newPage(run) {
    return { fsm: "pristine", run: run, responses: {}, asks: {} };
  }

  function pageRecord(page, askId, response) {
    page.responses[askId] = response;
    if (page.fsm !== "responding") page.fsm = "responding";
  }

  function exportResponses(page) {
    page.fsm = "exported";
    return JSON.stringify({
      schema_version: 1,
      run: page.run,
      responded_at: new Date().toISOString(),
      responses: page.responses
    }, null, 2);
  }

  var api = { newAsk: newAsk, send: send, newPage: newPage,
              pageRecord: pageRecord, exportResponses: exportResponses };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ArchwrightReport = api;
})(this);
