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


def print_tool_list():
    table = Table(title="Available Tools", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Tool", style="cyan")
    table.add_column("Description")
    for tool in get_all_tools():
        table.add_row(tool.name, tool.description.split("\n")[0])
    console.print(table)
    console.print()


def print_help():
    help_text = """
**Commands:**
- `/tools`  - List all available tools
- `/clear`  - Clear screen
- `/help`   - Show this help
- `/exit`   - Exit program
    """
    console.print(Markdown(help_text))


def main():
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    if not settings.is_deepseek_configured:
        console.print(
            Panel(
                "[yellow]WARNING: DeepSeek API Key not configured![/yellow]\n\n"
                "Edit [bold].env[/bold] and set [bold]DEEPSEEK_API_KEY[/bold]=your_key\n"
                "Get one at [blue]https://platform.deepseek.com/[/blue]",
                title="Configuration Required",
                border_style="yellow",
                expand=False,
            )
        )
        console.print()

    print_banner()

    console.print("[dim]Initializing DeepAgent (Official SDK)...[/dim]")
    try:
        agent = get_agent()
        console.print("[green]DeepAgent is ready![/green]\n")
    except Exception as e:
        console.print(f"[red]Agent initialization failed: {e}[/red]")
        sys.exit(1)

    console.print("Type [bold]/help[/bold] for commands\n", style="dim")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        except EOFError:
            break

        if not user_input.strip():
            continue

        cmd = user_input.strip().lower()
        if cmd == "/exit":
            console.print("[yellow]Goodbye![/yellow]")
            break
        elif cmd == "/help":
            print_help()
            continue
        elif cmd == "/tools":
            print_tool_list()
            continue
        elif cmd == "/clear":
            console.clear()
            print_banner()
            continue

        console.print("[dim]DeepAgent is thinking...[/dim]")

        try:
            with console.status("[bold green]Processing...", spinner="dots"):
                response = run_agent(agent, user_input)

            console.print()
            console.print(
                Panel(
                    Markdown(response),
                    title="[bold green]DeepAgent[/bold green]",
                    border_style="green",
                    title_align="left",
                )
            )
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            continue
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")
            continue


if __name__ == "__main__":
    main()
