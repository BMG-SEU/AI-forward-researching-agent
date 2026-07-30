"""网页全文抓取工具"""

import httpx
import re
from typing import Optional


def fetch_webpage(url: str, max_length: int = 10000) -> str:
    """
    抓取网页内容并提取正文文本。

    Args:
        url: 网页 URL
        max_length: 最大返回字符数

    Returns:
        网页纯文本内容
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
        response.raise_for_status()

        text = response.text

        # 尝试提取 <article> 或 <main> 内容
        article_match = re.search(
            r"<article[^>]*>(.*?)</article>", text, re.DOTALL | re.IGNORECASE
        )
        main_match = re.search(
            r"<main[^>]*>(.*?)</main>", text, re.DOTALL | re.IGNORECASE
        )
        body_match = re.search(
            r"<body[^>]*>(.*?)</body>", text, re.DOTALL | re.IGNORECASE
        )

        content = ""
        if article_match:
            content = article_match.group(1)
        elif main_match:
            content = main_match.group(1)
        elif body_match:
            content = body_match.group(1)
        else:
            content = text

        # 去除 HTML 标签
        content = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)
        content = re.sub(r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL)
        content = re.sub(r"<[^>]+>", " ", content)
        content = re.sub(r"\s+", " ", content).strip()

        if len(content) > max_length:
            content = content[:max_length] + "\n\n... [内容已截断]"

        return content or "无法提取页面内容"

    except httpx.TimeoutException:
        return f"请求超时: {url}"
    except httpx.HTTPStatusError as e:
        return f"HTTP 错误 ({e.response.status_code}): {url}"
    except Exception as e:
        return f"抓取失败: {e!s}"
