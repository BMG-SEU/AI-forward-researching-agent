"""工具注册中心"""

from typing import List
from langchain_core.tools import tool


def get_all_tools() -> List:
    """返回所有注册的工具"""
    from tools.calculator import calculator_tool
    from tools.search import duckduckgo_search_tool

    tools = [calculator_tool, duckduckgo_search_tool]

    @tool
    def search_arxiv(query: str, max_results: int = 10) -> str:
        """Search arXiv for academic papers by keyword. Returns paper info including title, authors, summary."""
        from tools.arxiv_tools import search_arxiv as _search
        results = _search(query, max_results=max_results)
        if not results:
            return "No papers found."
        lines = []
        for i, p in enumerate(results, 1):
            if "error" in p:
                return p["error"]
            lines.append(
                f"{i}. {p['title']}\n"
                f"   Authors: {', '.join(p['authors'][:5])}{'...' if len(p['authors']) > 5 else ''}\n"
                f"   Published: {p['published']}  |  Categories: {', '.join(p['categories'][:3])}\n"
                f"   Link: {p['link']}\n"
                f"   Summary: {p['summary'][:300]}..."
            )
        return "\n\n".join(lines)
    tools.append(search_arxiv)

    @tool
    def fetch_webpage(url: str, max_length: int = 8000) -> str:
        """Fetch and extract readable text content from a webpage URL. Use for reading papers and articles."""
        from tools.web_tools import fetch_webpage as _fetch
        return _fetch(url, max_length=max_length)
    tools.append(fetch_webpage)

    @tool
    def save_report(content: str, filename: str = "") -> str:
        """Save a research report to the current reports directory. Content should be in Markdown."""
        from tools.report_tools import save_report as _save
        return _save(content, filename=filename if filename else None)
    tools.append(save_report)

    @tool
    def set_reports_dir(path: str) -> str:
        """Change the directory where reports are saved. Use this when the user asks to save reports to a specific folder (e.g. '把报告保存到 D:/xxx'). The new directory is remembered for future runs."""
        from tools.report_tools import set_reports_dir as _set
        return _set(path)
    tools.append(set_reports_dir)

    return tools


def get_tool_names() -> List[str]:
    return [t.name if hasattr(t, 'name') else t.__name__ for t in get_all_tools()]
