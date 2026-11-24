import importlib
import subprocess
from pathlib import Path

from ceo_workers.entrypoint import QUEUES

ROOTS = (
    Path("apps/api/src"),
    Path("apps/workers/src"),
    Path("packages/core/src"),
    Path("packages/brain/src"),
    Path("packages/connectors/src"),
    Path("packages/surfaces/src"),
    Path("packages/agent/src"),
)


def module_name(root: Path, path: Path) -> str | None:
    relative = path.relative_to(root).with_suffix("")
    if "migrations" in relative.parts or relative.name == "__main__":
        return None
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def test_phase1_modules_import() -> None:
    failures: list[str] = []
    for root in ROOTS:
        for path in sorted(root.rglob("*.py")):
            name = module_name(root, path)
            if name is None:
                continue
            try:
                importlib.import_module(name)
            except Exception as exc:
                failures.append(f"{name}: {exc}")
    assert failures == []


def test_local_worker_queues() -> None:
    assert QUEUES == ("agent-queue", "sync-queue")


def test_package_boundaries() -> None:
    completed = subprocess.run(
        ["lint-imports"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
