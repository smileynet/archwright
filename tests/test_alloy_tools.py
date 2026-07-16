import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]


def load_tool(name: str):
    path = ROOT / "tools" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compiler = load_tool("archwright-compile-alloy.py")
checker = load_tool("archwright-check.py")


BEHAVIOR = {
    "kind": "behavior",
    "id": "door-lifecycle",
    "context": {
        "variables": {
            "authorized": {"type": "bool", "initial": False},
            "attempts": {"type": "int", "initial": 0},
        }
    },
    "initial": "closed",
    "states": {
        "closed": {
            True: {
                "OPEN": {
                    "target": "open",
                    "guard": {"predicate": "authorized"},
                    "effects": {"attempts": 1},
                }
            }
        },
        "open": {True: {}},
    },
    "invariants": [
        {
            "id": "authorized-before-open",
            "type": "state",
            "predicate": "always (open implies authorized)",
        }
    ],
    "check": {"model": {"scope": 4, "steps": 6}},
}


class AlloyCompilerTests(unittest.TestCase):
    def test_compiles_yaml_boolean_on_key_and_bool_context(self):
        source = compiler.generate_alloy(BEHAVIOR)

        self.assertIn("pred t_closed_OPEN", source)
        self.assertIn("var authorized: one BoolVal", source)
        self.assertIn("M.authorized = TrueVal", source)
        self.assertIn("M.attempts' = 1", source)

    def test_compiles_real_invariant_without_placeholder(self):
        source = compiler.generate_alloy(BEHAVIOR)

        self.assertIn("M.current = Open implies M.authorized = TrueVal", source)
        self.assertNotIn("placeholder", source)
        self.assertNotIn("always (true)", source)

    def test_rejects_unsupported_predicate(self):
        bad = {**BEHAVIOR, "invariants": [{"id": "bad", "predicate": "eventually open"}]}

        with self.assertRaisesRegex(ValueError, "Unsupported predicate"):
            compiler.generate_alloy(bad)


class CheckerTests(unittest.TestCase):
    def test_boundary_is_schema_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "boundary.md"
            path.write_text("---\nkind: boundary\nid: local-only\n---\n", encoding="utf-8")

            output, code = checker.check_file(path)

        self.assertEqual(0, code)
        self.assertIn("PASS", output)

    def test_missing_runtime_is_error(self):
        with patch.object(checker, "_alloy_jar", return_value=None):
            result = checker.check_behavior(BEHAVIOR, Path("behavior.yaml"))

        self.assertEqual("error", result[0]["status"])

    def test_real_alloy_finds_counterexample(self):
        if checker._alloy_jar() is None:
            self.skipTest("Pinned Alloy runtime is not installed")
        bad = {
            **BEHAVIOR,
            "context": {"variables": {"authorized": {"type": "bool", "initial": False}}},
            "states": {
                "closed": {True: {"OPEN": {"target": "open"}}},
                "open": {True: {}},
            },
        }

        result = checker.check_behavior(bad, Path("behavior.yaml"))

        self.assertEqual("fail", result[0]["status"])
        self.assertEqual("bounded", result[0]["assurance"])
        self.assertTrue(result[0]["counterexample"])

    def test_parses_pass_and_counterexample_results(self):
        invariants = [
            {"id": "safe-open", "confidence": "★"},
            {"id": "reachable-close", "confidence": "★"},
        ]

        result = checker.parse_alloy_results(
            "00. check safeOpen 0 UNSAT\n01. check reachableClose 0 SAT",
            invariants,
        )

        self.assertEqual(["pass", "fail"], [item["status"] for item in result])
        self.assertEqual("bounded", result[0]["assurance"])

    def test_malformed_alloy_output_has_no_results(self):
        self.assertEqual([], checker.parse_alloy_results("unexpected output", BEHAVIOR["invariants"]))

    def test_parses_counterexample_instances(self):
        receipt = {"commands": {"safeOpen": {"solution": [{"instances": [{"state": 1}]}]}}}

        self.assertEqual({"safeOpen": [{"state": 1}]}, checker.parse_counterexamples(receipt))

    def test_pending_target_is_explicit_skip(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "pending.md"
            data = {
                "kind": "constraint",
                "id": "pending-target",
                "confidence": "★",
                "check": {
                    "method": "grep",
                    "target": "not-built-yet",
                    "target_status": "pending",
                    "pattern": "forbidden",
                    "expect": "absent",
                },
            }

            result = checker.check_conformance(data, spec)

        self.assertEqual("skipped", result[0]["status"])
        self.assertIn("pending", result[0]["message"].lower())


if __name__ == "__main__":
    unittest.main()
