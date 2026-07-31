"""arXiv 论文搜索工具。"""

from typing import Dict, List
from xml.etree import ElementTree

import httpx

ARXIV_QUERY_URL = "https://export.arxiv.org/api/query"
ARXIV_BASE = "https://arxiv.org"


def search_arxiv(query: str, max_results: int = 10, sort_by: str = "submittedDate") -> List[Dict]:
    """使用参数化请求搜索 arXiv，避免手工拼接查询字符串。"""
    if not query.strip():
        return [{"error": "搜索关键词不能为空"}]
    max_results = max(1, min(int(max_results), 50))
    sort_param = sort_by if sort_by in {"submittedDate", "relevance"} else "submittedDate"
    params = {
        "search_query": f"all:{query.strip()}",
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_param,
        "sortOrder": "descending",
    }
    try:
        response = httpx.get(ARXIV_QUERY_URL, params=params, timeout=30, follow_redirects=True)
        response.raise_for_status()
        root = ElementTree.fromstring(response.text)
    except (httpx.HTTPError, ElementTree.ParseError) as exc:
        return [{"error": f"搜索 arXiv 失败: {exc!s}"}]

    ns = {"a": "http://www.w3.org/2005/Atom"}
    papers = []
    for entry in root.findall("a:entry", ns):
        paper = {
            "title": _clean(entry.find("a:title", ns)),
            "summary": _clean(entry.find("a:summary", ns))[:800],
            "published": _clean(entry.find("a:published", ns))[:10],
            "updated": _clean(entry.find("a:updated", ns))[:10],
            "authors": [_clean(a.find("a:name", ns)) for a in entry.findall("a:author", ns)],
            "link": "", "pdf_link": "", "categories": [], "arxiv_id": "",
        }
        for link in entry.findall("a:link", ns):
            href = link.attrib.get("href", "")
            if link.attrib.get("title") == "pdf":
                paper["pdf_link"] = href
                paper["arxiv_id"] = href.split("/")[-1].replace(".pdf", "")
            elif "/abs/" in href:
                paper["link"] = href
                paper["arxiv_id"] = paper["arxiv_id"] or href.split("/")[-1]
        paper["categories"] = [cat.attrib.get("term", "") for cat in entry.findall("a:category", ns)]
        papers.append(paper)
    return papers


def get_arxiv_paper_details(arxiv_id: str) -> Dict:
    """获取单篇论文的详情页地址。"""
    safe_id = arxiv_id.strip().replace("/", "")
    if not safe_id:
        return {"error": "arXiv ID 不能为空"}
    try:
        resp = httpx.get(f"{ARXIV_BASE}/abs/{safe_id}", timeout=15, follow_redirects=True)
        resp.raise_for_status()
        return {"id": safe_id, "abstract_url": str(resp.url)}
    except httpx.HTTPError as exc:
        return {"error": f"获取失败: {exc!s}"}


def _clean(element) -> str:
    return " ".join(element.text.split()) if element is not None and element.text else ""
