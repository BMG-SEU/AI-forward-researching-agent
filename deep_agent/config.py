"""配置管理 - 使用 pydantic-settings 从 .env 加载"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件加载"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # DeepSeek API 配置
    # 官方文档: https://api-docs.deepseek.com/
    # Base URL: https://api.deepseek.com (OpenAI SDK 自动拼接 /v1 路径)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"  # 或 deepseek-v4-pro

    # LangSmith 追踪（可选）
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "deepagent-practice"

    # Agent 行为配置
    agent_max_iterations: int = 15
    agent_max_execution_time: int = 120  # 秒

    @property
    def is_deepseek_configured(self) -> bool:
        """检查 DeepSeek API 是否已配置"""
        return bool(self.deepseek_api_key) and self.deepseek_api_key != "your_deepseek_api_key_here"


# 全局单例
settings = Settings()
