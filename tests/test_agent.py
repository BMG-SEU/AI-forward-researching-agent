from langchain_core.messages import AIMessage

from deep_agent import agent as agent_module


class DummyAgent:
    def __init__(self):
        self.config = None
    def invoke(self, payload, config):
        self.config = config
        return {"messages": [AIMessage(content="done")]}


def test_run_agent_applies_thread_and_recursion_limit(monkeypatch):
    dummy = DummyAgent()
    monkeypatch.setattr(agent_module.settings, "agent_recursion_limit", 100)
    monkeypatch.setattr(agent_module.settings, "agent_max_execution_time", 2)
    assert agent_module.run_agent(dummy, "hello", thread_id="thread-7") == "done"
    assert dummy.config["configurable"]["thread_id"] == "thread-7"
    assert dummy.config["recursion_limit"] == 100


def test_sqlite_checkpointer_is_cached(tmp_path, monkeypatch):
    agent_module._create_checkpointer.cache_clear()
    monkeypatch.setattr(agent_module.settings, "checkpoint_db", str(tmp_path / "state.sqlite"))
    first = agent_module._create_checkpointer()
    second = agent_module._create_checkpointer()
    assert first is second
    assert (tmp_path / "state.sqlite").exists()
    agent_module._create_checkpointer.cache_clear()

def test_runtime_resources_are_copied_without_overwriting(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_module.settings, "ai_frontier_home", str(tmp_path))
    agent_module._ensure_runtime_files()
    agents_file = tmp_path / "memories" / "AGENTS.md"
    preference = tmp_path / "memories" / "preferences.md"
    skill = tmp_path / "skills" / "ai-research" / "SKILL.md"
    assert agents_file.is_file()
    assert preference.is_file()
    assert skill.is_file()

    preference.write_text("custom memory", encoding="utf-8")
    agent_module._ensure_runtime_files()
    assert preference.read_text(encoding="utf-8") == "custom memory"

def test_composite_backend_reads_agents_file(tmp_path, monkeypatch):
    from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend

    monkeypatch.setattr(agent_module.settings, "ai_frontier_home", str(tmp_path))
    agent_module._ensure_runtime_files()
    files = FilesystemBackend(root_dir=tmp_path / "memories", virtual_mode=True)
    backend = CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": files},
    )

    result = backend.read("/memories/AGENTS.md")
    assert result.error is None
    assert "DeepAgent Memory" in result.file_data["content"]
