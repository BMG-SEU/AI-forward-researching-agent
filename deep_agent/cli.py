"""AI 前沿探索 Agent — 命令行入口。"""

import signal
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from deep_agent import __version__
from deep_agent.agent import build_agent, run_agent
from deep_agent.config import settings
from tools import get_all_tools, get_tool_names
from tools.report_tools import get_reports_dir

console = Console()
_agent = None


def _reports_dir():
    """动态读取当前报告目录。"""
    return get_reports_dir()


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def execute_agent(message: str, status: str = "思考中...") -> str | None:
    """运行 Agent，并让运行时错误不再终止整个 CLI。"""
    try:
        with console.status(f"[bold green]{status}", spinner="dots"):
            return run_agent(get_agent(), message)
    except KeyboardInterrupt:
        console.print("\n[yellow]任务已中断，程序仍可继续使用。[/yellow]")
    except Exception as exc:
        console.print(Panel(
            f"[red]{type(exc).__name__}: {exc}[/red]\n\n"
            "程序未退出。你可以调整关键词后重试，或输入 /help 查看命令。",
            title="任务执行失败",
            border_style="red",
        ))
    return None


def print_banner():
    banner = r"""
   ╔══════════════════════════════════════════╗
   ║    AI Frontier Explorer                  ║
   ║   追踪前沿 · 深度研读 · 通俗报告          ║
   ╚══════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print(f"  Version: {__version__}", style="dim")
    console.print(f"  Model: {settings.deepseek_model}", style="dim")
    console.print(f"  Tools: {', '.join(get_tool_names())}", style="dim")
    console.print(f"  Reports: {_reports_dir()}", style="dim")
    console.print()


def show_status():
    """显示最近生成的报告。"""
    reports = sorted(_reports_dir().glob("*.md"))
    table = Table(title="📊 已有报告", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("文件名", style="cyan")
    table.add_column("大小")
    for report in reports[-10:]:
        size = report.stat().st_size
        table.add_row(report.name, f"{size}B" if size < 1024 else f"{size // 1024}KB")
    if reports:
        console.print(table)
    else:
        console.print("[dim]暂无报告，开始你的第一次追踪吧！[/dim]")
    console.print()


def print_help():
    console.print(Markdown("""
**命令:**
- `/track <主题>` — 开始追踪一个 AI 前沿主题
- `/reports` — 查看已有报告
- `/read <文件名>` — 阅读某份报告
- `/search <关键词>` — 快速搜索论文
- `/remember <内容>` — 让 Agent 记住你的偏好
- `/tools` — 查看所有工具
- `/help` — 帮助
- `/exit` — 退出

**示例:**
- `/track AI Agent 最新进展`
- `/search large language model reasoning`
- `/read 2026-07-30-AI-Agent进展.md`
"""))


def main():
    signal.signal(signal.SIGINT, lambda _signal, _frame: sys.exit(0))
    if not settings.is_deepseek_configured:
        console.print("[yellow]请先配置 .env 中的 DEEPSEEK_API_KEY[/yellow]")
        sys.exit(1)

    print_banner()
    show_status()
    console.print("输入 [bold]/track <主题>[/bold] 开始追踪\n", style="dim")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        except EOFError:
            break
        if not user_input.strip():
            continue
        cmd = user_input.strip()

        if cmd == "/exit":
            console.print("[yellow]再见！[/yellow]")
            break
        if cmd == "/help":
            print_help()
            continue
        if cmd == "/tools":
            table = Table(box=box.ROUNDED, header_style="bold magenta")
            table.add_column("Tool", style="cyan")
            table.add_column("Description")
            for tool in get_all_tools():
                name = tool.name if hasattr(tool, "name") else tool.__name__
                description = tool.description if hasattr(tool, "description") else ""
                table.add_row(name, description.split("\n")[0][:80])
            console.print(table)
            continue
        if cmd == "/reports":
            show_status()
            continue
        if cmd.startswith("/read "):
            filename = cmd[6:].strip()
            path = _reports_dir() / Path(filename).name
            if path.exists():
                console.print(Panel(path.read_text(encoding="utf-8"), title=f"📄 {filename}", border_style="blue"))
            else:
                console.print(f"[red]报告 {filename} 不存在[/red]")
            continue
        if cmd.startswith("/remember "):
            response = execute_agent(f"请记住：{cmd[10:]}", "保存记忆中...")
            if response is not None:
                console.print(Panel(response, title="DeepAgent", border_style="green"))
            continue
        if cmd.startswith("/search "):
            response = execute_agent(f"用 search_arxiv 搜索 {cmd[8:]}", "搜索论文中...")
            if response is not None:
                console.print(Panel(Markdown(response), title="搜索结果", border_style="blue"))
            continue
        if cmd.startswith("/track "):
            topic = cmd[7:]
            console.print(f"\n[bold cyan]🎯 开始追踪: {topic}[/bold cyan]")
            console.print("[dim]这可能需要几分钟...[/dim]\n")
            response = execute_agent(
                f"请帮我追踪 AI 前沿主题：{topic}。按照你的工作流程，搜索论文、深度研读，然后生成结构化报告保存到 reports/ 目录。",
                "搜索→研读→报告中...",
            )
            if response is not None:
                console.print(Panel(Markdown(response), title="✅ 追踪完成", border_style="green"))
                show_status()
            continue

        response = execute_agent(cmd)
        if response is not None:
            console.print(Panel(Markdown(response), title="DeepAgent", border_style="green"))
            console.print()


if __name__ == "__main__":
    main()