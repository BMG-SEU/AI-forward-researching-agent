from pathlib import Path

from tools import report_tools


def test_save_report_sanitizes_path_and_updates_history(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    history = tmp_path / "memories" / "reading_history.md"
    monkeypatch.setattr(report_tools, "REPORTS_DIR", reports)
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
