# LangGraph Studio entrypoint for visualizing the agent graph
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from deep_agent.config import settings
from deep_agent.llm import create_llm
from tools import get_all_tools


def _create_system_prompt(tools):
    tool_descriptions = "\n".join(f"  - {t.name}: {t.description}" for t in tools)
    tool_names = ", ".join(t.name for t in tools)
    return f"""你是一个能力强大的 AI 助手（DeepAgent），可以使用工具来帮助用户解决问题。\n\n## 可用工具\n{tool_descriptions}\n\n## 工作方式\n1. 分析用户的问题，决定是否需要使用工具\n2. 如果需要工具，请使用工具获取信息\n3. 根据工具返回的结果，给出最终答案\n4. 如果不需要工具，直接回答\n\n## 规则\n- 使用工具时，一次只调用一个工具\n- 观察工具结果后再决定下一步\n- 工具调用格式: <tool_name>(输入参数)\n- 可以以中文回答用户的问题\n- 如果多次尝试后仍无法解决问题，诚实地告诉用户\n\n可用工具: {tool_names}"""


def call_llm(state, llm, tools):
    system_prompt = _create_system_prompt(tools)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(messages)
    return {"messages": [response], "next_step": None}


def call_tool(state, tools_dict):
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {"messages": [], "next_step": "end"}

    tool_messages = []
    for tc in last_message.tool_calls:
        tool_name = tc["name"]
        tool_args = tc.get("args", {})
        tool_call_id = tc.get("id", "")
        if tool_name in tools_dict:
            try:
                result = tools_dict[tool_name].invoke(tool_args)
                result_str = str(result)
            except Exception as e:
                result_str = f"工具执行错误: {e!s}"
        else:
            result_str = f"未知工具: {tool_name}"
        tool_messages.append(ToolMessage(content=result_str, tool_call_id=tool_call_id))
    return {"messages": tool_messages, "next_step": "continue"}


def should_continue(state):
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"


def _build_graph(tools):
    builder = StateGraph(dict)
    builder.add_node("agent", lambda state: call_llm(state, create_llm(), tools))
    builder.add_node("tools", lambda state: call_tool(state, {t.name: t for t in tools}))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {
        "tools": "tools",
        "end": END,
    })
    builder.add_edge("tools", "agent")
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


graph = _build_graph(get_all_tools())
