"""将编译后的 Deep Agents/LangGraph 图导出为 Mermaid。"""

from pathlib import Path
from typing import Any

from deep_agent.agent import build_agent


def export_mermaid(graph: Any | None = None, output_file: str | Path | None = None) -> str:
    """返回 Mermaid 图文本，并可选择写入文件。"""
    compiled_graph = graph or build_agent()
    mermaid_code = compiled_graph.get_graph().draw_mermaid()
    if output_file:
        Path(output_file).write_text(mermaid_code, encoding="utf-8")
    return mermaid_code


def print_graph_ascii() -> None:
    """打印当前运行图的 Mermaid 表达。"""
    print(export_mermaid())


if __name__ == "__main__":
    print_graph_ascii()