from contextlib import nullcontext

from deep_agent import cli


def test_execute_agent_returns_response(monkeypatch):
    monkeypatch.setattr(cli, "get_agent", lambda: object())
    monkeypatch.setattr(cli, "run_agent", lambda agent, message: "ok")
    monkeypatch.setattr(cli.console, "status", lambda *args, **kwargs: nullcontext())
    assert cli.execute_agent("hello") == "ok"


def test_execute_agent_catches_runtime_error(monkeypatch):
    monkeypatch.setattr(cli, "get_agent", lambda: object())
    monkeypatch.setattr(cli.console, "status", lambda *args, **kwargs: nullcontext())
    printed = []
    monkeypatch.setattr(cli.console, "print", lambda *args, **kwargs: printed.append(args))

    def fail(agent, message):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "run_agent", fail)
    assert cli.execute_agent("hello") is None
    assert printed