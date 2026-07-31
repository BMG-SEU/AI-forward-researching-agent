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
    monkeypatch.setattr(agent_module.settings, "agent_max_iterations", 9)
    monkeypatch.setattr(agent_module.settings, "agent_max_execution_time", 2)
    assert agent_module.run_agent(dummy, "hello", thread_id="thread-7") == "done"
    assert dummy.config["configurable"]["thread_id"] == "thread-7"
    assert dummy.config["recursion_limit"] == 9


def test_sqlite_checkpointer_is_cached(tmp_path, monkeypatch):
    agent_module._create_checkpointer.cache_clear()
    monkeypatch.setattr(agent_module.settings, "checkpoint_db", str(tmp_path / "state.sqlite"))
    first = agent_module._create_checkpointer()
    second = agent_module._create_checkpointer()
    assert first is second
    assert (tmp_path / "state.sqlite").exists()
    agent_module._create_checkpointer.cache_clear()
