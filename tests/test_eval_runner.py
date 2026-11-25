from pathlib import Path

from evals.runner import main, run_suite


def test_empty_checked_in_suites_pass() -> None:
    assert main() == 0


def test_suite_fails_when_cases_exist_without_an_executor(tmp_path: Path) -> None:
    suite = tmp_path / "acl_leaks"
    suite.mkdir()
    (suite / "private_channel.json").write_text("{}\n", encoding="utf-8")
    assert run_suite(suite) == 1


def test_acl_hard_gate_rejects_an_empty_suite(tmp_path: Path) -> None:
    suite = tmp_path / "acl_leaks"
    suite.mkdir()
    (suite / ".gitkeep").write_text("", encoding="utf-8")
    assert run_suite(suite) == 1


def test_planted_leak_fails_the_hard_gate(tmp_path: Path) -> None:
    suite = tmp_path / "acl_leaks"
    suite.mkdir()
    (suite / "planted.json").write_text(
        """
        {
          "document": {"tenant_id": "tenant-a", "principals": ["user:alice"]},
          "query": {
            "tenant_id": "tenant-a",
            "user_principals": ["user:alice"],
            "channel_principals": null
          },
          "expect_visible": false
        }
        """,
        encoding="utf-8",
    )
    assert run_suite(suite) == 1
