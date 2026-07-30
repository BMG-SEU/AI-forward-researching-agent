"""报告工具 - 将报告写入实际文件系统"""

from pathlib import Path
from datetime import datetime


def save_report(content: str, filename: str = None) -> str:
    """
    将跟踪报告保存到 reports/ 目录。

    Args:
        content: 报告内容 (Markdown 格式)
        filename: 文件名，默认自动生成

    Returns:
        保存的文件路径
    """
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    if not filename:
        date_str = datetime.now().strftime("%Y-%m-%d")
        # 从内容中提取主题
        lines = content.strip().split("\n")
        topic = "AI-Frontier"
        for line in lines:
            if line.startswith("## ") or line.startswith("# "):
                topic = line.strip("#").strip()[:30]
                break
        safe_topic = "".join(c for c in topic if c.isalnum() or c in " -_").strip()
        filename = f"{date_str}-{safe_topic}.md"

    if not filename.endswith(".md"):
        filename += ".md"

    filepath = reports_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return f"报告已保存至: {filepath}"
