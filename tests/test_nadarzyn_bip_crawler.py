import types
from unittest.mock import Mock

import pytest
from selectolax.lexbor import LexborHTMLParser

from src.models import ContentItem, RedirectItem


def test_crawler_init_attributes(crawler, base_url, parser1, parser2):
    assert crawler.base_url == base_url
    assert crawler.parsers == [parser1, parser2]
    assert crawler.logger.name == "crawler"


@pytest.mark.parametrize(
    "p1_can,p2_can,p1_items,p2_items,expected_len",
    [
        (True, False, [ContentItem(url="X", main_title="T1", title="S1", description="D")], None, 1),
        (False, True, None, [ContentItem(url="Y", main_title="T2", title="S2")], 1),
        (True, False, [None], None, 0),
    ],
)
def test_crawl_basic_variants(
    crawler, base_url, parser1, parser2, http_client, sleep_calls, p1_can, p2_can, p1_items, p2_items, expected_len
):
    # Response reused
    resp = Mock()
    resp.url = base_url
    resp.text = "<html><body>Test content</body></html>"
    http_client.fetch.return_value = resp

    parser1.can_parse.return_value = p1_can
    parser2.can_parse.return_value = p2_can

    if p1_items is not None:
        # Replace placeholder URLs with actual base_url for consistency
        adjusted = []
        for it in p1_items:
            if isinstance(it, ContentItem):
                it.url = base_url
            adjusted.append(it)
        parser1.parse.return_value = iter(adjusted)

    if p2_items is not None:
        adjusted = []
        for it in p2_items:
            if isinstance(it, ContentItem):
                it.url = base_url
            adjusted.append(it)
        parser2.parse.return_value = iter(adjusted)

    result = crawler.crawl()
    assert len(result) == expected_len
    # Sleep called once per crawled URL
    assert list(sleep_calls) == [1.5] * 1


def test_crawl_redirect_flow(crawler, parser1, parser2, http_client, base_url, sleep_calls):
    redirect_target = f"{base_url}/content/123"
    redirect_resp = Mock(url=base_url, text="<html><body>R</body></html>")
    content_resp = Mock(url=redirect_target, text="<html><body>C</body></html>")
    http_client.fetch.side_effect = [redirect_resp, content_resp]

    redirect_item = RedirectItem(url=redirect_target, main_title="From redirect")
    content_item = ContentItem(url=redirect_target, main_title="Final", title="Sub", description="Body")

    parser1.can_parse.side_effect = [True, True]
    parser1.parse.side_effect = [iter([redirect_item]), iter([content_item])]
    parser2.can_parse.return_value = False

    result = crawler.crawl()
    assert len(result) == 1
    final = result[0]
    assert final.url == redirect_target
    assert final.main_title == "Final"
    assert final.description == "Body"
    assert list(sleep_calls) == [1.5, 1.5]
    assert http_client.fetch.call_count == 2


def test_crawl_url_no_suitable_parser(crawler, parser1, parser2, http_client, base_url):
    resp = Mock(url=base_url, text="<html><body>Unknown</body></html>")
    http_client.fetch.return_value = resp
    parser1.can_parse.return_value = False
    parser2.can_parse.return_value = False
    results = list(crawler.crawl_url(base_url, http_client))
    assert results == []


def test_crawl_url_http_error_propagates(crawler, http_client, base_url):
    http_client.fetch.side_effect = Exception("Network error")
    with pytest.raises(Exception, match="Network error"):
        list(crawler.crawl_url(base_url, http_client))


def test_crawl_url_creates_dom_parser(crawler, parser1, parser2, http_client, base_url):
    resp = Mock(url=base_url, text="<html><body>HTML</body></html>")
    http_client.fetch.return_value = resp
    parser1.can_parse.return_value = True
    parser1.parse.return_value = iter([])
    list(crawler.crawl_url(base_url, http_client))
    (url_arg, dom_arg), _ = parser1.can_parse.call_args
    assert url_arg == base_url
    assert isinstance(dom_arg, LexborHTMLParser)


def test_crawl_url_uses_resolved_url(crawler, parser1, http_client, base_url):
    requested = f"{base_url}/redirect"
    resolved = f"{base_url}/final"
    resp = Mock(url=resolved, text="<html><body>Content</body></html>")
    http_client.fetch.return_value = resp
    parser1.can_parse.return_value = True
    parser1.parse.return_value = iter([])
    list(crawler.crawl_url(requested, http_client))
    (url_arg, _), _ = parser1.can_parse.call_args
    assert url_arg == resolved


def test_crawl_logging_messages(crawler, parser1, http_client, base_url, caplog_info):
    resp = Mock(url=base_url, text="<html><body>C</body></html>")
    http_client.fetch.return_value = resp
    parser1.can_parse.return_value = True
    parser1.parse.return_value = iter([ContentItem(url=base_url, main_title="T", title="S", description="D")])
    crawler.crawl()
    # Ensure key log fragments appear
    msgs = "\n".join(caplog_info.messages)
    assert "Fetching URL" in msgs
    assert "Item parsed" in msgs
    assert "No suitable parser" not in msgs


def test_crawl_url_returns_generator(crawler, http_client, base_url):
    http_client.fetch.return_value = Mock(url=base_url, text="<html><body>X</body></html>")
    gen = crawler.crawl_url(base_url, http_client)
    assert isinstance(gen, types.GeneratorType)


def test_crawl_merge_redirect_fields(crawler, parser1, http_client, base_url, sleep_calls):
    content_url = f"{base_url}/content"
    redirect_resp = Mock(url=base_url, text="<html><body>Red</body></html>")
    content_resp = Mock(url=content_url, text="<html><body>Content</body></html>")
    http_client.fetch.side_effect = [redirect_resp, content_resp]

    redirect_item = RedirectItem(url=content_url, main_title="Redirect Title", description="From redirect")
    # Content missing description -> should inherit
    content_item = ContentItem(url=content_url, main_title="Content Title", title="Content Subtitle")

    parser1.can_parse.side_effect = [True, True]
    parser1.parse.side_effect = [iter([redirect_item]), iter([content_item])]

    result = crawler.crawl()
    assert len(result) == 1
    merged = result[0]
    assert merged.main_title == "Content Title"
    assert merged.description == "From redirect"
    assert list(sleep_calls) == [1.5, 1.5]
