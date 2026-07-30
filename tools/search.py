"""网络搜索工具 - 使用 DuckDuckGo 进行轻量级网络搜索"""

from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class DuckDuckGoSearchInput(BaseModel):
    """搜索输入"""
    query: str = Field(description="搜索查询词")


class DuckDuckGoSearchTool(BaseTool):
    """使用 DuckDuckGo 进行网络搜索"""

    name: str = "web_search"
    description: str = """搜索网络信息。当你需要回答关于最新事件、实时数据、
不熟悉的话题时使用。输入搜索关键词即可返回相关结果摘要。"""

    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: str) -> str:
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, max_results=5)):
                    title = r.get("title", "")
                    body = r.get("body", "")
                    href = r.get("href", "")
                    results.append(f"{i+1}. [{title}]({href})\n   {body[:200]}")

            if not results:
                return f"未找到 '{query}' 的相关结果。"

            return "\n\n".join(results)

        except ImportError:
            return "错误: 需要安装 duckduckgo-search 包 (pip install duckduckgo-search)"
        except Exception as e:
            return f"搜索出错: {e!s}"


duckduckgo_search_tool = DuckDuckGoSearchTool()
