"""Run the evaluation suites.

An empty suite passes. A suite with cases fails until an executor exists, so a
checked-in case cannot silently skip the ACL hard gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

CASE_SUFFIXES = {".json", ".yaml", ".yml", ".py"}
IGNORED_NAMES = {".gitkeep", "__init__.py"}


def list_cases(suite_dir: Path) -> list[Path]:
    if not suite_dir.exists():
        return []
    return sorted(
        path
        for path in suite_dir.rglob("*")
        if path.is_file() and path.name not in IGNORED_NAMES and path.suffix in CASE_SUFFIXES
    )


def run_suite(suite_dir: Path) -> int:
    cases = list_cases(suite_dir)
    if not cases:
        print(f"{suite_dir.name}: no cases")
        return 0
    print(
        f"{suite_dir.name}: {len(cases)} case(s) found, but the suite executor is not implemented",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    root = Path(__file__).resolve().parent
    acl = run_suite(root / "suites" / "acl_leaks")
    citations = run_suite(root / "suites" / "citations")
    if acl != 0:
        print("acl_leaks hard gate failed", file=sys.stderr)
    return acl or citations


if __name__ == "__main__":
    raise SystemExit(main())
