# DeepAgent 实操项目

基于 **Deep Agents SDK（官方）+ LangGraph + DeepSeek** 构建的深度智能体。

## Tech Stack

| Component     | Technology                   |
|---------------|------------------------------|
| Agent SDK     | Deep Agents v0.7.0 (official)|
| Orchestration | LangGraph                    |
| LLM API       | DeepSeek (via ChatOpenAI)    |
| Tools         | Calculator + DuckDuckGo Search |
| Terminal UI   | Rich                         |

## Quick Start

### 1. Configure API Keys

Edit `.env`:

```env
DEEPSEEK_API_KEY=sk-your_deepseek_key
LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_key
```

### 2. Install & Run

```bash
cd DeepAgent
.venv\Scripts\activate
pip install -r requirements.txt
python -m deep_agent.main
```

### 3. Usage

```
You > Calculate 2^10 + pi
You > Search latest AI news
You > /tools
You > /exit
```

## Project Structure

```
DeepAgent/
├── deep_agent/
│   ├── __init__.py
│   ├── agent.py         # create_deep_agent() 构建
│   ├── config.py        # Settings
│   ├── llm.py           # DeepSeek via ChatOpenAI
│   ├── main.py          # CLI entry
│   └── studio.py        # LangGraph Studio entry
├── tools/
│   ├── __init__.py      # Tool registry
│   ├── calculator.py    # Safe calculator
│   └── search.py        # DuckDuckGo search
├── .env
├── requirements.txt
└── pyproject.toml
```

## LangGraph Studio

```bash
npx @langchain/langgraph-cli dev
```
