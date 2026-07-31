"""报告工具 - 安全地保存报告并维护阅读历史。"""

from datetime import datetime
from pathlib import Path
import re

from deep_agent.config import settings

REPORTS_DIR = settings.reports_dir
HISTORY_FILE = settings.data_dir / "memories" / "reading_history.md"


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
    """将 Markdown 报告保存到固定目录，并记录阅读历史。"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    topic = _topic_from_content(content)
    if not filename:
        filename = f"{datetime.now():%Y-%m-%d}-{topic}"
    safe_name = _safe_filename(filename)
    filepath = (REPORTS_DIR / safe_name).resolve()
    if filepath.parent != REPORTS_DIR.resolve():
        raise ValueError("报告路径必须位于 reports 目录内")
    filepath.write_text(content, encoding="utf-8")
    _append_reading_history(safe_name, topic)
    return f"报告已保存至: {filepath}"
