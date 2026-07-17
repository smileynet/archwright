# Deployed skills can't use repo-relative tool paths

One-line: skills deploy globally and run from target projects where `tools/` doesn't exist.

**Date:** 2026-07-17 · **Source:** session review

Skill command examples now say `python3 <archwright-repo>/tools/...` with a
repo-locator note in archwright-check. Anything a skill references at runtime
must either deploy with it (domains, glossary, stacks registry pattern) or be
addressed via an explicit placeholder the agent resolves.
