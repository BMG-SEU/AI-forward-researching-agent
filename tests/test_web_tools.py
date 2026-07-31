import pytest

from tools.web_tools import _ReadableTextParser, _validate_public_url


def test_parser_excludes_script_and_style():
    parser = _ReadableTextParser()
    parser.feed("<main>Hello <script>secret()</script><style>x</style> world</main>")
    assert " ".join(parser.parts) == "Hello world"


@pytest.mark.parametrize("url", ["file:///etc/passwd", "http://localhost/a", "http://127.0.0.1/a"])
def test_private_or_invalid_urls_are_blocked(url):
    with pytest.raises(ValueError):
        _validate_public_url(url)
