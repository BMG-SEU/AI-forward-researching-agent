"""兼容旧入口：实际 CLI 实现在 deep_agent.cli。"""

from deep_agent.cli import main

__all__ = ["main"]


if __name__ == "__main__":
    main()