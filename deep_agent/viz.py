"""辅助可视化模块"""

from rich.console import Console
from rich.tree import Tree


def print_structure():
    tree = Tree("DeepAgent")
    tree.add("deep_agent/")
    tree.add("tools/")
    tree.add("memories/")
    tree.add("skills/")
    console = Console()
    console.print(tree)
