"""网页正文抓取工具。"""

from html.parser import HTMLParser
import ipaddress
import socket
from urllib.parse import urlparse

import httpx


class _ReadableTextParser(HTMLParser):
    """提取可见文本，忽略脚本、样式和模板内容。"""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript", "template", "svg"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "template", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self.parts.append(data.strip())


def _validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("仅支持有效的 HTTP/HTTPS URL")
    if parsed.username or parsed.password:
        raise ValueError("URL 不允许包含认证信息")
    if parsed.hostname.lower() == "localhost":
        raise ValueError("不允许访问本地地址")
    for info in socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM):
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            raise ValueError("不允许访问内网或保留地址")


def fetch_webpage(url: str, max_length: int = 10000) -> str:
    """抓取公开网页并提取可见文本。"""
    try:
        _validate_public_url(url)
        max_length = max(500, min(int(max_length), 50000))
        headers = {"User-Agent": "AI-Frontier-Explorer/1.0", "Accept": "text/html,text/plain,application/xhtml+xml"}
        with httpx.Client(follow_redirects=False, timeout=30, headers=headers) as client:
            current_url = url
            for _ in range(5):
                response = client.get(current_url)
                if response.is_redirect:
                    target = str(response.next_request.url)
                    _validate_public_url(target)
                    current_url = target
                    continue
                response.raise_for_status()
                break
            else:
                return "抓取失败: 重定向次数过多"
        content_type = response.headers.get("content-type", "").lower()
        if not any(kind in content_type for kind in ("text/html", "text/plain", "application/xhtml+xml")):
            return f"不支持的内容类型: {content_type or '未知'}"
        parser = _ReadableTextParser()
        parser.feed(response.text[:2_000_000])
        content = " ".join(" ".join(parser.parts).split())
        if len(content) > max_length:
            content = content[:max_length] + "\n\n... [内容已截断]"
        return content or "无法提取页面内容"
    except (ValueError, socket.gaierror) as exc:
        return f"URL 校验失败: {exc!s}"
    except httpx.TimeoutException:
        return f"请求超时: {url}"
    except httpx.HTTPStatusError as exc:
        return f"HTTP 错误 ({exc.response.status_code}): {url}"
    except httpx.HTTPError as exc:
        return f"抓取失败: {exc!s}"
