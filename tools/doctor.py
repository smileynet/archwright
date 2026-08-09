#!/usr/bin/env python3
"""archwright doctor: check all dependencies and report capability gaps.

Exit 0: all required deps present (warnings for missing capability/optional deps).
Exit 1: required dep missing.
"""

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent


def _version(cmd, flag="--version"):
    """Get version string from a command, or None."""
    exe = shutil.which(cmd)
    if not exe:
        return None
    try:
        r = subprocess.run([exe, flag], capture_output=True, text=True, timeout=10)
        out = (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else ""
        return out
    except (subprocess.TimeoutExpired, OSError):
        return ""


def _python_module(name):
    """Check if a Python module is importable and get its version."""
    try:
        mod = __import__(name)
        ver = getattr(mod, "__version__", "installed")
        return ver
    except ImportError:
        return None


def _jar_exists():
    """Check for the Alloy jar."""
    import os
    env = os.environ.get("ARCHWRIGHT_ALLOY_JAR")
    if env and Path(env).exists():
        return str(Path(env))
    candidates = [
        REPO_ROOT / ".references" / "alloy6.jar",
        Path.home() / "code" / "archwright" / ".references" / "alloy6.jar",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


# Dependency definitions: (name, check_fn, category, purpose, install_hint)
# Categories: required (exit 1 if missing), capability (suite tests skip), optional (advisory)

DEPS = [
    # Required
    ("python", lambda: _version("python3") or _version("python"), "required",
     "all tools + suite", None),
    ("pyyaml", lambda: _python_module("yaml"), "required",
     "all tools (YAML parsing)", "mise run setup"),
    # Capability (suite tests skip without these)
    ("java", lambda: _version("java", "-version"), "capability",
     "Alloy behavior + contract checks",
     "winget install EclipseAdoptium.Temurin.21.JRE | brew install temurin | apt install default-jre"),
    ("alloy6.jar", _jar_exists, "capability",
     "bounded model checking (behavior + contract specs)", "mise run rehydrate-alloy"),
    ("hypothesis", lambda: _python_module("hypothesis"), "capability",
     "PBT harness (property-based testing)", "mise run setup"),
    ("node", lambda: _version("node"), "capability",
     "check-compile, report reducer, trace-schema validation",
     "mise install (managed by mise.toml)"),
    ("git", lambda: _version("git"), "capability",
     "commit-binding code_state, changed-only scoping", "apt install git | brew install git"),
    # Optional (never block suite, advisory only)
    ("semgrep", lambda: _version("semgrep"), "optional",
     "review AST checks (archwright-review)", "pipx install semgrep"),
    ("smcat", lambda: _version("smcat"), "optional",
     "FSM diagram rendering (PNG needs Graphviz dot)", "npm i -g state-machine-cat"),
    ("merman-cli", lambda: _version("merman-cli") or _version("merman"), "optional",
     "Mermaid diagram rendering", "cargo install merman-cli"),
]


def main():
    print("=== Archwright Environment ===")
    issues = {"required": [], "capability": []}

    for name, check_fn, category, purpose, hint in DEPS:
        result = check_fn()
        if result:
            # Truncate long version strings
            ver = str(result)[:60]
            print(f"  ✓ {name:<14} {ver}")
        else:
            if category == "required":
                print(f"  ✗ {name:<14} MISSING — {purpose}")
                if hint:
                    print(f"                   fix: {hint}")
                issues["required"].append(name)
            elif category == "capability":
                print(f"  ✗ {name:<14} missing — {purpose} will SKIP")
                if hint:
                    print(f"                   fix: {hint}")
                issues["capability"].append(name)
            else:  # optional
                print(f"  ○ {name:<14} not installed — {purpose}")
                if hint:
                    print(f"                   install: {hint}")

    print()
    if issues["required"]:
        print(f"BLOCKED: {len(issues['required'])} required dep(s) missing — tools will not run")
        sys.exit(1)
    elif issues["capability"]:
        n = len(issues["capability"])
        print(f"Ready with gaps: {n} capability dep(s) missing — some suite tests will SKIP")
        sys.exit(0)
    else:
        print("Ready: full suite capability (0 gaps)")
        sys.exit(0)


if __name__ == "__main__":
    main()
