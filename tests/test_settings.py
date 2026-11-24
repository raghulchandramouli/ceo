from pathlib import Path

import pytest

from ceo_api.config import Settings
from ceo_workers.entrypoint import WorkerSettings


def test_database_url_defaults_to_local_postgres(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.chdir(tmp_path)
    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://ceo:ceo@localhost:5432/ceo"


def test_temporal_address_defaults_to_local(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("TEMPORAL_ADDRESS", raising=False)
    monkeypatch.delenv("TEMPORAL_NAMESPACE", raising=False)
    monkeypatch.chdir(tmp_path)
    settings = WorkerSettings()
    assert settings.temporal_address == "localhost:7233"
    assert settings.temporal_namespace == "default"
