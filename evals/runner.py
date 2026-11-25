"""Run the evaluation suites.

acl_leaks is a hard gate. It fails when there are no cases, when a case is
invalid, or when any document is shown to a caller who must not see it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import cast

from ceo_brain.acl.filter import is_visible

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
    if suite_dir.name == "acl_leaks":
        return run_acl_leaks(suite_dir)
    cases = list_cases(suite_dir)
    if not cases:
        print(f"{suite_dir.name}: no cases")
        return 0
    print(
        f"{suite_dir.name}: {len(cases)} case(s) found, but the suite executor is not implemented",
        file=sys.stderr,
    )
    return 1


def run_acl_leaks(suite_dir: Path) -> int:
    cases = [path for path in list_cases(suite_dir) if path.suffix == ".json"]
    if not cases:
        print("acl_leaks: no cases; hard gate failed", file=sys.stderr)
        return 1
    leaks = 0
    mismatches = 0
    for path in cases:
        try:
            visible, expected = _evaluate_case(path)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            print(f"acl_leaks: invalid case {path.name}: {exc}", file=sys.stderr)
            return 1
        if visible != expected:
            mismatches += 1
            if visible and not expected:
                leaks += 1
                print(f"acl_leaks: leak in {path.name}", file=sys.stderr)
            else:
                print(f"acl_leaks: missed visible document in {path.name}", file=sys.stderr)
    percent = (leaks / len(cases)) * 100
    print(f"acl_leaks: {percent:.0f}% leaks ({leaks}/{len(cases)})")
    if leaks or mismatches:
        print("acl_leaks hard gate failed", file=sys.stderr)
        return 1
    return 0


def _evaluate_case(path: Path) -> tuple[bool, bool]:
    raw = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    document = _object(raw["document"], "document")
    query = _object(raw["query"], "query")
    expected = raw["expect_visible"]
    if not isinstance(expected, bool):
        raise TypeError("expect_visible must be a boolean")
    principals = _strings(document["principals"], "principals")
    # Revoked principals are history. Visibility uses the current principal set only.
    _strings(document.get("revoked_principals", []), "revoked_principals")
    channel = query["channel_principals"]
    channel_principals = None if channel is None else _strings(channel, "channel_principals")
    visible = is_visible(
        document_tenant=_string(document["tenant_id"], "document.tenant_id"),
        document_principals=set(principals),
        query_tenant=_string(query["tenant_id"], "query.tenant_id"),
        user_principals=set(_strings(query["user_principals"], "user_principals")),
        channel_principals=set(channel_principals) if channel_principals is not None else None,
    )
    return visible, expected


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be an object")
    return cast(dict[str, object], value)


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or value == "":
        raise TypeError(f"{label} must be a string")
    return value


def _strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{label} must be a list")
    items = cast(list[object], value)
    return [_string(item, label) for item in items]


def main() -> int:
    root = Path(__file__).resolve().parent
    acl = run_acl_leaks(root / "suites" / "acl_leaks")
    citations = run_suite(root / "suites" / "citations")
    return acl or citations


if __name__ == "__main__":
    raise SystemExit(main())
