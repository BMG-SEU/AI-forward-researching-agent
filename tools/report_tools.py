"""报告工具 - 动态报告目录、安全保存并维护阅读历史。

报告目录可通过三种方式决定（优先级从高到低）：
1. set_reports_dir() 在对话中设置并持久化（最高优先级，代表用户最新意图）
2. REPORTS_DIR 环境变量 / .env
3. 默认 <data_dir>/reports
"""

from datetime import datetime
from pathlib import Path
import re

from deep_agent.config import save_settings, settings

HISTORY_FILE = settings.data_dir / "memories" / "reading_history.md"


def _load_saved_reports_dir() -> Path | None:
    """读取对话中持久化的报告目录（若存在）。"""
    from deep_agent.config import _load_persisted
    saved = _load_persisted().get("reports_dir")
    if saved:
        return Path(saved).expanduser().resolve()
    return None


def get_reports_dir() -> Path:
    """当前报告目录：对话设置 > 环境变量 > 默认。"""
    saved = _load_saved_reports_dir()
    if saved is not None:
        return saved
    return settings.reports_dir


def set_reports_dir(path: str) -> str:
    """将报告保存目录改为指定路径，并持久化到配置。

    Args:
        path: 目标目录的绝对或相对路径。

    Returns:
        确认信息，包含新的报告目录。
    """
    try:
        new_dir = Path(path).expanduser().resolve()
        new_dir.mkdir(parents=True, exist_ok=True)
        save_settings({"reports_dir": str(new_dir)})
        return f"报告保存目录已更改为: {new_dir}"
    except OSError as exc:
        return f"无法设置报告目录: {exc!s}"


def _safe_filename(filename: str) -> str:
    """将任意输入压缩成 reports 目录内的安全 Markdown 文件名。"""
    name = Path(filename.replace("\\", "/")).name
    stem = name[:-3] if name.lower().endswith(".md") else name
    stem = re.sub(r"[^\w\- .\u4e00-\u9fff]", "", stem, flags=re.UNICODE)
    stem = re.sub(r"\s+", "-", stem).strip(" .-_")[:80]
    return f"{stem or 'AI-Frontier'}.md"


def _topic_from_content(content: str) -> str:
    for line in content.splitlines():
        if line.startswith(("# ", "## ")):
            return line.lstrip("#").strip()
    return "AI-Frontier"


def _append_reading_history(filename: str, topic: str) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("# Reading History\n\n", encoding="utf-8")
    entry = f"- {datetime.now().isoformat(timespec='seconds')} | [{topic}](../reports/{filename})\n"
    with HISTORY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def save_report(content: str, filename: str | None = None) -> str:
    """将 Markdown 报告保存到当前报告目录，并记录阅读历史。"""
    reports_dir = get_reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)
    topic = _topic_from_content(content)
    if not filename:
        filename = f"{datetime.now():%Y-%m-%d}-{topic}"
    safe_name = _safe_filename(filename)
    filepath = (reports_dir / safe_name).resolve()
    if filepath.parent != reports_dir.resolve():
        raise ValueError("报告路径必须位于当前报告目录内")
    filepath.write_text(content, encoding="utf-8")
    _append_reading_history(safe_name, topic)
    return f"报告已保存至: {filepath}"
