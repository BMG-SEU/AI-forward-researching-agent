"""应用配置与兼容的 .env 加载。"""

import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict


def _detect_env_encoding(path: Path) -> str:
    """识别 PowerShell 生成的 UTF-16 .env 以及常见 UTF-8 格式。"""
    prefix = path.read_bytes()[:4]
    if prefix.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"
    if prefix.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    return "utf-8"


def load_dotenv_compat(path: Path | None = None) -> None:
    """加载当前目录的 .env，并兼容 Windows PowerShell 5 的 UTF-16 输出。"""
    env_path = path or Path.cwd() / ".env"
    if not env_path.is_file():
        return
    encoding = _detect_env_encoding(env_path)
    try:
        values = dotenv_values(env_path, encoding=encoding)
    except UnicodeDecodeError as exc:
        raise RuntimeError(
            f"无法读取 {env_path}。请将文件保存为 UTF-8 或 UTF-16。"
        ) from exc
    for key, value in values.items():
        if key and value is not None:
            os.environ.setdefault(key, value)


load_dotenv_compat()


class Settings(BaseSettings):
    """应用配置；环境变量优先，.env 已在模块加载时兼容读取。"""

    model_config = SettingsConfigDict(extra="ignore")

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "deepagent-practice"

    agent_max_iterations: int = 15  # 兼容旧配置
    agent_recursion_limit: int = 100
    agent_max_execution_time: int = 600
    agent_thread_id: str = "default"
    checkpoint_db: str = "checkpoints.sqlite"
    ai_frontier_home: str = ""

    @property
    def resource_root(self) -> Path:
        """wheel 内只读的默认技能和记忆模板。"""
        return Path(__file__).resolve().parent / "resources"

    @property
    def data_dir(self) -> Path:
        """用户可写的持久数据目录，可由 AI_FRONTIER_HOME 覆盖。"""
        if self.ai_frontier_home:
            return Path(self.ai_frontier_home).expanduser().resolve()
        if os.name == "nt":
            base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        else:
            base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        return (base / "ai-frontier-explorer").resolve()

    @property
    def reports_dir(self) -> Path:
        return self.data_dir / "reports"

    @property
    def checkpoint_path(self) -> Path:
        path = Path(self.checkpoint_db).expanduser()
        return path.resolve() if path.is_absolute() else self.data_dir / path

    @property
    def is_deepseek_configured(self) -> bool:
        return bool(self.deepseek_api_key) and self.deepseek_api_key != "your_deepseek_api_key_here"


settings = Settings()