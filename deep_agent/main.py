"""CLI 主入口 - DeepAgent 交互式命令行界面（官方 SDK 版）"""

import sys
import signal

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from deep_agent.config import settings
from deep_agent.agent import build_agent, run_agent
from tools import get_all_tools, get_tool_names

console = Console()

_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def print_banner():
    banner = """
   ╔══════════════════════════════════════════╗
   ║      DeepAgent  (Official SDK)           ║
   ║   LangChain · Deep Agents · DeepSeek     ║
   ╚══════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print(f"  Model: {settings.deepseek_model}", style="dim")
    console.print(f"  Base:  {settings.deepseek_base_url}", style="dim")
    console.print(f"  Tools: {', '.join(get_tool_names())}", style="dim")
    console.print(f"  SDK:   deepagents v0.7.0", style="dim")
    console.print()
