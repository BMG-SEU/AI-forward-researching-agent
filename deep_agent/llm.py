"""LLM 初始化 - 配置 DeepSeek API（OpenAI 兼容接口）"""

from langchain_openai import ChatOpenAI
from deep_agent.config import settings


def create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.7,
        timeout=60,
        max_retries=2,
    )


def create_deep_research_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.1,
        timeout=120,
        max_retries=3,
    )
