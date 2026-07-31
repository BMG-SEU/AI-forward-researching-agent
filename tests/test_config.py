import os

from deep_agent import config as config_module
from deep_agent.config import Settings, load_dotenv_compat, load_persisted_config, save_settings


def test_load_dotenv_accepts_powershell_utf16(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPSEEK_API_KEY=sk-utf16\n", encoding="utf-16")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(config_module, "_compute_data_dir", lambda: tmp_path)
    config_module._config_file.cache_clear() if hasattr(config_module._config_file, "cache_clear") else None

    load_dotenv_compat(env_file)

    assert os.environ["DEEPSEEK_API_KEY"] == "sk-utf16"
    assert Settings().deepseek_api_key == "sk-utf16"
    # key 已迁移到持久化配置
    persisted = config_module._load_persisted()
    assert persisted.get("deepseek_api_key") == "sk-utf16"


def test_api_key_persists_across_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module, "_compute_data_dir", lambda: tmp_path)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    # 第一次：保存 key 到持久化
    save_settings({"deepseek_api_key": "sk-persisted-abc"})
    # 模拟新进程：清掉 env，从持久化加载
    monkeypatch.delenv("deepseek_api_key", raising=False)
    load_persisted_config()

    assert Settings().deepseek_api_key == "sk-persisted-abc"


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