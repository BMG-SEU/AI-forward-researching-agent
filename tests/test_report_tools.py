from pathlib import Path

from tools import report_tools


def test_save_report_sanitizes_path_and_updates_history(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    history = tmp_path / "memories" / "reading_history.md"
    monkeypatch.setattr(report_tools, "get_reports_dir", lambda: reports)
    monkeypatch.setattr(report_tools, "HISTORY_FILE", history)

    result = report_tools.save_report("# 安全报告\n\n内容", "../../unsafe:name.md")

    saved = reports / "unsafename.md"
    assert saved.exists()
    assert str(saved) in result
    assert "安全报告" in history.read_text(encoding="utf-8")
    assert "../reports/unsafename.md" in history.read_text(encoding="utf-8")


def test_safe_filename_always_returns_markdown_basename():
    name = report_tools._safe_filename(r"..\..\folder\paper?.txt")
    assert name == "paper.txt.md"
    assert Path(name).name == name


def test_set_reports_dir_persists_and_save_uses_it(tmp_path, monkeypatch):
    from deep_agent import config as config_module
    monkeypatch.setattr(config_module, "_compute_data_dir", lambda: tmp_path)
    history = tmp_path / "memories" / "reading_history.md"
    monkeypatch.setattr(report_tools, "HISTORY_FILE", history)

    new_dir = tmp_path / "custom-reports"
    message = report_tools.set_reports_dir(str(new_dir))

    assert str(new_dir.resolve()) in message
    assert report_tools.get_reports_dir() == new_dir.resolve()
    # 持久化文件已写入统一 config.json
    config_file = tmp_path / "config.json"
    assert config_file.exists()
    assert "custom-reports" in config_file.read_text(encoding="utf-8")

    # 保存报告会写入新目录
    result = report_tools.save_report("# 新目录报告\n\n内容")
    assert str(new_dir.resolve()) in result
    assert list(new_dir.glob("*.md"))


def test_set_reports_dir_creates_missing_directory(tmp_path, monkeypatch):
    from deep_agent import config as config_module
    monkeypatch.setattr(config_module, "_compute_data_dir", lambda: tmp_path)
    nested = tmp_path / "a" / "b" / "c"
    report_tools.set_reports_dir(str(nested))
    assert nested.is_dir()
