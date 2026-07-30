"""图可视化工具 — 将 LangGraph 图导出为 Mermaid 流程图"""

from langgraph.graph import StateGraph
from deep_agent.agent import DeepAgent


def export_mermaid(graph=None, output_file: str = None) -> str:
    """
    将 LangGraph 图导出为 Mermaid 流程图

    Args:
        graph: 编译后的 LangGraph 图，默认使用 DeepAgent 的图
        output_file: 可选，保存到文件

    Returns:
        Mermaid 流程图文本
    """
    if graph is None:
        agent = DeepAgent()
        graph = agent.graph

    # 生成 Mermaid 图
    mermaid_code = graph.get_graph().draw_mermaid()

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(mermaid_code)

    return mermaid_code


def print_graph_ascii():
    """打印简单的 ASCII 流程图"""
    print("""
  ┌─────────────┐
  │   START     │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │   agent     │  ← LLM 推理节点
  │  (reason)   │
  └──────┬──────┘
         │
    ┌────┴────┐
    │ 需要工具? │  ← 条件路由
    └────┬────┘
         │
    Yes  │    No
    │    │     │
    ▼    │     ▼
  ┌────────┐ ┌────────┐
  │ tools  │ │  END   │
  │ (exec) │ └────────┘
  └───┬────┘
      │
      └──→ 回到 agent

  Nodes:  agent, tools
  Edges:  START → agent
          agent → tools  (当 LLM 调用了工具)
          agent → END    (当 LLM 直接回答)
          tools → agent  (工具结果返回给 LLM)
    """)


if __name__ == "__main__":
    # 测试：导出 Mermaid 并打印 ASCII 图
    agent = DeepAgent()
    mermaid = export_mermaid(agent.graph)
    print("=== Mermaid 流程图 ===")
    print(mermaid)
    print()
    print_graph_ascii()
