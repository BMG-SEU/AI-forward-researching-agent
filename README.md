# AI Frontier Explorer 🧠🔍

> Track cutting-edge AI research, deep-read papers, and generate plain-language reports — powered by DeepSeek + LangChain.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![Deep Agents SDK](https://img.shields.io/badge/Deep%20Agents%20SDK-0.7.0-green.svg)](https://docs.langchain.com/oss/python/deepagents/overview)

## ✨ Features

- **📡 Track** — Search arXiv for the latest papers on any AI topic
- **📖 Deep Read** — Fetch full paper content via web scraping
- **🤖 Parallel Sub-agents** — Delegate paper analysis to sub-agents for concurrent reading
- **📝 Structured Reports** — Auto-generate reports with: summary, key points, plain-language explanation, glossary, impact score
- **💾 Persistent Memory** — Remembers your preferences across conversations
- **🎯 Skills System** — Built-in AI research methodology

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- API Keys: [DeepSeek](https://platform.deepseek.com/) + [LangSmith](https://smith.langchain.com/)

### 1. Install

```bash
git clone https://github.com/your-username/ai-frontier-explorer
cd ai-frontier-explorer
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure

Create `.env` file. On Windows PowerShell, use `Set-Content` so the file encoding is explicit:

```powershell
"DEEPSEEK_API_KEY=sk-your_deepseek_key" | Set-Content -Encoding utf8 .env
```

The CLI also accepts UTF-16 `.env` files produced by Windows PowerShell 5. Full example:

```env
DEEPSEEK_API_KEY=sk-your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_key
LANGCHAIN_PROJECT=ai-frontier-explorer
```

### 3. Launch

```bash
# One-click (Windows)
start.bat

# Or manually
python ai_frontier.py
```

## 🎮 Usage

```
╔══════════════════════════════════════════╗
║    AI Frontier Explorer  v1.0            ║
║   追踪前沿 · 深度研读 · 通俗报告          ║
╚══════════════════════════════════════════╝

You > /track AI Agent 最新进展
You > /track 多模态大模型 2026
You > /search transformer architecture
You > /reports
You > /read 2026-07-30-AI-Agent-前沿进展追踪.md
You > /remember 我关注AI安全方向
```

### Commands

| Command | Description |
|---------|-------------|
| `/track <topic>` | Track frontier research on a topic |
| `/search <query>` | Quick arXiv search |
| `/reports` | List generated reports |
| `/read <file>` | Read a saved report |
| `/remember <info>` | Save a preference to memory |
| `/tools` | List available tools |
| `/help` | Show help |
| `/exit` | Exit |

## 🧠 Architecture

```
ai_frontier.py          # CLI entry point
deep_agent/
  ├── agent.py          # create_deep_agent() with DeepSeek model
  ├── config.py         # Settings management
  └── llm.py            # LLM initialization
tools/
  ├── arxiv_tools.py    # arXiv paper search
  ├── web_tools.py      # Web page content extraction
  ├── report_tools.py   # Save reports to disk
  ├── search.py         # DuckDuckGo web search
  └── calculator.py     # Safe calculator
skills/
  └── ai-research/      # Research methodology skill
memories/               # Persistent memory files
reports/                # Generated reports output
```

## 🔧 Tech Stack

- **Agent Framework**: [Deep Agents SDK](https://docs.langchain.com/oss/python/deepagents/overview) (official)
- **Orchestration**: LangGraph
- **LLM**: DeepSeek via OpenAI-compatible API
- **Memory**: LangGraph StoreBackend
- **CLI**: Rich terminal UI

## 📄 Report Format

Each generated report includes:

- **Name** — Paper title
- **Domain** — AI subfield (NLP/CV/RL/Agent/LLM...)
- **Summary** — What the paper does
- **Key Points** — 3-5 core insights
- **Plain Explanation** — Easy-to-understand analogy-based explanation
- **Glossary** — Technical term definitions
- **Impact Score** — 1-10 rating with breakdown

## 📦 Install as a Package

```bash
pip install -e .
ai-frontier     # launch from anywhere
```

## 📜 License

MIT
