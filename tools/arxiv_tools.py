"""arXiv 论文搜索工具"""

import httpx
from typing import List, Dict
from xml.etree import ElementTree

ARXIV_QUERY_URL = "http://export.arxiv.org/api/query"
ARXIV_BASE = "https://arxiv.org"


def search_arxiv(
    query: str,
    max_results: int = 10,
    sort_by: str = "submittedDate",
) -> List[Dict]:
    sort_map = {"submittedDate": "submittedDate", "relevance": "relevance"}
    sort_param = sort_map.get(sort_by, "submittedDate")

    url = (
        f"{ARXIV_QUERY_URL}?search_query=all:{query}"
        f"&start=0&max_results={max_results}"
        f"&sortBy={sort_param}&sortOrder=descending"
    )

    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        return [{"error": f"搜索 arXiv 失败: {e!s}"}]

    root = ElementTree.fromstring(response.text)
    ns = {"a": "http://www.w3.org/2005/Atom"}

    papers = []
    for entry in root.findall("a:entry", ns):
        paper = {
            "title": _clean(entry.find("a:title", ns)),
            "summary": _clean(entry.find("a:summary", ns))[:800],
            "published": _clean(entry.find("a:published", ns))[:10],
            "updated": _clean(entry.find("a:updated", ns))[:10],
            "authors": [
                _clean(a.find("a:name", ns))
                for a in entry.findall("a:author", ns)
            ],
            "link": "",
            "pdf_link": "",
            "categories": [],
            "arxiv_id": "",
        }

        for link in entry.findall("a:link", ns):
            href = link.attrib.get("href", "")
            title_attr = link.attrib.get("title", "")
            if title_attr == "pdf":
                paper["pdf_link"] = href
                paper["arxiv_id"] = href.split("/")[-1].replace(".pdf", "")
            elif "abs" in href:
                paper["link"] = href
                if not paper["arxiv_id"]:
                    paper["arxiv_id"] = href.split("/")[-1]

        for cat in entry.findall("a:category", ns):
            paper["categories"].append(cat.attrib.get("term", ""))

        papers.append(paper)

    return papers


def get_arxiv_paper_details(arxiv_id: str) -> Dict:
    try:
        resp = httpx.get(f"{ARXIV_BASE}/abs/{arxiv_id}", timeout=15)
        resp.raise_for_status()
        return {"id": arxiv_id, "abstract_url": f"{ARXIV_BASE}/abs/{arxiv_id}"}
    except Exception as e:
        return {"error": f"获取失败: {e!s}"}


def _clean(element) -> str:
    return element.text.strip() if element is not None and element.text else ""
