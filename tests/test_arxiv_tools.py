import httpx

from tools import arxiv_tools

ATOM = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'>
  <entry><title> A  Paper </title><summary>Useful work</summary>
  <published>2026-07-30T00:00:00Z</published><updated>2026-07-30T00:00:00Z</updated>
  <author><name>Alice</name></author>
  <link href='https://arxiv.org/abs/2607.00001'/>
  <link title='pdf' href='https://arxiv.org/pdf/2607.00001'/>
  <category term='cs.AI'/></entry>
</feed>"""


def test_search_arxiv_uses_encoded_params(monkeypatch):
    captured = {}
    def fake_get(url, **kwargs):
        request = httpx.Request("GET", url, params=kwargs["params"])
        captured["url"] = str(request.url)
        return httpx.Response(200, text=ATOM, request=request)
    monkeypatch.setattr(arxiv_tools.httpx, "get", fake_get)

    papers = arxiv_tools.search_arxiv("agent safety & alignment", max_results=999)

    assert "agent+safety+%26+alignment" in captured["url"]
    assert "max_results=50" in captured["url"]
    assert papers[0]["title"] == "A Paper"
    assert papers[0]["arxiv_id"] == "2607.00001"
