from deep_agent.viz import export_mermaid


class Drawable:
    def draw_mermaid(self):
        return "graph TD; A-->B"


class FakeGraph:
    def get_graph(self):
        return Drawable()


def test_export_mermaid_with_supplied_graph(tmp_path):
    output = tmp_path / "graph.mmd"
    value = export_mermaid(FakeGraph(), output)
    assert value == "graph TD; A-->B"
    assert output.read_text(encoding="utf-8") == value
