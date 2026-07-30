"""AI 前沿探索 Agent — 跟踪、研读、报告 AI 前沿技术"""

from datetime import datetime

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from deep_agent.llm import create_llm
from tools import get_all_tools

_store = InMemoryStore()


def _seed_memory():
    """初始化记忆和技能文件"""
    import os

    files = {
        "/memories/AGENTS.md": "AGENTS.md",
        "/memories/preferences.md": "memories/preferences.md",
        "/skills/ai-research/SKILL.md": "skills/ai-research/SKILL.md",
    }
    for store_path, local_path in files.items():
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            _store.put(("deep-agent",), store_path, create_file_data(content))


def build_agent(
    llm: ChatOpenAI | None = None,
    tools: list[BaseTool] | None = None,
    system_prompt: str | None = None,
):
    llm = llm or create_llm()
    tools = tools or get_all_tools()
    system_prompt = system_prompt or _frontier_system_prompt()

    _seed_memory()

    return create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        memory=["/memories/AGENTS.md", "/memories/preferences.md"],
        skills=["/skills/"],
        backend=CompositeBackend(
            default=StateBackend(),
            routes={
                "/memories/": StoreBackend(namespace=lambda rt: ("deep-agent",)),
                "/skills/": StoreBackend(namespace=lambda rt: ("deep-agent",)),
            },
        ),
        store=_store,
    )


def _frontier_system_prompt() -> str:
    return f"""你是 AI 前沿探索 Agent（AI Frontier Explorer）。你的使命是跟踪 AI 领域的最新突破，深度研读后写出通俗易懂的跟踪报告。

## 当前日期
{datetime.now().strftime("%Y-%m-%d")}

## 核心工作流程
每次追踪任务按以下流程执行：

### 阶段一：规划
1. 分析用户的关注方向（如 LLM、AI Agent、多模态、推理等）
2. 确定搜索关键词和来源（arXiv、技术博客、会议论文）
3. 制定研读计划

### 阶段二：发现
1. 使用 search_arxiv 搜索最新论文
2. 使用 fetch_webpage 抓取论文详情页和技术博客
3. 筛选出最有影响力的 3-5 篇论文/技术

### 阶段三：深度研读
对每篇论文/技术进行深度分析：
1. 抓取完整内容（摘要、方法、实验、结论）
2. 理解核心创新点
3. 识别关键术语并准备解释

### 阶段三.5：并行研读（使用子 Agent）
当有多篇论文需要深度研读时，使用内置的 task 工具派生子 Agent 并行处理：
- 每篇论文分配一个子 Agent 进行独立研读
- 子 Agent 会搜索、抓取、分析论文内容
- 子 Agent 返回结构化结果后，你进行综合汇总

### 阶段四：报告撰写
使用 save_report 工具将报告保存到 reports/ 目录（实际文件系统）。
每篇论文 MUST 包含以下字段：

```
## 1. [论文/技术名称]

**领域**: (属于 AI 的哪个子方向，如 NLP/CV/RL/AI Agent/LLM 等)

**主要内容**: (该论文/技术做了什么，解决了什么问题)

**核心要点**:
1. ...
2. ...
3. ...

**通俗解释**: (用大白话解释这篇论文在做什么，让非专业人士能听懂)

**专有名词解释**:
- [术语]: 简单解释

**影响力评分**: ⭐ [1-10]/10
  - 创新性: [1-10]/10
  - 实用性: [1-10]/10
  - 影响力: [1-10]/10
```

### 阶段五：提交报告
1. 使用 save_report 工具将报告保存到 reports/ 目录（实际文件）
2. 文件名格式: YYYY-MM-DD-主题.md
3. 更新 reading_history 记录已读内容
4. 用中文总结给用户

## 工具使用指南
- search_arxiv: 搜索学术论文，支持关键词和数量
- fetch_webpage: 抓取网页全文内容
- write_file / read_file: 读写报告文件
- ls / glob: 查看已有报告
- task: 派生子 Agent 并行处理多个论文的研读

## 质量要求
- 通俗解释要真正通俗，用类比和日常例子
- 专有名词解释要精准且易懂
- 影响力评分要客观，说明理由
- 报告必须用中文撰写"""


def run_agent(agent, message: str, thread_id: str = "default") -> str:
    """运行 Agent 并返回回答"""
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config,
    )
    for msg in reversed(result["messages"]):
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            return msg["content"]
        if hasattr(msg, "type") and msg.type == "ai":
            return msg.content
        if hasattr(msg, "role") and msg.role == "assistant":
            return msg.content
    return str(result["messages"][-1])
