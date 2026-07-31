"""LLM 初始化 - 配置 DeepSeek API（OpenAI 兼容接口）"""

from langchain_openai import ChatOpenAI
from deep_agent.config import settings


def create_llm() -> ChatOpenAI:
    """
    创建 DeepSeek Chat 模型实例。

    DeepSeek 提供 OpenAI 兼容 API，使用 langchain-openai 即可调用。
    """
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.7,
        timeout=settings.agent_max_execution_time,
        max_retries=2,
    )


def create_deep_research_llm() -> ChatOpenAI:
    """
    创建用于深度研究的 LLM 实例（更低温度，更确定性的输出）。
    """
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.1,
        timeout=settings.agent_max_execution_time,
        max_retries=3,
    )
