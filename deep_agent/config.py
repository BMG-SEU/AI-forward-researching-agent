"""应用配置与兼容的 .env 加载。

API key 等敏感配置会持久化到用户数据目录（data_dir/config.json），
这样即使更新包、更换运行目录，配置也不会丢失。
读取优先级（从高到低）：
1. 真实环境变量
2. data_dir/config.json 持久化配置
3. 当前目录 .env 文件（首次运行时自动迁移到持久化配置）
"""

import json
import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 支持持久化到 config.json 的设置字段（小写 pydantic 字段名）
PERSISTED_FIELDS = (
    "deepseek_api_key",
    "deepseek_base_url",
    "deepseek_model",
    "reports_dir",
)


def _compute_data_dir() -> Path:
    """计算用户可写的持久数据目录（不依赖 Settings 实例）。"""
    ai_frontier_home = os.environ.get("AI_FRONTIER_HOME", "").strip()
    if ai_frontier_home:
        return Path(ai_frontier_home).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return (base / "ai-frontier-explorer").resolve()


def _config_file() -> Path:
    return _compute_data_dir() / "config.json"


def _load_persisted() -> dict:
    try:
        data = json.loads(_config_file().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def load_persisted_config() -> None:
    """把 data_dir/config.json 中持久化的设置合并进环境变量（不覆盖已有 env）。"""
    for key, value in _load_persisted().items():
        if value is None:
            continue
        # 环境变量名大小写不敏感；已存在则跳过，保持真实 env 优先级最高
        if not any(existing.upper() == key.upper() for existing in os.environ):
            os.environ[key] = str(value)


def save_settings(values: dict) -> None:
    """将一组设置持久化到 data_dir/config.json。"""
    data = _load_persisted()
    for key, value in values.items():
        if key not in PERSISTED_FIELDS:
            raise ValueError(f"不支持持久化的配置项: {key}")
        if value is None:
            data.pop(key, None)
        else:
            data[key] = str(value)
    _config_file().parent.mkdir(parents=True, exist_ok=True)
    _config_file().write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _detect_env_encoding(path: Path) -> str:
    """识别 PowerShell 生成的 UTF-16 .env 以及常见 UTF-8 格式。"""
    prefix = path.read_bytes()[:4]
    if prefix.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"
    if prefix.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    return "utf-8"


def load_dotenv_compat(path: Path | None = None) -> None:
    """加载 .env 并迁移到持久化配置（若持久化中还没有对应值）。"""
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

    persisted = _load_persisted()
    migrate = {}
    for key, value in values.items():
        if not key or value is None:
            continue
        # 环境变量已存在时不覆盖
        if not any(existing.upper() == key.upper() for existing in os.environ):
            os.environ.setdefault(key, value)
        # 迁移到持久化：字段属于持久化范围，且持久化中没有，且 .env 里有值
        field = key.lower()
        if field in PERSISTED_FIELDS and field not in persisted and value:
            migrate[field] = value
    if migrate:
        save_settings(migrate)


load_dotenv_compat()
load_persisted_config()


class Settings(BaseSettings):
    """应用配置；环境变量优先，持久化配置次之，.env 兜底。"""

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
    # 报告输出目录，可单独覆盖；留空则默认 data_dir/reports
    reports_dir_override: str = Field(default="", validation_alias="REPORTS_DIR")

    @property
    def resource_root(self) -> Path:
        """wheel 内只读的默认技能和记忆模板。"""
        return Path(__file__).resolve().parent / "resources"

    @property
    def data_dir(self) -> Path:
        """用户可写的持久数据目录，可由 AI_FRONTIER_HOME 覆盖。"""
        if self.ai_frontier_home:
            return Path(self.ai_frontier_home).expanduser().resolve()
        return _compute_data_dir()

    @property
    def reports_dir(self) -> Path:
        """报告输出目录；REPORTS_DIR 环境变量优先，否则 data_dir/reports。"""
        if self.reports_dir_override:
            return Path(self.reports_dir_override).expanduser().resolve()
        return self.data_dir / "reports"

    @property
    def checkpoint_path(self) -> Path:
        path = Path(self.checkpoint_db).expanduser()
        return path.resolve() if path.is_absolute() else self.data_dir / path

    @property
    def is_deepseek_configured(self) -> bool:
        return bool(self.deepseek_api_key) and self.deepseek_api_key != "your_deepseek_api_key_here"


settings = Settings()
