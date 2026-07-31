import os

from deep_agent.config import Settings, load_dotenv_compat


def test_load_dotenv_accepts_powershell_utf16(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPSEEK_API_KEY=sk-utf16\n", encoding="utf-16")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    load_dotenv_compat(env_file)

    assert os.environ["DEEPSEEK_API_KEY"] == "sk-utf16"
    assert Settings().deepseek_api_key == "sk-utf16"


def test_data_dir_can_be_overridden(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_FRONTIER_HOME", str(tmp_path))
    configured = Settings()
    assert configured.data_dir == tmp_path.resolve()
    assert configured.reports_dir == tmp_path.resolve() / "reports"
    assert configured.checkpoint_path == tmp_path.resolve() / "checkpoints.sqlite"


def test_reports_dir_can_be_overridden_by_env(tmp_path, monkeypatch):
    target = tmp_path / "my_reports"
    monkeypatch.setenv("REPORTS_DIR", str(target))
    configured = Settings()
    assert configured.reports_dir == target.resolve()
    # checkpoint 与 memory 不受影响，仍随 data_dir
    assert configured.checkpoint_path == configured.data_dir / "checkpoints.sqlite"


def test_reports_dir_expands_user_and_relative(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "a" / ".." / "b"))
    configured = Settings()
    assert configured.reports_dir == (tmp_path / "b").resolve()