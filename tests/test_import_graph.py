"""The workspace import graph matches the architecture rule, and that rule can fail."""

from __future__ import annotations

import os
import subprocess
import tomllib
from pathlib import Path
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
SANDBOX_PACKAGE = "ceo_sandbox"

EXPECTED_LAYERS: tuple[dict[str, bool], ...] = (
    {"ceo_api": False, "ceo_workers": False},
    {"ceo_agent": False},
    {"ceo_brain": False, "ceo_connectors": False, "ceo_surfaces": False, SANDBOX_PACKAGE: True},
    {"ceo_core": False},
)


def sandbox_package_exists() -> bool:
    return (REPO_ROOT / "packages" / "sandbox" / "src" / SANDBOX_PACKAGE).is_dir()


def expected_layers() -> tuple[dict[str, bool], ...]:
    layers = [dict(layer) for layer in EXPECTED_LAYERS]
    layers[2][SANDBOX_PACKAGE] = not sandbox_package_exists()
    return tuple(layers)


def discover_workspace_packages() -> set[str]:
    found: set[str] = set()
    for base in (REPO_ROOT / "apps", REPO_ROOT / "packages"):
        for project in base.iterdir():
            src = project / "src"
            if not src.is_dir():
                continue
            for child in src.iterdir():
                if child.is_dir() and (child / "__init__.py").is_file():
                    found.add(child.name)
    return found


def as_dict(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AssertionError(label)
    return cast(dict[str, object], value)


def as_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise AssertionError(label)
    return cast(list[object], value)


def import_linter_config() -> dict[str, object]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    tool = as_dict(data["tool"], "pyproject.toml is missing [tool]")
    return as_dict(tool["importlinter"], "pyproject.toml is missing [tool.importlinter]")


def parse_layer(raw: str) -> dict[str, bool]:
    if ":" in raw:
        raise AssertionError(f"layer siblings must be independent: {raw}")
    parsed: dict[str, bool] = {}
    for part in raw.split("|"):
        name = part.strip()
        optional = name.startswith("(") and name.endswith(")")
        if optional:
            name = name[1:-1].strip()
        parsed[name] = optional
    return parsed


def layers_contract(config: dict[str, object]) -> list[str]:
    for item in as_list(config["contracts"], "import-linter contracts are missing"):
        contract = as_dict(item, "import-linter contract must be a table")
        if contract.get("name") != "Acyclic package layers":
            continue
        layers = [
            layer
            for layer in as_list(contract.get("layers"), "layers contract is missing its layers")
            if isinstance(layer, str)
        ]
        if layers:
            return layers
    raise AssertionError("Acyclic package layers contract is missing")


def root_packages(config: dict[str, object]) -> set[str]:
    names = [
        item
        for item in as_list(config["root_packages"], "root_packages must list package names")
        if isinstance(item, str)
    ]
    return set(names)


def test_workspace_packages_match_the_layer_rule() -> None:
    config = import_linter_config()
    actual = [parse_layer(layer) for layer in layers_contract(config)]
    assert actual == list(expected_layers())
    discovered = discover_workspace_packages()
    assert root_packages(config) == discovered
    classified = {name for layer in actual for name, optional in layer.items() if not optional}
    assert classified == discovered


def test_forbidden_upward_import_breaks_the_same_layer_shape(tmp_path: Path) -> None:
    broken = _write_graph(tmp_path / "broken", upward=True)
    allowed = _write_graph(tmp_path / "allowed", upward=False)

    broken_run = _lint(broken)
    allowed_run = _lint(allowed)

    assert broken_run.returncode != 0, broken_run.stdout + broken_run.stderr
    assert "core is not allowed to import app_a" in broken_run.stdout + broken_run.stderr
    assert allowed_run.returncode == 0, allowed_run.stdout + allowed_run.stderr


def _write_graph(root: Path, *, upward: bool) -> Path:
    modules = ("app_a", "app_b", "agent", "domain", "core")
    for name in modules:
        package = root / name
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
    (root / "app_a" / "__init__.py").write_text("import core\n", encoding="utf-8")
    if upward:
        (root / "core" / "leak.py").write_text("import app_a\n", encoding="utf-8")
    config = root / "pyproject.toml"
    config.write_text(
        "\n".join(
            (
                "[tool.importlinter]",
                'root_packages = ["app_a", "app_b", "agent", "domain", "core"]',
                "",
                "[[tool.importlinter.contracts]]",
                'name = "Acyclic package layers"',
                'type = "layers"',
                "layers = [",
                '  "app_a | app_b",',
                '  "agent",',
                '  "domain",',
                '  "core",',
                "]",
                "",
            )
        ),
        encoding="utf-8",
    )
    return config


def _lint(config: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(config.parent)
    return subprocess.run(
        ["lint-imports", "--no-cache", str(config)],
        check=False,
        capture_output=True,
        text=True,
        cwd=config.parent,
        env=env,
    )
