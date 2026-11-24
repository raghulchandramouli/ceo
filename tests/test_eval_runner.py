from pathlib import Path

from evals.runner import main, run_suite


def test_empty_checked_in_suites_pass() -> None:
    assert main() == 0


def test_suite_fails_when_cases_exist_without_an_executor(tmp_path: Path) -> None:
    suite = tmp_path / "acl_leaks"
    suite.mkdir()
    (suite / "private_channel.json").write_text("{}\n", encoding="utf-8")
    assert run_suite(suite) == 1


def test_suite_ignores_placeholders(tmp_path: Path) -> None:
    suite = tmp_path / "acl_leaks"
    suite.mkdir()
    (suite / ".gitkeep").write_text("", encoding="utf-8")
    assert run_suite(suite) == 0
