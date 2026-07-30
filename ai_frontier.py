"""AI 前沿探索 Agent — 独立 CLI 入口"""

import sys
import signal
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from pathlib import Path

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
    banner = r"""
   ╔══════════════════════════════════════════╗
   ║    AI Frontier Explorer  v1.0            ║
   ║   追踪前沿 · 深度研读 · 通俗报告          ║
   ╚══════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print(f"  Model: {settings.deepseek_model}", style="dim")
    console.print(f"  Tools: {', '.join(get_tool_names())}", style="dim")
    console.print(f"  Reports: {Path('reports').absolute()}", style="dim")
    console.print()


def show_status():
    """显示当前状态"""
    reports = sorted(Path("reports").glob("*.md"))
    table = Table(title="📊 已有报告", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("文件名", style="cyan")
    table.add_column("大小")
    for r in reports[-10:]:
        size = r.stat().st_size
        table.add_row(r.name, f"{size}B" if size < 1024 else f"{size//1024}KB")
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
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

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
        elif cmd == "/help":
            print_help()
            continue
        elif cmd == "/tools":
            table = Table(box=box.ROUNDED, header_style="bold magenta")
            table.add_column("Tool", style="cyan")
            table.add_column("Description")
            for t in get_all_tools():
                name = t.name if hasattr(t, "name") else t.__name__
                desc = t.description if hasattr(t, "description") else ""
                table.add_row(name, desc.split("\n")[0][:80])
            console.print(table)
            continue
        elif cmd == "/reports":
            show_status()
            continue
        elif cmd.startswith("/read "):
            fname = cmd[6:].strip()
            path = Path("reports") / fname
            if path.exists():
                console.print(Panel(path.read_text(encoding="utf-8"),
                              title=f"📄 {fname}", border_style="blue"))
            else:
                console.print(f"[red]报告 {fname} 不存在[/red]")
            continue
        elif cmd.startswith("/remember "):
            agent = get_agent()
            resp = run_agent(agent, f"请记住：{cmd[10:]}")
            console.print(Panel(resp, title="DeepAgent", border_style="green"))
            continue
        elif cmd.startswith("/search "):
            agent = get_agent()
            resp = run_agent(agent, f"用 search_arxiv 搜索 {cmd[8:]}")
            console.print(Panel(Markdown(resp), title="搜索结果", border_style="blue"))
            continue
        elif cmd.startswith("/track "):
            topic = cmd[7:]
            agent = get_agent()
            console.print(f"\n[bold cyan]🎯 开始追踪: {topic}[/bold cyan]")
            console.print("[dim]这可能需要几分钟...[/dim]\n")

            with console.status("[bold green]搜索→研读→报告中...", spinner="dots"):
                resp = run_agent(agent, f"请帮我追踪 AI 前沿主题：{topic}。按照你的工作流程，搜索论文、深度研读，然后生成结构化报告保存到 reports/ 目录。")

            console.print()
            console.print(Panel(Markdown(resp), title="✅ 追踪完成", border_style="green"))
            show_status()
            continue

        # 普通对话
        agent = get_agent()
        with console.status("[bold green]思考中...", spinner="dots"):
            resp = run_agent(agent, cmd)
        console.print()
        console.print(Panel(Markdown(resp), title="DeepAgent", border_style="green"))
        console.print()


if __name__ == "__main__":
    main()
